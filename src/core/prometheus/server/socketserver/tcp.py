# coding=utf-8
import socket
import gc
import uos
import prometheus
import prometheus.server.socketserver as socketserver
import prometheus.logging as logging
import prometheus.psocket

gc.collect()
shell_enabled = True


class TcpSocketServer(socketserver.SocketServer):
    def __init__(self, instance, socketwrapper=None):
        socketserver.SocketServer.__init__(self, instance, socketwrapper)
        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_STREAM)
        self.split_chars = '\n'
        self.end_chars = '\r'
        self.sockets = dict()
        self.buffers = dict()

    def start(self, bind_host='', bind_port=9195):
        socketserver.SocketServer.start(self, bind_host=bind_host, bind_port=bind_port)

    def pre_loop(self, bind_host='', bind_port=9195, **kwargs):
        socketserver.SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except prometheus.psocket.socket_error:
            logging.warn('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(1)
        self.socket.settimeout(0)
        logging.success('listening on %s:%d (tcp)' % (bind_host, bind_port))

    def loop_tick(self, **kwargs):
        socketserver.SocketServer.loop_tick(self, **kwargs)

        sock, addr = None, None
        try:
            # TODO: put this pair in a wrapper class
            sock, addr = self.socket.accept()
        except prometheus.psocket.socket_error as exception:
            if prometheus.is_micro:
                if exception.args[0] != 11 and exception.args[0] != 110 and exception.args[0] != 23:
                    logging.error(exception)
                    raise
            else:
                if exception.errno != 11 and exception.errno != 110 and exception.errno != 10035:
                    logging.error(exception)
                    raise

        if sock is not None:
            logging.success('Accepted connection from %s' % repr(addr))
            sock.settimeout(0)
            # if addr not in buffers.keys():
            if prometheus.server.debug:
                logging.debug('Creating new buffer context')
            self.buffers[addr] = prometheus.Buffer(split_chars=self.split_chars, end_chars=self.end_chars)
            self.sockets[addr] = sock

        # TODO: would be more efficient by using Poll (which is the micropython way)
        # TODO: do socket cleanup when they go away (cause an exception that isnt timeout, i suppose)
        for addr in self.buffers.keys():
            data = None
            try:
                data = self.sockets[addr].recv(100)
            except prometheus.psocket.socket_error as exception:
                if prometheus.is_micro:
                    # 104 connect reset by peer, 113 no route to host, might want to make this 100-113
                    if exception.args[0] == 104 or exception.args[0] == 113:
                        if prometheus.server.debug:
                            logging.debug('disconnected')
                        del self.buffers[addr]
                        del self.sockets[addr]
                        continue
                    if exception.args[0] != 11 and exception.args[0] != 110 and exception.args[0] != 23:
                        logging.error(exception)
                        raise
                    # else:
                    #     logging.debug(e)
                else:
                    if exception.errno == 104:
                        if prometheus.server.debug:
                            logging.debug('disconnected')
                        del self.buffers[addr]
                        del self.sockets[addr]
                        continue
                    if exception.errno != 11 and exception.errno != 104 and exception.errno != 110 and \
                       exception.errno != 10035 and exception.errno != 10054:
                        logging.error(exception)
                        raise
                    # else:
                    #     logging.debug(e)

            if data == b'':
                if prometheus.server.debug:
                    logging.debug('disconnected (empty data)')
                del self.buffers[addr]
                del self.sockets[addr]
                continue

            if data is None:
                continue

            logging.notice('Got data from %s' % repr(addr))
            try:
                data = data.decode('utf-8')
            except UnicodeError:
                data = None

            if data is not None:
                self.buffers[addr].parse(data)

            while True:
                command = self.buffers[addr].pop()  # type: prometheus.BufferPacket
                if command is None:
                    # logging.notice('Breaking command loop')
                    break

                if shell_enabled and command.packet == b'shell':
                    if not prometheus.is_micro:
                        self.reply('Not implemented for this platform', source=self.sockets[addr], **kwargs)
                        break

                    logging.warn('dupterm %s:0' % repr(addr))
                    del self.buffers[addr]
                    sock = self.sockets[addr]
                    sock.setblocking(False)
                    # notify REPL on socket incoming data
                    sock.setsockopt(socket.SOL_SOCKET, 20, uos.dupterm_notify)
                    uos.dupterm(sock, 0)
                    raise Exception('Dropping to REPL')
                elif command.packet == b'quit':
                    # TODO: this is somewhat a duplicate of quit from super
                    self.sockets[addr].close()
                    del self.buffers[addr]
                    del self.sockets[addr]
                    break

                if prometheus.server.debug:
                    logging.debug('Calling handle data')

                self.handle_data(command.packet, self.sockets[addr], context=prometheus.parse_args(command.args))

    def post_loop(self, **kwargs):
        socketserver.SocketServer.post_loop(self, **kwargs)

        # attempt a graceful shutdown of all sockets
        for addr in self.sockets.keys():
            self.sockets[addr].close()
        self.socket.close()

    def reply(self, return_value, source=None, **kwargs):
        socketserver.SocketServer.reply(self, return_value, **kwargs)

        # TODO: encode/decode consistency, its a mixture of ascii and utf-8 at the moment
        if type(return_value) is str:
            return_value = return_value.encode('utf-8')
        elif type(return_value) is bytes:
            pass
        else:
            # convert to string first, then bytes
            return_value = b'%s' % str(return_value).encode('utf-8')

        logging.notice('Returning %s to %s' % (return_value, repr(source)))
        source.send(b'%s%s%s' % (return_value, self.end_chars.encode('utf-8'), self.split_chars.encode('utf-8')))
