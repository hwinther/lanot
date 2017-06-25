# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import gc
import webrepl
import network
import machine
import os

webrepl.start()
gc.collect()

wlan = network.WLAN(network.STA_IF)
# turn off ap
ap_if = network.WLAN(network.AP_IF)
if ap_if.active():
    ap_if.active(False)

if not wlan.active():
    wlan.active(True)

if not wlan.isconnected():
    wlan.connect('dgn', 'pingvin9195')
    while not wlan.isconnected():
        machine.idle()
    cfg = wlan.ifconfig()
    print('WLAN connected ip {} gateway {}'.format(cfg[0], cfg[2]))


print(os.uname())
