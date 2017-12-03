import socket
import sys
import os
import json
import gc
import time
import prometheus
import prometheus_logging as logging

__version__ = '0.1.4'
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

if prometheus.is_micro:
    socket_error = Exception
else:
    socket_error = socket.error
# 11 EAGAIN (try again later)
# 110 Connection timed out
# 23 cant read data?
# 10035 WSAEWOULDBLOCK (A non-blocking socket operation could not be completed immediately)


class Server(object):
    # :type data_commands: dict
    # :type instance: Prometheus
    # :type loopActive: bool
    def __init__(self, instance):
        """
        :type instance: Prometheus
        :param instance: Instance of Prometheus
        """
        self.instance = instance
        self.loop_active = False

    def start(self, **kwargs):
        self.pre_loop(**kwargs)
        self.loop_active = True
        while self.loop_active:
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
            logging.notice('entering Server.handle_data')
        if command == '':
            return

        if debug:
            logging.notice('input: %s' % repr(command))

        if type(command) is bytes:
            command = command.decode('utf-8')

        if command == 'die':
            logging.warn('die command received')
            self.loop_active = False
            return
        elif command == 'cap':
            # capability
            return_value = ''
            for command in self.instance.cached_remap:
                return_value = return_value + command
            self.reply(return_value, source=source, **kwargs)
        elif command == 'uname':
            self.reply(self.uname(), source=source, **kwargs)
        elif command == 'version':
            self.reply(self.version(), source=source, **kwargs)
        elif command == 'sysinfo':
            self.reply(self.sysinfo(), source=source, **kwargs)
        elif command in self.instance.cached_remap:
            registered_method = self.instance.cached_remap[command]  # type: prometheus.RegisteredMethod
            return_value = registered_method.method_reference()
            if registered_method.return_type == 'str':
                self.reply(return_value, source=source, **kwargs)
        else:
            logging.error('invalid cmd: %s' % command)
        if debug:
            logging.notice('exiting Server.handle_data')

        gc.collect()

    def uname(self):
        if debug:
            logging.notice('Server.uname')
        hostname = self.instance.__class__.__name__
        if prometheus.is_micro:
            un = os.uname()
            return '%s %s %s %s %s MicroPython' % (un[0], hostname, un[2], un[3], un[4])
        else:
            # assume win32 or unix
            import platform
            # return '%s %s %s %s CPython' % (hostname, str(sys.version).replace('\n', ''), platform.platform(), sys.platform)
            un = platform.uname()
            return '%s-%s %s@%s %s %s %s CPython' % (un[0], un[2], hostname, un[1], un[3], str(sys.version).split(' ')[0], un[4])

    def version(self):
        return '%s/%s' % (__version__, prometheus.__version__)

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
        if prometheus.is_micro:
            stvfs = os.statvfs('/')
            freespace = (stvfs[0] * stvfs[3]) / 1048576
            gc.collect()
            return '%.2fMB vfs free, %.2fKB mem free' % (freespace, gc.mem_free()/1024)
        else:
            return 'Not implemented for this platform'


class SocketServer(Server):
    def __init__(self, instance, socketwrapper=None):
        Server.__init__(self, instance)

        if socketwrapper is None:
            if debug:
                logging.notice('using socket.socket default')
            socketwrapper = socket.socket

        if debug:
            logging.notice('setting socketwrapper')
        self.socketwrapper = socketwrapper


