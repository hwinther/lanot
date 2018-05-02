import socket
import gc
import servers
import prometheus
import prometheus_logging as logging

gc.collect()

if prometheus.is_micro:
    socket_error = Exception
else:
    socket_error = socket.error
# 11 EAGAIN (try again later)
# 110 Connection timed out
# 23 cant read data?
# 10035 WSAEWOULDBLOCK (A non-blocking socket operation could not be completed immediately)


class SocketServer(servers.Server):
    def __init__(self, instance, socketwrapper=None):
        servers.Server.__init__(self, instance)

        if socketwrapper is None:
            if servers.debug:
                logging.notice('using socket.socket default')
            socketwrapper = socket.socket

        if servers.debug:
            logging.notice('setting socketwrapper')
        self.socketwrapper = socketwrapper
