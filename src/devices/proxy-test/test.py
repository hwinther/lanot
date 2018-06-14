import machine
import gc
import sys
import time
import network
import binascii

gc.collect()

# TODO: i've turned off devices all over the place, its somewhat redundant and messy, and right now related to testing
ap_if = network.WLAN(network.AP_IF)
if ap_if.active():
    ap_if.active(False)
if not ap_if.config('essid').startswith('Prometheus'):
    essid = b"Prometheus-%s" % binascii.hexlify(ap_if.config("mac")[-3:])
    # if essid.decode('ansi') is not ap_if.config('essid'):
    ap_if.config(essid=essid, authmode=network.AUTH_WPA_WPA2_PSK, password=b"forethought")
    # except Exception as e:
    #     print('Failed to set ap_if config: %s' % str(e))
sta_if = network.WLAN(network.STA_IF)
if sta_if.active():
    sta_if.active(False)


def connect(network_info):
    if network_info.find(':') is -1:
        return 'Missing : between ssid and password'

    ssid, password = network_info.split(':', 1)
    print('Connecting to %s' % ssid)
    gc.collect()

    if sys.platform == 'esp8266':
        # HACK: esp8266 seems to crash if both AP and STA are active at once
        # this might come down to implementation differences, maybe you should use one of them to do both tasks?
        print('turning off ap')
        ap_if.active(False)
        machine.idle()

    if not sta_if.active():
        sta_if.active(True)

    print('!! 1')
    if not sta_if.isconnected():
        print('ssid: %s' % repr(ssid))
        print('password: %s' % repr(password))
        sta_if.connect(ssid, password)

        # time_start = time.time()
        print('!! 2')
        i = 0
        while not sta_if.isconnected():
            # and not (time.time() - time_start) >= 10:
            # machine.idle()
            i += 1
            pass
        print(i)

    print('!! 3')
    if sta_if.isconnected():
        print('Connected successfully')
        # save config and disable ap
        # save_config(ssid, password)
        gc.collect()
        sta_mode(ssid, password)
        # TODO: return does not seem to work, could be hardware/toolchain related?
        # (i.e. which dev do we send this from)
        # return 'Connected successfully'
    else:
        print('Connection timed out')
        if sys.platform == 'esp8266':
            # followup of previous hack, turning it back on
            print('turning ap back on')
            ap_if.active(True)
        # return 'Connection timed out'

    gc.collect()


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
