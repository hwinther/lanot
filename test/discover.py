import socket
import sys

cmd = sys.argv[1] + '\r\n'
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('', 9100))
s.sendto(cmd, ('10.20.1.255', 9190))
s.sendto(cmd, ('10.20.1.255', 9195))
s.sendto(cmd, ('10.20.2.255', 9190))
s.sendto(cmd, ('10.20.2.255', 9195))

while True:
    data, addr = s.recvfrom(1024)
    try:
        dns = socket.gethostbyaddr(addr[0])
    except:
       dns = ('could not resolve', 0)
    print('data: %s host: %s addr: %s' % (repr(data), dns[0], repr(addr)))
