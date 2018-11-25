# coding=utf-8
import usocket
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
                logging.notice('using usocket.socket default')
            socketwrapper = usocket.socket

        if prometheus.server.debug:
            logging.notice('setting socketwrapper')
        self.socketwrapper = socketwrapper
