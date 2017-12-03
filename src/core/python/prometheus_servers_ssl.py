import prometheus
import prometheus_logging as logging
import socket
import gc
import sys
import os
if prometheus.is_micro:
    from ussl import wrap_socket as ssl_wrap_socket
    ssl_SSLEOFError = OSError
else:
    from ssl import wrap_socket as ssl_wrap_socket
    from ssl import SSLEOFError as ssl_SSLEOFError

__version__ = '0.1.2'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()
# All the method names that must be delegated to either the real socket
# object or the _closedsocket object.
_delegate_methods = ('recvfrom', 'sendto', 'bind', 'listen', 'settimeout', 'setsockopt')
if not prometheus.is_micro:
    _delegate_methods = _delegate_methods + ('recv_into', 'recvfrom_into')


class SslSocket(object):
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        if _sock is None:
            _sock = socket.socket(family, type, proto)
        self._sock = _sock
        self.sslsock = None
        for method in _delegate_methods:
            setattr(self, method, getattr(_sock, method))

    def accept(self):
        # print('SslSocket accept')
        sock, addr = self._sock.accept()
        sock = SslSocket(_sock=sock)
        sock.wrap()
        return sock, addr

    def wrap(self):
        logging.notice('ssl wrap')
        ciphers = 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:AES128-GCM-SHA256:AES128-SHA256:HIGH:'
        ciphers += '!aNULL:!eNULL:!EXPORT:!DSS:!DES:!RC4:!3DES:!MD5:!PSK'
        keyfile = 'key.pem'
        certfile = 'cert.pem'
        cacertfile = 'cacert.pem'
        try:
            if prometheus.is_micro:
                # note: at present this does not work at all on esp8266 due to stack size limitations
                # ultimately the tls code does not seem mature enough - it might create new attack vectors
                if sys.platform == 'esp32':
                    # mbedtls
                    # esp32 will work, but chrome seems to reject something during handshake
                    cert = open(certfile, 'r').read()
                    key = open(keyfile, 'r').read()
                    self.sslsock = ssl_wrap_socket(self._sock, server_side=True, cert=cert, key=key)
                else:
                    # axtls
                    self.sslsock = ssl_wrap_socket(self._sock, server_side=True)
            else:
                # cpython/openssl
                if not os.path.exists(cacertfile):
                    self.sslsock = ssl_wrap_socket(self._sock, server_side=True, keyfile=keyfile, certfile=certfile,
                                                   ciphers=ciphers)
                else:
                    self.sslsock = ssl_wrap_socket(self._sock, server_side=True, keyfile=keyfile, certfile=certfile,
                                                   ca_certs=cacertfile, ciphers=ciphers)
        except ssl_SSLEOFError:
            logging.warn('SSLEOFError')
        except Exception as e:
            logging.error(e)

    def recv(self, buffersize, flags=None):
        # self._sock.recv(buffersize, flags)
        if self.sslsock is None:
            logging.warn('sslsock is None')
            return None
        return self.sslsock.read(buffersize)

    def close(self):
        if self.sslsock is not None:
            self.sslsock.close()
        if self._sock is not None:
            self._sock.close()

    def send(self, data, flags=None):
        # socket.socket.send(self, data, flags)
        try:
            self.sslsock.write(data)
        except OSError as e:
            logging.error('OSError: %s' % e)
