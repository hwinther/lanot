import os
import time
import machine
import network
import binascii
import prometheus
import prometheus.pgc as gc
import prometheus.server.socketserver.udp
import prometheus.logging as logging

__version__ = '0.1.4'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()

# The purpose of this component is to create a singleton like scope for reuse of these wrapper classes

ap_if = None
sta_if = None
if prometheus.is_micro:
    ap_if = network.WLAN(network.AP_IF)
    if not ap_if.config('essid').startswith('Prometheus'):
        essid = b"Prometheus-%s" % binascii.hexlify(ap_if.config("mac")[-3:])
        # if essid.decode('ansi') is not ap_if.config('essid'):
        ap_if.config(essid=essid, authmode=network.AUTH_WPA_WPA2_PSK, password=b"forethought")
        # except Exception as e:
        #     print('Failed to set ap_if config: %s' % str(e))
    sta_if = network.WLAN(network.STA_IF)

config_filename = 'sta_if.cfg'

gc.collect()


def run_local():
    # the following will start up a default config udp server to receive configuration instructions

    # dont run if main.py exists
    if 'main.py' in os.listdir('/'):
        return

    # temporarily disabled
    return

    logging.info('Starting default server')
    node = prometheus.Prometheus()
    udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
    # enable configuration commands if necessary
    if not prometheus.server.config_enabled:
        prometheus.server.config_enabled = True

    logging.boot(udpserver)
    try:
        udpserver.start()
    except Exception as e:
        logging.warn('Default udpserver exception: %s' % str(e))

    del udpserver
    del node
    gc.collect()
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
        while not sta_if.isconnected() and not (time.time() - time_start) >= 30:
            machine.idle()

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
