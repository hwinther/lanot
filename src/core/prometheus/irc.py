import prometheus
import prometheus.logging as logging
import socket
if prometheus.is_micro:
    from ussl import wrap_socket as ssl_wrap_socket
    ssl_SSLEOFError = OSError
else:
    from ssl import wrap_socket as ssl_wrap_socket
    # from ssl import SSLEOFError as ssl_SSLEOFError

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('5.9.191.98', 6697))
ss = ssl_wrap_socket(s)

ss.write('NICK dgramtest\r\n')
ss.write('USER dgramtest 0 * :dgrams test\r\n')
_buffer = prometheus.Buffer(split_chars='\n', end_chars='\r')

while True:
    data = ss.read(100)
    print('recv: %s' % data)
    _buffer.parse(data)
    while True:
        command = _buffer.pop()
        if command is None:
            # logging.notice('Breaking command loop')
            break

        print('command=%s' % command)
        if command.find(b'PING') != -1:
            logging.info('sending pong')
            ss.write(command.replace(b'PING', b'PONG') + '\r\n')
        elif command.find(b'376') != -1:
            ss.write('JOIN #wsh\r\n')
