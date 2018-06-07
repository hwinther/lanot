import socket
import gc
import os
import prometheus
import prometheus.server.socketserver as socketserver
import prometheus.logging as logging

gc.collect()


class TcpSocketServer(socketserver.SocketServer):
    def __init__(self, instance, socketwrapper=None):
        socketserver.SocketServer.__init__(self, instance, socketwrapper)
        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_STREAM)
        self.splitChars = '\n'
        self.endChars = '\r'
        self.sockets = dict()  # type: dict((str,int), socket.socket)
        self.buffers = dict()  # type: dict((str,int), prometheus.Buffer)

    def start(self, bind_host='', bind_port=9195):
        socketserver.SocketServer.start(self, bind_host=bind_host, bind_port=bind_port)

    def pre_loop(self, bind_host='', bind_port=9195, **kwargs):
        socketserver.SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
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
        except socketserver.socket_error as e:
            if prometheus.is_micro:
                if e.args[0] != 11 and e.args[0] != 110 and e.args[0] != 23:
                    logging.error(e)
                    raise
            else:
                if e.errno != 11 and e.errno != 110 and e.errno != 10035:
                    logging.error(e)
                    raise

        if sock is not None:
            logging.success('Accepted connection from %s' % repr(addr))
            sock.settimeout(0)
            # if addr not in buffers.keys():
            logging.notice('Creating new buffer context')
            self.buffers[addr] = prometheus.Buffer(split_chars=self.splitChars, end_chars=self.endChars)
            self.sockets[addr] = sock

        # TODO: would be more efficient by using Poll (which is the micropython way)
        # TODO: do socket cleanup when they go away (cause an exception that isnt timeout, i suppose)
        for addr in self.buffers.keys():
            data = None
            try:
                data = self.sockets[addr].recv(100)
            except socketserver.socket_error as e:
                if prometheus.is_micro:
                    if e.args[0] == 104:
                        logging.notice('disconnected')
                        del self.buffers[addr]
                        del self.sockets[addr]
                        continue
                    if e.args[0] != 11 and e.args[0] != 110 and e.args[0] != 23:
                        logging.error(e)
                        raise
                    # else:
                    #     logging.debug(e)
                else:
                    if e.errno == 104:
                        logging.notice('disconnected')
                        del self.buffers[addr]
                        del self.sockets[addr]
                        continue
                    if e.errno != 11 and e.errno != 104 and e.errno != 110 and e.errno != 10035 and e.errno != 10054:
                        logging.error(e)
                        raise
                    # else:
                    #     logging.debug(e)

            if data == b'':
                logging.notice('disconnected (empty data)')
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
                command = self.buffers[addr].pop()
                if command is None:
                    # logging.notice('Breaking command loop')
                    break

                if command == b'shell':
                    # this is very experimental, and does not seem to work atm - one of the fd's breaks down after
                    #  the initial data burst
                    logging.warn('dupterm %s:0' % repr(addr))
                    del self.buffers[addr]
                    sock = self.sockets[addr]
                    sock.setblocking(False)
                    # notify REPL on socket incoming data
                    sock.setsockopt(socket.SOL_SOCKET, 20, os.dupterm_notify)
                    os.dupterm(sock, 0)
                    # del self.sockets[addr]
                    raise Exception('Dropping to REPL')
                    # self.loop_active = False
                    # break

                logging.notice('Calling handle data')
                self.handle_data(command, self.sockets[addr])

    def post_loop(self, **kwargs):
        socketserver.SocketServer.post_loop(self, **kwargs)

        # attempt a graceful shutdown of all sockets
        for addr in self.sockets.keys():
            self.sockets[addr].close()
        self.socket.close()

    def reply(self, return_value, source=None, **kwargs):
        socketserver.SocketServer.reply(self, return_value, **kwargs)

        if type(return_value) is str:
            return_value = return_value.encode('utf-8')

        logging.notice('returning %s to %s' % (return_value, repr(source)))
        source.send(b'%s%s%s' % (return_value, self.endChars.encode('utf-8'), self.splitChars.encode('utf-8')))
