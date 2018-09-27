from deploy.clients import nodetestclient

# udp = nodetestclient.NodeTestUdpClient('nodetest')
tcp = nodetestclient.NodeTestTcpClient('10.20.2.117')

# print('udp: %s' % udp.version())
print('tcp: %s' % tcp.version())
