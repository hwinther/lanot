# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal
#
import network
import machine
from machine import SD
from network import WLAN
import os

#
# Set up WLAN
#
wlan = WLAN()  # get current object, without changing the mode

ssid = 'dgn'
password = 'pingvin9195'
ip = '192.168.1.250'
net_mask = '255.255.255.0'
gateway = '192.168.1.1'
dns = '192.168.1.5'


def init():
    wlan.init(WLAN.STA, antenna=WLAN.EXT_ANT)
    wlan.ifconfig(config=(ip, net_mask, gateway, dns))


def connect():
    wlan.connect(ssid, auth=(WLAN.WPA2, password), timeout=5000)
    while not wlan.isconnected():
        machine.idle()  # save power while waiting
    cfg = wlan.ifconfig()
    print('WLAN connected ip {} gateway {}'.format(cfg[0], cfg[2]))


def setup():
    init()
    if not wlan.isconnected():
        connect()


setup()

#
# Set up server
#
server = network.Server()
server.deinit()
server.init(login=('dgram', 'pingvin'), timeout=600)

#
# SD card support
#
sd = SD()
os.mount(sd, '/sd')
