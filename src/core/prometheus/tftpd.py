import socket
import gc

__version__ = '0.1.3'
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
                if line == b'':
                    # most likely, connection closed
                    break
                data = data + line
                del line
                gc.collect()
            except:
                # TODO: find out what this is and handle it better
                break
        # print(repr(data))
        if data.find(b'\00\01\02\03') != -1:
            name, content = data.split(b'\00\01\02\03', 1)
            if name.find('/') is -1:
                # make it an explicit path in case current working dir is not / (that used to be the assumption)
                name = '/' + name
            print('name: %s len: %d' % (repr(name), len(content)))
            f = open(name, 'w')
            f.write(content)
            f.close()
        if data.find(b'quit') != -1:
            print('tftpd ending listener loop')
            break
        client.close()
        gc.collect()


def tftp_client(host, *filenames):
    for filename in filenames:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting')
        sock.connect((host, 69))
        data = open(filename, 'r').read()
        print('Sending %d bytes from file %s' % (len(data), filename))
        sock.send('%s\00\01\02\03%s' % (filename, data))
        sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting')
    sock.connect((host, 69))
    print('tftpd_client quitting')
    sock.send('quit\r\n')
    sock.close()
