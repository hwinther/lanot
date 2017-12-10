import prometheus_tftpd

'''
import prometheus_tftpd
prometheus_tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

# prometheus_tftpd.tftp_client('test01', 'boot.py')
prometheus_tftpd.tftp_client('test01', 'main.py')
prometheus_tftpd.tftp_client('test01', 'test01.py')

# prometheus_tftpd.tftp_client('test01', 'cacert.pem')
# prometheus_tftpd.tftp_client('test01', 'cert.pem')
# prometheus_tftpd.tftp_client('test01', 'key.pem')
