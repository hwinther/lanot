# coding=utf-8
import prometheus
import socket as socket_original
from socket import *

"""
Compatibility wrapper for usocket

Delegation borrowed from sslsocket.py
"""

# All the method names that must be delegated to either the real socket
# object or the _closedsocket object.
_delegate_methods = ('recvfrom', 'sendto', 'bind', 'listen', 'settimeout', 'setsockopt', 'recv', 'close', 'send')
if not prometheus.is_micro:
    _delegate_methods += 'recv_into', 'recvfrom_into'


class socket(socket_original.socket):
    def __init__(self, family=socket_original.AF_INET, _type=socket_original.SOCK_STREAM, proto=0, _sock=None):
        if _sock is None:
            _sock = socket_original.socket(family, _type, proto)
        self._sock = _sock
        self.sslsock = None
        for method in _delegate_methods:
            setattr(self, method, getattr(_sock, method))

    def readinto(self, buf, nbytes=0):
        return self.recv_into(buf, nbytes)

    def accept(self):
        # print('wrapped accept used')
        sock, addr = self._sock.accept()
        return socket(_sock=sock), addr
