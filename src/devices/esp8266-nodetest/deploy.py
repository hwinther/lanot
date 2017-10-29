import prometheus_tftpd

'''
import prometheus_tftpd
prometheus_tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

prometheus_tftpd.tftp_client('nodetest.iot.oh.wsh.no', 'boot.py')
prometheus_tftpd.tftp_client('nodetest.iot.oh.wsh.no', 'main.py')
prometheus_tftpd.tftp_client('nodetest.iot.oh.wsh.no', 'nodetest.py')
