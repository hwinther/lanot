import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('', 9100))
cmd = 'uname\r\n'
s.sendto(cmd, ('10.20.1.255', 9190))
s.sendto(cmd, ('10.20.2.255', 9190))
s.sendto(cmd, ('10.20.2.255', 9195))

while True:
    data, addr = s.recvfrom(1024)
    print(repr(data), repr(addr))
