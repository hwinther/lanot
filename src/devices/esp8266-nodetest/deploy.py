import prometheus_tftpd

'''
import prometheus_tftpd
prometheus_tftpd.tftpd()
'''

prometheus_tftpd.tftp_client('nodetest', 'boot.py')
prometheus_tftpd.tftp_client('nodetest', 'main.py')
prometheus_tftpd.tftp_client('nodetest', 'nodetest.py')
