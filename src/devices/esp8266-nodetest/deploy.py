import prometheus.tftpd

'''
import prometheus.tftpd
prometheus.tftpd.tftpd()

to run:
set PYTHONPATH=p:\lanot\src\core\python
'''

# prometheus.tftpd.tftp_client('nodetest', 'boot.py')
prometheus.tftpd.tftp_client('nodetest', 'main.py')
prometheus.tftpd.tftp_client('nodetest', 'nodetest.py')

# prometheus.tftpd.tftp_client('nodetest', 'cacert.pem')
# prometheus.tftpd.tftp_client('nodetest', 'cert.pem')
# prometheus.tftpd.tftp_client('nodetest', 'key.pem')
