# coding=utf-8
import socket as socket_original
from socket import *

"""
Compatibility wrapper for usocket
"""


class socket(socket_original.socket):
    def readinto(self, buf, nbytes=None):
        return socket_original.socket.recv_into(self, buf, nbytes)
