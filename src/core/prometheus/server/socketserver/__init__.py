# coding=utf-8
import socket
import gc
import prometheus
import prometheus.server
import prometheus.logging as logging

gc.collect()


class SocketServer(prometheus.server.Server):
    def __init__(self, instance, socketwrapper=None):
        prometheus.server.Server.__init__(self, instance)

        if socketwrapper is None:
            if prometheus.server.debug:
                logging.notice('using socket.socket default')
            socketwrapper = socket.socket

        if prometheus.server.debug:
            logging.notice('setting socketwrapper')
        self.socketwrapper = socketwrapper
