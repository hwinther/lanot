import socket
import sys
import os
import json
import gc
from prometheus import Buffer, RegisteredMethod
from prometheus import __version__ as prometheus__version
is_micro = sys.platform in ['esp8266', 'esp32', 'WiPy']
if is_micro:
    from ussl import wrap_socket as ssl_wrap_socket
    # from ussl import SSLEOFError as ssl_SSLEOFError
else:
    from ssl import wrap_socket as ssl_wrap_socket
    from ssl import SSLEOFError as ssl_SSLEOFError

__version__ = '0.1.3cx'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()

favicon = b'\x00\x00\x01\x00\x01\x00\x10\x10\x10\x00\x01\x00\x04\x00(\x01\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00\x04\x00' +\
          b'\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x84\x00\x00\x00\x00\x00\x00' +\
          b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' +\
          b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x10\x10\x00\x00\x00\x00' +\
          b'\x00\x10\x01\x01\x00\x00\x00\x00\x00\x10\x01\x01\x00\x00\x00\x00\x01\x10\x01\x01\x00\x11\x00\x01\x00\x10\x00\x10\x01\x00\x10\x01\x00\x00\x00\x00' +\
          b'\x01\x00\x10\x01\x00\x00\x00\x00\x01\x00\x10\x01\x00\x00\x00\x00\x00\x11\x00\x11\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x11\x01\x01' +\
          b'\x01\x00\x10\x00\x01\x00\x01\x11\x01\x01\x10\x00\x01\x00\x01\x01\x01\x10\x10\x00\x01\x00\x00\x10\x01\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00' +\
          b'\xff\xff\x00\x00\xff\xd5\x00\x00\xff\xda\x00\x00\xff\xda\x00\x00\xff\x9a\x00\x00\xce\xdd\x00\x00\xb6\xff\x00\x00\xb6\xff\x00\x00\xb6\xff\x00\x00' +\
          b'\xcc\x7f\x00\x00\xff\xff\x00\x00\x8a\xb7\x00\x00\xb8\xa7\x00\x00\xba\x97\x00\x00\xbd\xb7\x00\x00\xff\xff\x00\x00'
