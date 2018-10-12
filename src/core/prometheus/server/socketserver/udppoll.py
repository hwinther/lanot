# coding=utf-8
import socket
import gc
import prometheus
import prometheus.server.socketserver as socketserver
import prometheus.logging as logging
import prometheus.psocket
import prometheus.pollcompat

gc.collect()

"""
Alternative implementation of socketserver.udp, through a poll compatibility layer that was intended to be optimized
for micropython, and use either cPythons regular poll, or select depending on the platform.
The ultimate goal was to get rid of try-catch SocketError, and perhaps at a later time aggregate the socket polling
in the global scope (when using multiple socket servers simultaneously)
However, the extra method invocations and string data being passed by value (assumptions) made micropython slower.
cPython was marginally faster, but not so much that it really matters.
(TLDR; how to get called out for micro optimizing on freenode)
"""


class UdpPollSocketServer(socketserver.SocketServer):
    def __init__(self, instance, socketwrapper=None):
        socketserver.SocketServer.__init__(self, instance, socketwrapper)
        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_DGRAM)
        self.split_chars = '\n'
        self.end_chars = '\r'
        self.buffers = dict()  # :type dict(Buffer)
        self.poll_compat = prometheus.pollcompat.PollCompat()

    def start(self, bind_host='', bind_port=9195, **kwargs):
        socketserver.SocketServer.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host='', bind_port=9195, **kwargs):
        socketserver.SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except prometheus.psocket.socket_error:
            logging.warn('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.setblocking(0)
        logging.success('listening on %s:%d (udp)' % (bind_host, bind_port))
        self.poll_compat.register(self.socket, prometheus.pollcompat.PollCompat.POLLIN)

    def loop_tick(self, **kwargs):
        socketserver.SocketServer.loop_tick(self, **kwargs)

        # TODO: buffer could be higher, but then the buffer class needs to prune its rest buffer over time
        # should probably bear in mind that the underlying fd buffer on mpy platforms will be limited to around
        #  500 bytes in the first place
        data, addr = None, None
        for pair in self.poll_compat.poll(0):
            if prometheus.pollcompat.PollCompat.POLLIN & pair[1]:
                # its input (what else could it be?:)
                data, addr = self.socket.recvfrom(500)

        if data is None:
            return

        logging.notice('recv %s from %s' % (repr(data), repr(addr)))

        if addr not in self.buffers.keys():
            if prometheus.server.debug:
                logging.debug('Creating new buffer context')
            # TODO: clean up buffer contexts over time!
            # TODO: this must be done in Tcp implementation also
            if len(self.buffers) > 2:
                if prometheus.server.debug:
                    logging.debug('Cleaning up old buffers')
                del self.buffers
                self.buffers = dict()
                gc.collect()
            self.buffers[addr] = prometheus.Buffer(split_chars=self.split_chars, end_chars=self.end_chars)

        if type(data) is str:
            # convert to bytes?
            data = data.decode('ascii')
        self.buffers[addr].parse(data)

        while True:
            command = self.buffers[addr].pop()
            if command is None:
                # logging.notice('Breaking command loop')
                break
            if type(command.packet) is bytes:
                command.packet = command.packet.decode('ascii')
            if prometheus.server.debug:
                logging.debug('Calling handle data')
            self.handle_data(command.packet, addr)

        gc.collect()

        # to reduce cpu/energy usage
        # if prometheus.is_micro:
        #     machine.idle()
        # else:
        #     time.sleep(0.001)

    def post_loop(self, **kwargs):
        socketserver.SocketServer.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None, **kwargs):
        socketserver.SocketServer.reply(self, return_value, **kwargs)

        if type(return_value) is str:
            return_value = return_value.encode('ascii')
        elif type(return_value) is bytes:
            pass
        else:
            return_value = b'%s' % return_value
        logging.notice('Returning %s to %s' % (return_value, repr(source)))
        self.socket.sendto(b'%s%s%s' % (return_value, self.end_chars.encode('ascii'),
                                        self.split_chars.encode('ascii')), source)
        gc.collect()
