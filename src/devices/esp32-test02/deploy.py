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

prometheus.tftpd.tftp_client('10.20.2.116', 'boot.py')
prometheus.tftpd.tftp_client('10.20.2.116', 'main.py')
prometheus.tftpd.tftp_client('10.20.2.116', 'test02.py')
