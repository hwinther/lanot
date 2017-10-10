import prometheus_tftpd

'''
prime the device with:

import network
import machine
import prometheus_tftpd
gc.collect()
wlan = network.WLAN(network.STA_IF)
wlan.connect('dgn', 'pingvin9195')
prometheus_tftpd.tftpd()
'''

prometheus_tftpd.tftp_client('192.168.1.122', 'boot.py')
prometheus_tftpd.tftp_client('192.168.1.122', 'main.py')
prometheus_tftpd.tftp_client('192.168.1.122', 'test02.py')
