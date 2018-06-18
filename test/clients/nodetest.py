from deploy.clients import nodetestclient

udp = nodetestclient.NodeTestUdpClient('nodetest')
tcp = nodetestclient.NodeTestTcpClient('nodetest')

print('udp: %s' % udp.version())
print('tcp: %s' % tcp.version())
