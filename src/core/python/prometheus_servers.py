import machine
import socket
import time
import gc
import json
from prometheus import Buffer, RegisteredMethod


gc.collect()


class Server(object):
    # :type data_commands: dict
    def __init__(self, instance):
        """
        :type instance: Prometheus
        :param instance: Instance of Prometheus
        """
        self.instance = instance
        self.data_commands = self.instance.recursive_remap()
        self.loopActive = False

    def handle_data(self, command, source=None):
        if command == '':
            return

        print('input:', command)

        if command in self.data_commands:
            registered_method = self.data_commands[command]  # type: RegisteredMethod
            return_value = registered_method.method_reference()
            if registered_method.return_type == 'str':
                self.reply(return_value, source)
        elif command == 'die':
            print('die command received')
            self.loopActive = False
            return
        else:
            print('invalid cmd', command)

    def reply(self, return_value, source=None):
        pass


class UdpSocketServer(Server):
    def __init__(self, instance):
        Server.__init__(self, instance)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.splitChars = '\n'
        self.endChars = '\r'

    def start(self, bind_host='', bind_port=9195):
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            print('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.settimeout(0)
        print('listening on %s:%d' % (bind_host, bind_port))

        buffers = dict()  # :type list(Buffer)

        self.loopActive = True
        while self.loopActive:
            data, addr = None, None
            try:
                data, addr = self.socket.recvfrom(1024)
            except:
                pass

            if data is None:
                continue

            print('recv %s from %s' % (repr(data), repr(addr)))

            if addr not in buffers.keys():
                print('creating new buffer context')
                buffers[addr] = Buffer(split_chars=self.splitChars, end_chars=self.endChars)

            buffers[addr].parse(data.decode('utf-8'))

            while True:
                command = buffers[addr].pop()
                if command is None:
                    print('Breaking command loop')
                    break
                print('Calling handle data')
                self.handle_data(command, addr)

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

    def start(self, bind_host='', bind_port=9195):
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            print('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(1)
        self.socket.settimeout(0)
        print('listening on %s:%d' % (bind_host, bind_port))

        sockets = dict()  # type: dict((str,int), socket.socket)
        buffers = dict()  # type: dict((str,int), Buffer)

        self.loopActive = True
        while self.loopActive:
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
                print('creating new buffer context')
                buffers[addr] = Buffer(split_chars=self.splitChars, end_chars=self.endChars)
                sockets[addr] = sock

            # TODO: would be more efficient by using Poll (which is the micropython way)
            # TODO: do socket cleanup when they go away (cause an exception that isnt timeout, i suppose)
            for addr in buffers.keys():
                data = None
                try:
                    data = sockets[addr].recv(1024)
                except:
                    pass

                if data is not None:
                    print('Got data from %s' % repr(addr))
                    buffers[addr].parse(data.decode('utf-8'))

                    while True:
                        command = buffers[addr].pop()
                        if command is None:
                            print('Breaking command loop')
                            break
                        print('Calling handle data')
                        self.handle_data(command, sockets[addr])

        # attempt a graceful shutdown of all sockets
        for addr in sockets.keys():
            try:
                sockets[addr].close()
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

    def start(self, bind_host='', bind_port=8080):
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            print('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(1)
        self.socket.settimeout(0)
        print('listening on %s:%d' % (bind_host, bind_port))

        urls = dict()
        for key in self.data_commands.keys():
            value = self.data_commands[key]
            url = '/' + '/'.join(value.logical_path.split('.')) + '/' + value.method_name
            print('url: %s' % url)
            urls[url] = value

        # gc.mem_free()
        # gc.collect()
        # gc.mem_free()

        self.loopActive = True
        while self.loopActive:
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
                if data is not None and data.find('\r\n') != -1:
                    for line in data.split('\r\n'):
                        if line == '':
                            continue
                        if line.find('GET /') != -1:
                            get = line.split(' ')[1]
                            print('get: %s' % get)
                            if get in urls.keys():
                                print('found matching command_key')
                                value = urls[get]  # type: RegisteredMethod
                                self.handle_data(value.command_key, sock)
                                if value.return_type != 'str':
                                    # give default empty response
                                    self.reply(None, sock)
                                found = True
                if not found:
                    print('Returning 404')
                    sock.send('HTTP/1.1 404 Not found\r\n')
                try:
                    sock.close()
                except:
                    pass

        self.socket.close()

    def reply(self, return_value, source=None):
        Server.reply(self, return_value)
        msg = json.dumps({'value': return_value})
        print('returning %s to %s' % (msg, repr(source)))
        source.send(b'HTTP/1.1 200 OK\r\nContent-Type: application/vnd.api+json\r\nContent-Length: %d\r\n\r\n%s' % (len(msg), msg))
