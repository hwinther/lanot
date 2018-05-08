import socket
import gc

__version__ = '0.1.2'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


def tftpd():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 69))
    sock.listen(1)
    while True:
        print('Waiting for connection..')
        client, addr = sock.accept()
        print('Accept: %s' % repr(addr))
        data = b''
        client.settimeout(1)
        while True:
            try:
                line = client.recv(1024)
                # print('repr: %s' % repr(line))
                if line == b'':
                    # print('endline')
                    break
                data = data + line
                # print('read')
                gc.collect()
            except:
                # print('exc')
                break
        # print(repr(data))
        if data.find(b'\00\01\02\03') != -1:
            name, content = data.split(b'\00\01\02\03', 1)
            print('name: %s len: %d' % (repr(name), len(content)))
            f = open(name, 'w')
            f.write(content)
            f.close()
        client.close()
        gc.collect()


def tftp_client(host, filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting')
    sock.connect((host, 69))
    data = open(filename, 'r').read()
    print('Sending %d bytes' % len(data))
    sock.send('%s\00\01\02\03%s' % (filename, data))
    print('done')
