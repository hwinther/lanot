import prometheus_tftpd

'''
prime the device with:

import network
import machine
import prometheus_tftpd
gc.collect()
wlan = network.WLAN(network.STA_IF)
wlan.connect('dgn.iot', 'umbFUTyJSvqhxNrQ')
prometheus_tftpd.tftpd()
'''

prometheus_tftpd.tftp_client('10.20.2.116', 'boot.py')
prometheus_tftpd.tftp_client('10.20.2.116', 'main.py')
prometheus_tftpd.tftp_client('10.20.2.116', 'test02.py')
