from deploy.clients import proxytest2client

udp = proxytest2client.ProxyTest2UdpClient('bastion.oh.wsh.no', remote_port=9190)
tcp = proxytest2client.ProxyTest2TcpClient('bastion.oh.wsh.no', remote_port=9191)

print('udp: %s' % udp.version())
print('tcp: %s' % tcp.version())