class UdpSocketServer(SocketServer):
    def __init__(self, instance, socketwrapper=None):
        SocketServer.__init__(self, instance, socketwrapper)
        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_DGRAM)
        self.split_chars = '\n'
        self.end_chars = '\r'
        self.buffers = dict()  # :type dict(Buffer)

    def start(self, bind_host='', bind_port=9195, **kwargs):
        SocketServer.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host, bind_port, **kwargs):
        SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            logging.warn('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.settimeout(0)
        logging.success('listening on %s:%d (udp)' % (bind_host, bind_port))

    def loop_tick(self, **kwargs):
        SocketServer.loop_tick(self, **kwargs)

        data, addr = None, None
        try:
            # TODO: buffer could be higher, but then the buffer class needs to prune its rest buffer over time
            data, addr = self.socket.recvfrom(500)
        except socket_error as e:
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
            logging.notice('Creating new buffer context')
            # TODO: clean up buffer contexts over time!
            # TODO: this must be done in Tcp implementation also
            if len(self.buffers) > 2:
                logging.notice('Cleaning up old buffers')
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
            if type(command) is bytes:
                command = command.decode('ascii')
            logging.notice('Calling handle data')
            self.handle_data(command, addr)

        gc.collect()

    def post_loop(self, **kwargs):
        SocketServer.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None, **kwargs):
        SocketServer.reply(self, return_value, **kwargs)

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