debug = False


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

    def reply(self, return_value, source=None, **kwargs):
        pass

    def handle_data(self, command, source=None, **kwargs):
        if debug:
            print('entering Server.handle_data')
        if command == '':
            return

        if debug:
            print('input:', command)

        if command == 'die':
            print('die command received')
            self.loopActive = False
            return
        elif command == 'cap':
            # capability
            return_value = ''
            for command in self.instance.cached_remap:
                return_value = return_value + command

            # print('before: %s' % str(gc.mem_free()))
            # gc.collect()
            # print('after: %s' % str(gc.mem_free()))

            self.reply(return_value, source=source, **kwargs)
        elif command == 'uname':
            self.reply(self.uname(), source=source, **kwargs)
        elif command == 'version':
            self.reply(self.version(), source=source, **kwargs)
        elif command == 'sysinfo':
            self.reply(self.sysinfo(), source=source, **kwargs)
        elif command in self.instance.cached_remap:
            registered_method = self.instance.cached_remap[command]  # type: RegisteredMethod
            return_value = registered_method.method_reference()
            if registered_method.return_type == 'str':
                self.reply(return_value, source=source, **kwargs)
        else:
            print('invalid cmd', command)
        if debug:
            print('exiting Server.handle_data')

        gc.collect()

    def uname(self):
        if debug:
            print('Server.uname')
        hostname = self.instance.__class__.__name__
        if is_micro:
            un = os.uname()
            return '%s %s %s %s %s MicroPython' % (un[0], hostname, un[2], un[3], un[4])
        else:
            # assume win32 or unix
            import platform
            # return '%s %s %s %s CPython' % (hostname, str(sys.version).replace('\n', ''), platform.platform(), sys.platform)
            un = platform.uname()
            return '%s-%s %s@%s %s %s %s CPython' % (un[0], un[2], hostname, un[1], un[3], str(sys.version).split(' ')[0], un[4])

    def version(self):
        return '%s/%s' % (__version__, prometheus__version)

    def sysinfo(self):
        # struct statvfs {
        #     unsigned long  f_bsize;    /* file system block size */
        #     unsigned long  f_frsize;   /* fragment size */
        #     fsblkcnt_t     f_blocks;   /* size of fs in f_frsize units */
        #     fsblkcnt_t     f_bfree;    /* # free blocks */
        #     fsblkcnt_t     f_bavail;   /* # free blocks for unprivileged users */
        #     fsfilcnt_t     f_files;    /* # inodes */
        #     fsfilcnt_t     f_ffree;    /* # free inodes */
        #     fsfilcnt_t     f_favail;   /* # free inodes for unprivileged users */
        #     unsigned long  f_fsid;     /* file system ID */
        #     unsigned long  f_flag;     /* mount flags */
        #     unsigned long  f_namemax;  /* maximum filename length */
        # };
        if is_micro:
            stvfs = os.statvfs('/')
            freespace = (stvfs[0] * stvfs[3]) / 1048576
            gc.collect()
            return '%.2fMB vfs free, %.2fKB mem free' % (freespace, gc.mem_free()/1024)
        else:
            return 'Not implemented for this platform'


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
            # TODO: buffer could be higher, but then the buffer class needs to prune its rest buffer over time
            data, addr = self.socket.recvfrom(500)
        except OSError as e:
            if e.args[0] not in [110, 10035]:
                raise

        if data is None:
            return

        print('recv %s from %s' % (repr(data), repr(addr)))

        if addr not in self.buffers.keys():
            print('Creating new buffer context')
            # TODO: clean up buffer contexts over time!
            # TODO: this must be done in Tcp implementation also
            if len(self.buffers) > 2:
                print('cleaning up old buffers')
                del(self.buffers)
                self.buffers = dict()
                gc.collect()
            self.buffers[addr] = Buffer(split_chars=self.splitChars, end_chars=self.endChars)

        if type(data) is str:
            # convert to bytes?
            data = data.decode('ascii')
        self.buffers[addr].parse(data)

        while True:
            command = self.buffers[addr].pop()
            if command is None:
                # print('Breaking command loop')
                break
            if type(command) is bytes:
                command = command.decode('ascii')
            print('Calling handle data')
            self.handle_data(command, addr)

        gc.collect()

    def post_loop(self, **kwargs):
        Server.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None, **kwargs):
        Server.reply(self, return_value, **kwargs)

        if type(return_value) is str:
            return_value = return_value.encode('ascii')
        elif type(return_value) is bytes:
            pass
        else:
            return_value = b'%s' % return_value
        print('returning %s to %s' % (return_value, repr(source)))
        self.socket.sendto(b'%s%s%s' % (return_value, self.endChars.encode('ascii'),
                                        self.splitChars.encode('ascii')), source)
        gc.collect()


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
                data = self.sockets[addr].recv(100)
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

    def reply(self, return_value, source=None, **kwargs):
        Server.reply(self, return_value, **kwargs)

        print('returning %s to %s' % (return_value, repr(source)))
        source.send(b'%s%s%s' % (return_value, self.endChars, self.splitChars))


