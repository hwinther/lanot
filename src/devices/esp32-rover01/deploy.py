import prometheus.tftpd

'''
import prometheus.tftpd
prometheus.tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

# prometheus.tftpd.tftp_client('rover01.iot.oh.wsh.no', 'boot.py')
prometheus.tftpd.tftp_client('rover01.iot.oh.wsh.no', 'main.py')
prometheus.tftpd.tftp_client('rover01.iot.oh.wsh.no', 'rover01.py')

# prometheus.tftpd.tftp_client('test01', 'cacert.pem')
# prometheus.tftpd.tftp_client('test01', 'cert.pem')
# prometheus.tftpd.tftp_client('test01', 'key.pem')
