import os
import time
import machine
import network
import prometheus
import prometheus.pgc as gc

gc.collect()

# The purpose of this component is to create a singleton like scope for reuse of these wrapper classes

ap_if = None
sta_if = None
if prometheus.is_micro:
    ap_if = network.WLAN(network.AP_IF)
    sta_if = network.WLAN(network.STA_IF)

config_filename = 'sta_if.cfg'

gc.collect()


def init_network():
    ssid, password = load_config()

    if ssid is not None and password is not None:
        sta_mode(ssid, password)
    else:
        ap_mode()


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
    print('STA mode')

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
            print('WLAN connected ip {} gateway {}'.format(cfg[0], cfg[2]))
        else:
            # switch back to AP mode
            ap_mode()


def ap_mode():
    print('AP mode')

    if not ap_if.active():
        ap_if.active(True)
    if sta_if.active():
        sta_if.active(False)
