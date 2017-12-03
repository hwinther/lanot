import prometheus_tftpd

'''
import prometheus_tftpd
prometheus_tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

# prometheus_tftpd.tftp_client('nodetest', 'boot.py')
prometheus_tftpd.tftp_client('nodetest', 'main.py')
# prometheus_tftpd.tftp_client('nodetest', 'nodetest.py')

# prometheus_tftpd.tftp_client('nodetest', 'cacert.pem')
# prometheus_tftpd.tftp_client('nodetest', 'cert.pem')
# prometheus_tftpd.tftp_client('nodetest', 'key.pem')
