import prometheus.tftpd

'''
import prometheus.tftpd
prometheus.tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

# prometheus.tftpd.tftp_client('rover01.iot.oh.wsh.no', 'boot.py')
prometheus.tftpd.tftp_client('10.20.2.144',
                             # 'rover01.py',
                             'main.py'
                             )
