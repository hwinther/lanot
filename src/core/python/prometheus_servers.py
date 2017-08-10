import socket
import gc
import json
from prometheus import Buffer, RegisteredMethod

__version__ = '0.1'
__author__ = 'Hans Christian Winther-Sorensen'


gc.collect()


class Server(object):
    # :type data_commands: dict
    def __init__(self, instance):
        """
        :type instance: Prometheus
        :param instance: Instance of Prometheus
        """
        self.instance = instance
        self.loopActive = False

    def start(self, **kwargs):
        self.pre_loop(**kwargs)
        self.loopActive = True
        while self.loopActive:
            self.loop_tick(**kwargs)
        self.post_loop(**kwargs)

    def pre_loop(self, **kwargs):
        self.instance.recursive_remap()

    def loop_tick(self, **kwargs):
        pass

    def post_loop(self, **kwargs):
        pass

    def reply(self, return_value, source=None):
        pass

    def handle_data(self, command, source=None):
        if command == '':
            return

        print('input:', command)

        if command in self.instance.cached_remap:
            registered_method = self.instance.cached_remap[command]  # type: RegisteredMethod
            return_value = registered_method.method_reference()
            if registered_method.return_type == 'str':
                self.reply(return_value, source)
        elif command == 'die':
            print('die command received')
            self.loopActive = False
            return
        else:
            print('invalid cmd', command)


class UdpSocketServer(Server):
    def __init__(self, instance):
        Server.__init__(self, instance)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.splitChars = '\n'
        self.endChars = '\r'
        self.buffers = dict()  # :type list(Buffer)

    def start(self, bind_host='', bind_port=9195, **kwargs):
        Server.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host, bind_port, **kwargs):
        Server.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            print('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.settimeout(0)
        print('listening on %s:%d' % (bind_host, bind_port))

    def loop_tick(self, **kwargs):
        Server.loop_tick(self, **kwargs)

        data, addr = None, None
        try:
            data, addr = self.socket.recvfrom(1024)
        except:
            pass

        if data is None:
            return

        print('recv %s from %s' % (repr(data), repr(addr)))

        if addr not in self.buffers.keys():
            print('Creating new buffer context')
            self.buffers[addr] = Buffer(split_chars=self.splitChars, end_chars=self.endChars)

        self.buffers[addr].parse(data.decode('utf-8'))

        while True:
            command = self.buffers[addr].pop()
            if command is None:
                # print('Breaking command loop')
                break
            print('Calling handle data')
            self.handle_data(command, addr)

    def post_loop(self, **kwargs):
        Server.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None):
        Server.reply(self, return_value)

        print('returning %s to %s' % (return_value, repr(source)))
        self.socket.sendto(b'%s%s%s' % (return_value, self.endChars, self.splitChars), source)


