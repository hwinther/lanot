from deploy.clients import localtestclient

udp = localtestclient.LocalTestUdpClient('localhost', remote_port=9190)
tcp = localtestclient.LocalTestTcpClient('localhost', remote_port=9191)

print('udp: %s' % udp.version())
print('tcp: %s' % tcp.version())
