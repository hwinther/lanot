import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('', 9191))
s.sendto('V\r\n', ('192.168.1.255', 9195))

while True:
    data, addr = s.recvfrom(1024)
    print(repr(data), repr(addr))
