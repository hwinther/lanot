from deploy.clients import nodetestclient

udp = nodetestclient.NodeTestUdpClient('nodetest', remote_port=9190)
tcp = nodetestclient.NodeTestTcpClient('nodetest', remote_port=9191)

print('udp: %s' % udp.version())
print('tcp: %s' % tcp.version())
