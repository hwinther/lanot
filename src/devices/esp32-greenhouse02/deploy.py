import prometheus.tftpd

'''
import prometheus.tftpd
prometheus.tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

# prometheus.tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'boot.py')
prometheus.tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'main.py')
prometheus.tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'greenhouse02.py')

# prometheus.tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'cacert.pem')
# prometheus.tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'cert.pem')
# prometheus.tftpd.tftp_client('greenhouse02.iot.oh.wsh.no', 'key.pem')
