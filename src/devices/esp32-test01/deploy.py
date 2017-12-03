import prometheus_tftpd

'''
import prometheus_tftpd
prometheus_tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

# prometheus_tftpd.tftp_client('10.20.2.115', 'boot.py')
prometheus_tftpd.tftp_client('10.20.2.115', 'main.py')
prometheus_tftpd.tftp_client('10.20.2.115', 'test01.py')

# prometheus_tftpd.tftp_client('10.20.2.115', 'cacert.pem')
# prometheus_tftpd.tftp_client('10.20.2.115', 'cert.pem')
# prometheus_tftpd.tftp_client('10.20.2.115', 'key.pem')
