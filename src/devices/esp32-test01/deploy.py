import prometheus.tftpd

'''
import prometheus.tftpd
prometheus.tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

files = [
    # 'boot.py',
    'main.py',
    'test01.py',
    # 'rover01client.py',
    # 'cacert.pem',
    # 'cert.pem',
    # 'key.pem'
]
prometheus.tftpd.tftp_client('test01.iot.oh.wsh.no', *files)
