import prometheus.tftpd

'''
prime the device with:
nc64 -c 192.168.4.1 9195
connect ssid:password

to run:
set PYTHONPATH=p:\lanot\src\core
'''

files = [
    'main.py',
    'test01.py',
    # 'rover01client.py',
]
prometheus.tftpd.tftp_client('test01.iot.oh.wsh.no', *files)
