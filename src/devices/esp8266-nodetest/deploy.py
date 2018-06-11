import prometheus.tftpd

'''
import prometheus.tftpd
prometheus.tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

files = [
    'boot.py',
    'main.py',
    'nodetest.py',
    # 'cacert.pem',
    # 'cert.pem',
    # 'key.pem'
]
prometheus.tftpd.tftp_client('nodetest.iot.oh.wsh.no', *files)