class TcpSocketServer(SocketServer):
    def __init__(self, instance, socketwrapper=None):
        SocketServer.__init__(self, instance, socketwrapper)
        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_STREAM)
        self.splitChars = '\n'
        self.endChars = '\r'
        self.sockets = dict()  # type: dict((str,int), socket.socket)
        self.buffers = dict()  # type: dict((str,int), prometheus.Buffer)

    def start(self, bind_host='', bind_port=9195):
        SocketServer.start(self, bind_host=bind_host, bind_port=bind_port)

    def pre_loop(self, bind_host='', bind_port=9195, **kwargs):
        SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            logging.warn('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(1)
        self.socket.settimeout(0)
        logging.success('listening on %s:%d (tcp)' % (bind_host, bind_port))

    def loop_tick(self, **kwargs):
        SocketServer.loop_tick(self, **kwargs)

        sock, addr = None, None
        try:
            # TODO: put this pair in a wrapper class
            sock, addr = self.socket.accept()
        except socket_error as e:
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
            except socket_error as e:
                if prometheus.is_micro:
                    if e.args[0] == 104:
                        logging.notice('disconnected')
                        del self.buffers[addr]
                        continue
                    if e.args[0] != 11 and e.args[0] != 110 and e.args[0] != 23:
                        logging.error(e)
                        raise
                else:
                    if e.errno == 104:
                        logging.notice('disconnected')
                        del self.buffers[addr]
                        continue
                    if e.errno != 11 and e.errno != 104 and e.errno != 110 and e.errno != 10035 and e.errno != 10054:
                        logging.error(e)
                        raise

            if data is not None:
                logging.notice('Got data from %s' % repr(addr))
                self.buffers[addr].parse(data.decode('utf-8'))

                while True:
                    command = self.buffers[addr].pop()
                    if command is None:
                        logging.notice('Breaking command loop')
                        break
                    logging.notice('Calling handle data')
                    self.handle_data(command, self.sockets[addr])

    def post_loop(self, **kwargs):
        SocketServer.post_loop(self, **kwargs)

        # attempt a graceful shutdown of all sockets
        for addr in self.sockets.keys():
            self.sockets[addr].close()
        self.socket.close()

    def reply(self, return_value, source=None, **kwargs):
        SocketServer.reply(self, return_value, **kwargs)

        if type(return_value) is str:
            return_value = return_value.encode('utf-8')

        logging.notice('returning %s to %s' % (return_value, repr(source)))
        source.send(b'%s%s%s' % (return_value, self.endChars.encode('utf-8'), self.splitChars.encode('utf-8')))


class JsonRestServer(SocketServer):
    def __init__(self, instance, socketwrapper=None, settimeout=0, loop_tick_delay=None):
        SocketServer.__init__(self, instance, socketwrapper)

        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_STREAM)
        self.settimeout = settimeout
        self.loop_tick_delay = loop_tick_delay

    def start(self, bind_host='', bind_port=8080, **kwargs):
        SocketServer.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host, bind_port, **kwargs):
        SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            logging.warn('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(4)
        if debug:
            logging.notice('settimeout: %s' % self.settimeout)
        self.socket.settimeout(self.settimeout)
        logging.success('listening on %s:%d (http/json)' % (bind_host, bind_port))

        self.instance.update_urls()
        if prometheus.data_debug:
            for key in self.instance.cached_urls.keys():
                logging.info('url: %s' % key)

    def loop_tick(self, **kwargs):
        if debug:
            logging.notice('entering JsonRestServer.loop_tick')
        SocketServer.loop_tick(self, **kwargs)

        sock, addr = None, None
        try:
            # TODO: put this pair in a wrapper class
            sock, addr = self.socket.accept()
        except socket_error as e:
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

            data = None
            try:
                data = sock.recv(1024)
            except socket_error as e:
                if prometheus.is_micro:
                    if e.args[0] != 11 and e.args[0] != 110 and e.args[0] != 23:
                        logging.error(e)
                        raise
                else:
                    if e.errno != 11 and e.errno != 110 and e.errno != 10035:
                        logging.error(e)
                        raise

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
                        logging.notice('get: %s (%s)' % (path, query))
                        if path in self.instance.cached_urls.keys():
                            logging.notice('found matching command_key')
                            value = self.instance.cached_urls[path]  # type: prometheus.RegisteredMethod
                            self.handle_data(value.command_key, source=sock, query=query)
                            if value.return_type != 'str':
                                # give default empty response
                                self.reply(return_value=None, source=sock, query=query)
                            found = True
                        elif path == b'/api' and b'class' in query.keys():
                            d = dict()
                            for key in self.instance.cached_urls.keys():
                                value = self.instance.cached_urls[key]  # type: prometheus.RegisteredMethod
                                logical_key = value.logical_path.replace('root.', '')
                                if logical_key not in d.keys():
                                    d[logical_key] = {'methods': dict(), 'class': value.class_name, 'path': value.logical_path}
                                d[logical_key]['methods'][value.method_name] = key.decode('utf-8')
                            # logging.notice('before: %s' % str(gc.mem_free()))
                            gc.collect()
                            # logging.notice('after: %s' % str(gc.mem_free()))
                            self.reply(return_value=d, source=sock, query=query)
                            found = True
                        elif path == b'/api':
                            lst = list()
                            for key in self.instance.cached_urls.keys():
                                lst.append(key.decode('utf-8'))
                            self.reply(return_value=lst, source=sock, query=query)
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
                logging.warn('Returning 404')
                sock.send(b'HTTP/1.1 404 Not found\r\n')

            sock.close()

        if self.loop_tick_delay is not None:
            time.sleep(self.loop_tick_delay)

        if debug:
            logging.notice('exiting JsonRestServer.loop_tick')

    def post_loop(self, **kwargs):
        SocketServer.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None, query=None, contenttype=None, **kwargs):
        SocketServer.reply(self, return_value, **kwargs)

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
                logging.notice('returning %s to %s' % (msg, repr(source)))
            else:
                logging.notice('returning %d bytes' % len(msg))
        else:
            # raw mode - could be image or other binary data
            msg = return_value
            logging.notice('returning %d bytes' % len(msg))

        response = b'HTTP/1.1 200 OK\r\nServer: ps-%s\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: %s\r\nContent-Length: %d\r\n\r\n' % \
                   (__version__.encode('ascii'), contenttype.encode('ascii'), len(msg))
        response = response + msg
        # logging.notice(repr(response))

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

        loop_active = True
        while loop_active:
            for wrappedserver in self.wrappedservers:
                wrappedserver.server.loop_tick(**wrappedserver.kwargs)
                if not wrappedserver.server.loopActive:
                    loop_active = False
                    break

        for wrappedserver in self.wrappedservers:
            wrappedserver.server.post_loop(**wrappedserver.kwargs)