class JsonRestServer(Server):
    def __init__(self, instance, usessl = False, settimeout=None):
        Server.__init__(self, instance)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.usessl = usessl
        self.sslsock = None
        self.settimeout = settimeout

    def start(self, bind_host='', bind_port=8080, **kwargs):
        Server.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host, bind_port, **kwargs):
        Server.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            print('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(4)
        if self.settimeout is None:
            self.socket.settimeout(0)
        else:
            print('settimeout override: %s' % self.settimeout)
            self.socket.settimeout(self.settimeout)
        print('listening on %s:%d' % (bind_host, bind_port))

        self.instance.update_urls()
        for key in self.instance.cached_urls.keys():
            print('url: %s' % key)

    def loop_tick(self, **kwargs):
        if debug:
            print('entering JsonRestServer.loop_tick')
        Server.loop_tick(self, **kwargs)

        sock, addr, self.sslsock = None, None, None
        try:
            # TODO: put this pair in a wrapper class
            sock, addr = self.socket.accept()
        except:
            pass  # timeout, i hope

        if sock is not None:
            print('Accepted connection from %s' % repr(addr))

            if self.usessl:
                print('ssl wrap')
                ciphers = "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:AES128-GCM-SHA256:AES128-SHA256:HIGH:"
                ciphers += "!aNULL:!eNULL:!EXPORT:!DSS:!DES:!RC4:!3DES:!MD5:!PSK"
                keyfile = r'C:\Users\dg2\Downloads\bastion.oh.wsh.no.pem'
                certfile = r'C:\Users\dg2\Downloads\bastion.oh.wsh.no-cert.pem'
                cacerts = r'C:\Users\dg2\Downloads\cacert.pem'
                try:
                    self.sslsock = ssl_wrap_socket(sock, server_side=True, keyfile=keyfile, certfile=certfile, ca_certs=cacerts,
                                                   ciphers=ciphers)
                except ssl_SSLEOFError:
                    print('SSLEOFError')
                    return

            try:
                if self.usessl:
                    data = self.sslsock.read(1024)
                else:
                    sock.settimeout(2)
                    data = sock.recv(1024)
            except:
                data = None

            found = False
            if data is not None and data.find(b'\r\n') != -1:
                for line in data.split(b'\r\n'):
                    if len(line) == 0:
                        continue
                    if line.find(b'GET /') != -1:
                        path = line.split(b' ')[1]
                        query = dict()
                        if path.find(b'?') != -1:
                            path, querystr = path.split(b'?', 1)
                            for q in querystr.split(b'&'):
                                if q.find(b'=') != -1:
                                    key, value = q.split(b'=', 1)
                                    query[key] = value
                                else:
                                    query[q] = True
                        print('get: %s (%s)' % (path, query))
                        if path in self.instance.cached_urls.keys():
                            print('found matching command_key')
                            value = self.instance.cached_urls[path]  # type: RegisteredMethod
                            self.handle_data(value.command_key, source=sock, query=query)
                            if value.return_type != 'str':
                                # give default empty response
                                self.reply(return_value=None, source=sock, query=query)
                            found = True
                        elif path == b'/api' and b'class' in query.keys():
                            d = dict()
                            for key in self.instance.cached_urls.keys():
                                value = self.instance.cached_urls[key]  # type: RegisteredMethod
                                logical_key = value.logical_path.replace('root.', '')
                                if logical_key not in d.keys():
                                    d[logical_key] = {'methods': dict(), 'class': value.class_name, 'path': value.logical_path}
                                d[logical_key]['methods'][value.method_name] = key.decode('utf-8')
                            # print('before: %s' % str(gc.mem_free()))
                            gc.collect()
                            # print('after: %s' % str(gc.mem_free()))
                            self.reply(return_value=d, source=sock, query=query)
                            found = True
                        elif path == b'/api':
                            l = list()
                            for key in self.instance.cached_urls.keys():
                                l.append(key.decode('utf-8'))
                            self.reply(return_value=l, source=sock, query=query)
                            found = True
                        elif path == b'/uname':
                            self.reply(return_value=self.uname(), source=sock, query=query)
                            found = True
                        elif path == b'/version':
                            self.reply(return_value=self.version(), source=sock, query=query)
                            found = True
                        elif path == b'/sysinfo':
                            self.reply(return_value=self.sysinfo(), source=sock, query=query)
                            found = True
                        elif path == b'/die':
                            self.reply(return_value='ok', source=sock, query=query)
                            self.loopActive = False
                            found = True
                        elif path == b'/favicon.ico':
                            self.reply(return_value=favicon, source=sock, contenttype='image/x-icon')
                            found = True

            if not found and data is not None:
                print('Returning 404')
                sock.send(b'HTTP/1.1 404 Not found\r\n')
            # noinspection PyBroadException
            try:
                if self.usessl:
                    self.sslsock.close()
                    sock.close()  # TODO: required?
                else:
                    sock.close()
            except:
                pass

        if debug:
            print('exiting JsonRestServer.loop_tick')

    def post_loop(self, **kwargs):
        Server.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None, query=None, contenttype=None, **kwargs):
        Server.reply(self, return_value, **kwargs)

        # JSON contenttype is assumed/default
        if contenttype is None:
            contenttype = 'application/vnd.api+json'

            if type(return_value) is dict or type(return_value) is list:
                msg = json.dumps(return_value)
            else:
                msg = json.dumps({'value': return_value})

            if query is not None and b'callback' in query.keys():
                callback = query[b'callback'].decode('utf-8')
                msg = '%s(%s)' % (callback, msg)

            # convert to bytes
            msg = msg.encode('ascii')
            if debug:
                print('returning %s to %s' % (msg, repr(source)))
            else:
                print('returning %d bytes' % len(msg))
        else:
            # raw mode - could be image or other binary data
            msg = return_value
            print('returning %d bytes' % len(msg))

        response = b'HTTP/1.1 200 OK\r\nServer: ps-%s\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: %s\r\nContent-Length: %d\r\n\r\n' % \
                   (__version__.encode('ascii'), contenttype.encode('ascii'), len(msg))
        response = response + msg
        # print(repr(response))

        if self.usessl:
            self.sslsock.write(response)
        else:
            source.send(response)


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
