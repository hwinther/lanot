# coding=utf-8
import socket
import gc
import time
import prometheus.psocket
import prometheus.logging as logging

__version__ = '0.1.5'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


def tftpd(timeout=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 69))
    sock.listen(1)
    # TODO: do away with timeout, but for now this is an acceptable compromise
    sock.settimeout(0.1)
    start_time = time.time()

    while True:
        if timeout is not None:
            diff = time.time() - start_time
            if diff >= timeout:
                break

        try:
            client, addr = sock.accept()
        except prometheus.psocket.socket_error:
            continue

        logging.notice('Accept: %s' % repr(addr))
        data = b''
        # TODO: never use settimeout in micro code
        client.settimeout(0.2)
        while True:
            try:
                line = client.recv(1024)
                if line == b'':
                    # most likely, connection closed
                    break
                data += line
                del line
                gc.collect()
            except prometheus.psocket.socket_error:
                # TODO: find out what this is and handle it better
                break
        # logging.debug(repr(data))
        if data.find(b'\00\01\02\03') != -1:
            name, content = data.split(b'\00\01\02\03', 1)
            if name.find(b'/') == -1:
                # make it an explicit path in case current working dir is not / (that used to be the assumption)
                name = b'/' + name
            logging.info('Writing to file: %s len: %d' % (repr(name), len(content)))
            f = open(name, 'w')
            f.write(content)
            f.close()
        if data.find(b'quit') != -1:
            logging.notice('tftpd ending listener loop')
            break
        client.close()
        del client
        gc.collect()

    sock.close()
    del sock
    gc.collect()


def tftp_client(host, *filenames):
    for filename in filenames:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.notice('Connecting')
        sock.connect((host, 69))
        data = open(filename, 'r').read()
        logging.info('Sending %d bytes from file %s' % (len(data), filename))
        sock.send('%s\00\01\02\03%s' % (filename, data))
        sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.notice('Connecting')
    sock.connect((host, 69))
    logging.info('tftpd_client quitting')
    sock.send('quit\r\n')
    sock.close()
