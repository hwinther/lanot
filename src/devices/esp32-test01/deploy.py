import prometheus.tftpd

'''
import prometheus.tftpd
prometheus.tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

# prometheus.tftpd.tftp_client('test01', 'boot.py')
prometheus.tftpd.tftp_client('test01', 'main.py')
# prometheus.tftpd.tftp_client('test01', 'test01.py')
prometheus.tftpd.tftp_client('test01', 'rover01client.py')

# prometheus.tftpd.tftp_client('test01', 'cacert.pem')
# prometheus.tftpd.tftp_client('test01', 'cert.pem')
# prometheus.tftpd.tftp_client('test01', 'key.pem')
