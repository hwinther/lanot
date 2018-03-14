import time
from deploy.clients import rover01client

udp = rover01client.Rover01UdpClient('rover01.iot.oh.wsh.no', remote_port=9190)
# tcp = rover01client.Rover01TcpClient('rover01.iot.oh.wsh.no', remote_port=9191)

print('udp: %s' % udp.version())
# print('tcp: %s' % tcp.version())

# P:\lanot\test\clients>set PYTHONPATH=p:\lanot\src\core\python;p:\lanot;p:\lanot\tools\micropython-mockup
# P:\lanot\test\clients>python rover01.py

import msvcrt
while True:
    input_char = msvcrt.getch()
    udp.send(b'%s' % input_char)
    time.sleep(0.4)
