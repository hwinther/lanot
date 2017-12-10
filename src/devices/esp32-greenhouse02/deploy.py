import prometheus_tftpd

'''
import prometheus_tftpd
prometheus_tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

prometheus_tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'boot.py')
prometheus_tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'main.py')
prometheus_tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'greenhouse02.py')

# prometheus_tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'cacert.pem')
# prometheus_tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'cert.pem')
# prometheus_tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'key.pem')
