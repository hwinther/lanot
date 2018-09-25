# coding=utf-8
import os
import sys
import time
import machine
import network
import binascii
import prometheus
import prometheus.pgc as gc
import prometheus.server.multiserver
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.tcp
import prometheus.logging as logging

__version__ = '0.1.5b'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()

# The purpose of this component is to create a singleton like scope for reuse of these wrapper classes

ap_if = None
sta_if = None
if prometheus.is_micro:
    ap_if = network.WLAN(network.AP_IF)
    if not ap_if.config('essid').startswith('Prometheus'):
        essid = b'Prometheus-%s' % binascii.hexlify(ap_if.config('mac')[-3:])
        ap_if.config(essid=essid, authmode=network.AUTH_WPA_WPA2_PSK, password=b'forethought')
    sta_if = network.WLAN(network.STA_IF)

config_filename = 'sta_if.cfg'
is_esp8266 = sys.platform == 'esp8266'
debug = False

gc.collect()


def run_local():
    # the following will start up a default config udp server to receive configuration instructions

    # dont run if main.py exists
    if 'main.py' in os.listdir('/'):
        return

    logging.info('Starting default server')

    node = prometheus.Prometheus()
    multiserver = prometheus.server.multiserver.MultiServer()

    udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
    multiserver.add(udpserver)
    gc.collect()

    tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
    multiserver.add(tcpserver)
    gc.collect()

    # enable configuration commands if necessary
    if not prometheus.server.config_enabled:
        prometheus.server.config_enabled = True

    logging.boot(udpserver)

    try:
        multiserver.start()
    except KeyboardInterrupt:
        logging.info('Shutting down default server')
    except Exception as e:
        logging.warn('Default server exception: %s' % str(e))

    del tcpserver
    del udpserver
    del multiserver
    del node
    gc.collect()
    if debug:
        logging.info('Cleaned up default server')


def init_network():
    ssid, password = load_config()

    if ssid is not None and password is not None:
        sta_mode(ssid, password)
        run_local()
    else:
        ap_mode()
        run_local()


def save_config(ssid, password):
    fd = open('/'+config_filename, 'w')
    fd.write('%s:%s' % (ssid, password))
    fd.close()


def load_config():
    ssid, password = None, None

    # look for stored credentials
    if config_filename in os.listdir('/'):
        config = open('/' + config_filename, 'r').read()
        if config.find(':') is not -1:
            ssid, password = config.split(':', 1)

    return ssid, password


def sta_mode(ssid, password):
    logging.info('STA mode')

    if ap_if.active():
        ap_if.active(False)
    if not sta_if.active():
        sta_if.active(True)

    if not sta_if.isconnected():
        sta_if.connect(ssid, password)
        time_start = time.time()
        i = 0
        while not sta_if.isconnected() and not (time.time() - time_start) >= 30:
            # esp8266 crashes when machine.idle is used in this context, thus the incrementing
            if is_esp8266:
                i += 1
            else:
                machine.idle()

        if is_esp8266 and debug:
            print('esp8266 - spent %d iterations' % i)

        if sta_if.isconnected():
            cfg = sta_if.ifconfig()
            logging.notice('WLAN connected ip {} gateway {}'.format(cfg[0], cfg[2]))
        else:
            # switch back to AP mode
            ap_mode()


def ap_mode():
    logging.info('AP mode')

    if not ap_if.active():
        ap_if.active(True)
    if sta_if.active():
        sta_if.active(False)

    cfg = ap_if.ifconfig()
    logging.notice('WLAN AP active - %s (IP %s)' % (ap_if.config('essid'), cfg[0]))


def connect(network_info):
    if network_info.find(':') is -1:
        return 'Missing : between ssid and password'

    if not prometheus.is_micro:
        return 'Not implemented for this platform'

    ssid, password = network_info.split(':', 1)
    logging.notice('Connecting to %s' % ssid)
    gc.collect()

    # if is_esp8266:
    #     # HACK: esp8266 seems to crash if both AP and STA are active at once
    #     # this might come down to implementation differences, maybe you should use one of them to do both tasks?
    #     print('turning off ap')
    #     ap_if.active(False)
    #     machine.idle()

    if not sta_if.active():
        sta_if.active(True)

    if not sta_if.isconnected():
        if debug:
            print('ssid: %s' % repr(ssid))
            print('password: %s' % repr(password))
        sta_if.connect(ssid, password)

        time_start = time.time()
        i = 0
        while not sta_if.isconnected() and not (time.time() - time_start) >= 30:
            # esp8266 crashes when machine.idle is used in this context, thus the incrementing
            if is_esp8266:
                i += 1
            else:
                machine.idle()

        if is_esp8266 and debug:
            print('esp8266 - spent %d iterations' % i)

    if sta_if.isconnected():
        logging.notice('Connected successfully')
        # save config and disable ap
        save_config(ssid, password)
        gc.collect()
        sta_mode(ssid, password)
        # TODO: return does not seem to work, could be hardware/toolchain related?
        # (i.e. which dev do we send this from)
        # return 'Connected successfully'
    else:
        logging.notice('Connection timed out')
        # if is_esp8266:
        #     # followup of previous hack, turning it back on
        #     print('turning ap back on')
        #     ap_if.active(True)
        # return 'Connection timed out'

    gc.collect()
