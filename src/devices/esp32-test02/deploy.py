import prometheus.tftpd

'''
prime the device with:

import network
import machine
gc.collect()
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('dgn.iot', 'umbFUTyJSvqhxNrQ')
import prometheus.tftpd
prometheus.tftpd.tftpd()
'''

files = [
    'boot.py',
    'main.py',
    'test02.py'
]
prometheus.tftpd.tftp_client('10.20.2.116', *files)
