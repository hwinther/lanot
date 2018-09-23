import prometheus.tftpd

'''
prime the device with:
nc64 -c 192.168.4.1 9195
connect ssid:password

to run:
set PYTHONPATH=p:\lanot\src\core
'''

files = [
    'main.py'
]
prometheus.tftpd.tftp_client('10.20.2.117', *files)  # 133/134
