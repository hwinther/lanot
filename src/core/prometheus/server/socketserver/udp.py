# coding=utf-8
import socket
import gc
import prometheus
import prometheus.server.socketserver as socketserver
import prometheus.logging as logging
import prometheus.psocket

gc.collect()


class UdpSocketServer(socketserver.SocketServer):
    def __init__(self, instance, socketwrapper=None):
        socketserver.SocketServer.__init__(self, instance, socketwrapper)
        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_DGRAM)
        self.split_chars = '\n'
        self.end_chars = '\r'
        self.buffers = dict()  # :type dict(Buffer)

    def start(self, bind_host='', bind_port=9195, **kwargs):
        socketserver.SocketServer.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host='', bind_port=9195, **kwargs):
        socketserver.SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except prometheus.psocket.socket_error:
            logging.warn('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.settimeout(0)
        logging.success('listening on %s:%d (udp)' % (bind_host, bind_port))

    def loop_tick(self, **kwargs):
        socketserver.SocketServer.loop_tick(self, **kwargs)

        data, addr = None, None
        try:
            # TODO: buffer could be higher, but then the buffer class needs to prune its rest buffer over time
            # should probably bear in mind that the underlying fd buffer on mpy platforms will be limited to around
            #  500 bytes in the first place
            data, addr = self.socket.recvfrom(500)
        except prometheus.psocket.socket_error as e:
            if prometheus.is_micro:
                if e.args[0] != 11 and e.args[0] != 110 and e.args[0] != 23:
                    logging.error(e)
                    raise
            else:
                if e.errno != 11 and e.errno != 110 and e.errno != 10035:
                    logging.error(e)
                    raise

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
            # if isinstance(command.packet, bytes):
            #     command.packet = command.packet.decode('ascii')
            if prometheus.server.debug:
                logging.debug('Calling handle data')
            self.handle_data(command.packet, addr, context=prometheus.parse_args(command.args))

        gc.collect()

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