class TcpSocketServer(Server):
    def __init__(self, instance):
        Server.__init__(self, instance)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.splitChars = '\n'
        self.endChars = '\r'
        self.sockets = dict()  # type: dict((str,int), socket.socket)
        self.buffers = dict()  # type: dict((str,int), Buffer)

    def start(self, bind_host='', bind_port=9195):
        Server.start(self, bind_host=bind_host, bind_port=bind_port)

    def pre_loop(self, bind_host='', bind_port=9195, **kwargs):
        Server.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            print('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(1)
        self.socket.settimeout(0)
        print('listening on %s:%d' % (bind_host, bind_port))

    def loop_tick(self, **kwargs):
        Server.loop_tick(self, **kwargs)

        sock, addr = None, None
        try:
            # TODO: put this pair in a wrapper class
            sock, addr = self.socket.accept()
        except:
            pass  # timeout, i hope

        if sock is not None:
            print('Accepted connection from %s' % repr(addr))
            sock.settimeout(0)
            # if addr not in buffers.keys():
            print('Creating new buffer context')
            self.buffers[addr] = Buffer(split_chars=self.splitChars, end_chars=self.endChars)
            self.sockets[addr] = sock

        # TODO: would be more efficient by using Poll (which is the micropython way)
        # TODO: do socket cleanup when they go away (cause an exception that isnt timeout, i suppose)
        for addr in self.buffers.keys():
            data = None
            try:
                data = self.sockets[addr].recv(1024)
            except:
                pass

            if data is not None:
                print('Got data from %s' % repr(addr))
                self.buffers[addr].parse(data.decode('utf-8'))

                while True:
                    command = self.buffers[addr].pop()
                    if command is None:
                        print('Breaking command loop')
                        break
                    print('Calling handle data')
                    self.handle_data(command, self.sockets[addr])

    def post_loop(self, **kwargs):
        Server.post_loop(self, **kwargs)

        # attempt a graceful shutdown of all sockets
        for addr in self.sockets.keys():
            try:
                self.sockets[addr].close()
            except:
                pass
        self.socket.close()

    def reply(self, return_value, source=None):
        Server.reply(self, return_value)

        print('returning %s to %s' % (return_value, repr(source)))
        source.send(b'%s%s%s' % (return_value, self.endChars, self.splitChars))


class JsonRestServer(Server):
    def __init__(self, instance):
        Server.__init__(self, instance)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, bind_host='', bind_port=8080, **kwargs):
        Server.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host, bind_port, **kwargs):
        Server.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            print('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(1)
        self.socket.settimeout(0)
        print('listening on %s:%d' % (bind_host, bind_port))

        self.instance.update_urls()
        for key in self.instance.cached_urls.keys():
            print('url: %s' % key)

    def loop_tick(self, **kwargs):
        Server.loop_tick(self, **kwargs)

        sock, addr = None, None
        try:
            # TODO: put this pair in a wrapper class
            sock, addr = self.socket.accept()
        except:
            pass  # timeout, i hope

        if sock is not None:
            print('Accepted connection from %s' % repr(addr))
            sock.settimeout(2)
            try:
                data = sock.recv(1024)
            except:
                data = None
            found = False
            if data is not None and data.find(b'\r\n') != -1:
                for line in data.split(b'\r\n'):
                    if len(line) == 0:
                        continue
                    if line.find(b'GET /') != -1:
                        get = line.split(b' ')[1]
                        print('get: %s' % get)
                        if get in self.instance.cached_urls.keys():
                            print('found matching command_key')
                            value = self.instance.cached_urls[get]  # type: RegisteredMethod
                            self.handle_data(value.command_key, sock)
                            if value.return_type != 'str':
                                # give default empty response
                                self.reply(None, sock)
                            found = True
                        elif get == b'/api':
                            l = list()
                            for key in self.instance.cached_urls.keys():
                                l.append(key.decode('utf-8'))
                            self.reply(l, sock)
                        elif get == b'/api?class':
                            d = dict()
                            for key in self.instance.cached_urls.keys():
                                value = self.instance.cached_urls[key]  # type: RegisteredMethod
                                logical_key = value.logical_path.replace('root.', '')
                                if logical_key not in d.keys():
                                    d[logical_key] = {'methods': list(), 'class': value.class_name, 'path': value.logical_path}
                                d[logical_key]['methods'].append({'name': value.method_name, 'uri': key.decode('utf-8')})
                            self.reply(d, sock)
            if not found:
                print('Returning 404')
                sock.send(b'HTTP/1.1 404 Not found\r\n')
            try:
                sock.close()
            except:
                pass

    def post_loop(self, **kwargs):
        Server.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None):
        Server.reply(self, return_value)

        if type(return_value) is dict or type(return_value) is list:
            msg = json.dumps(return_value)
        else:
            msg = json.dumps({'value': return_value})
        print('returning %s to %s' % (msg, repr(source)))
        response = 'HTTP/1.1 200 OK\r\nContent-Type: application/vnd.api+json\r\nContent-Length: %d\r\n\r\n%s' % (len(msg), msg)
        source.send(response.encode('ascii'))


class WrappedServer(object):
    def __init__(self, server, kwargs):
        self.server = server
        self.kwargs = kwargs


class MultiServer(object):
    def __init__(self):
        self.wrappedservers = list()

    def add(self, server, **kwargs):
        self.wrappedservers.append(WrappedServer(server, kwargs))

    def start(self):
        for wrappedserver in self.wrappedservers:
            wrappedserver.server.pre_loop(**wrappedserver.kwargs)
            wrappedserver.server.loopActive = True

        loopActive = True
        while loopActive:
            for wrappedserver in self.wrappedservers:
                wrappedserver.server.loop_tick(**wrappedserver.kwargs)
                if not wrappedserver.server.loopActive:
                    loopActive = False
                    break

        for wrappedserver in self.wrappedservers:
            wrappedserver.server.post_loop(**wrappedserver.kwargs)
