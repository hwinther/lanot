# coding=utf-8
import usocket
import time
import json
import prometheus
import prometheus.pgc as gc
import prometheus.server
import prometheus.server.socketserver as socketserver
import prometheus.logging as logging
import prometheus.psocket

__version__ = '0.2.2'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class JsonRestServer(socketserver.SocketServer):
    """
    JsonRestServer currently only supports a single client, which is acheived by receiving all the request data
    either without, or with a very low timeout. The low timeout (blocking for say 100ms) was a tradeoff to reduce
    the amount of memory that is allocated, and would ultimately lead to heap fragmentation.
    However the socket connection requests are buffered (TODO: how many does the accept queue hold?), and this
    creates an acceptable replacement for concurrency (multiple receiving contexts, typically worker threads elsewhere)
    """
    def __init__(self, instance, socketwrapper=None, settimeout=0, loop_tick_delay=None):
        socketserver.SocketServer.__init__(self, instance, socketwrapper)

        self.socket = self.socketwrapper(usocket.AF_INET, usocket.SOCK_STREAM)
        self.settimeout = settimeout
        self.loop_tick_delay = loop_tick_delay
        self.recv_size = 500
        # allocate a fixed size bytearray and wrap it in a memoryview, this is reused for each request
        self.memoryview = memoryview(bytearray(self.recv_size))

    def start(self, bind_host='', bind_port=8080, **kwargs):
        socketserver.SocketServer.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host='', bind_port=8080, **kwargs):
        socketserver.SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        except prometheus.psocket.socket_error:
            # TODO: look into this, when and where does this happen? (I no longer recall)
            logging.warn('could not bind with reuse flag')
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(4)
        if prometheus.server.debug:
            logging.notice('settimeout: %s' % self.settimeout)
        self.socket.settimeout(self.settimeout)
        logging.success('listening on %s:%d (http/json)' % (bind_host, bind_port))

        # TODO: optimize memory usage - working on it
        gc.collect()
        if prometheus.server.debug and prometheus.is_micro:
            logging.debug('mem_free before urls: %s' % gc.mem_free())
        self.instance.update_urls()
        if prometheus.data_debug:
            for key in self.instance.cached_urls.keys():
                logging.info('url: %s' % key)
        gc.collect()
        if prometheus.server.debug and prometheus.is_micro:
            logging.debug('mem_free after urls: %s' % gc.mem_free())

    def loop_tick(self, **kwargs):
        if prometheus.server.debug:
            logging.notice('entering JsonRestServer.loop_tick')
            socketserver.SocketServer.loop_tick(self, **kwargs)

        sock, addr = None, None
        try:
            sock, addr = self.socket.accept()
            sock.settimeout(self.settimeout)
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

            # data = None
            view = self.memoryview  # temporary replacement
            received_bytes = 0
            try:
                # data = sock.recv(self.recv_size)
                received_bytes = sock.readinto(self.memoryview)
                # view = self.memoryview[:received_bytes]
                # TODO: this should've worked, but due to how readinto functions we need to parse the whole view
                # this may work in cPython, haven't really tested it, but i suspect its a difference between
                # cPython's recv_into and uPython's readinto methods
            except prometheus.psocket.socket_error as exception:
                # Note: uPython will raise EAGAIN here if you did not construct the class with a timeout
                #  whereas cPython will not..
                # print(exception)
                if prometheus.is_micro:
                    if exception.args[0] != 11 and exception.args[0] != 110 and exception.args[0] != 23:
                        logging.error(exception)
                        raise
                else:
                    if exception.errno != 11 and exception.errno != 110 and exception.errno != 10035:
                        logging.error(exception)
                        raise

            # print('parsing:')
            # print(received_bytes)
            # if view is not None:
            # if prometheus.is_micro:
            #     print(repr(bytes(self.memoryview)))
            # else:
            #     print(repr(self.memoryview.tobytes()))

            if view is None:
                sock.close()
                return

            found = False
            start = 0
            current = 0
            for byte in view:
                if (type(byte) is int and byte != 10) or (type(byte) is bytes and byte != b'\n'):
                    current += 1
                    continue
                if (type(byte) is int and byte == 0) or (type(byte) is bytes and byte == 'b\x00'):
                    # EOS
                    break

                # if prometheus.is_micro:
                #     line = bytes(view[start:current+1])
                # else:
                #     line = view[start:current + 1].tobytes()
                line = view[start:current+1]

                start = current + 1
                current += 1

                verb = line[0:5]
                # TODO: this check should be for python3.x and not is_micro!
                if prometheus.is_micro:
                    if bytes(verb) != b'GET /':
                        continue
                else:
                    if verb.tobytes() != b'GET /':
                        continue

                # GET /url?param=value HTTP/1.1\r\n
                path = None
                line_counter = 5
                for line_byte in line[5:]:
                    if (type(line_byte) is int and line_byte == 32) or (type(line_byte) is bytes and line_byte == b' '):
                        if prometheus.is_micro:
                            path = bytes(line[5:line_counter])
                        else:
                            path = line[5:line_counter].tobytes()
                        break
                    if (type(byte) is int and byte == 0) or (type(byte) is bytes and byte == 'b\x00'):
                        # EOS
                        break
                    line_counter += 1

                # failed to parse path
                if path is None:
                    break

                # path = line.split(b' ')[1][1:]
                # path should be url, query should be (dict) param=value
                query = dict()
                if path.find(b'?') != -1:
                    path, querystr = path.split(b'?', 1)
                    query = prometheus.parse_args(querystr)

                logging.notice('get: %s (%s)' % (path, query))

                if self.handle_request(path, query, sock):
                    found = True
                    break

            if not found:
                logging.warn('Returning 404')
                sock.send(b'HTTP/1.1 404 Not found\r\n')

            sock.close()

        if self.loop_tick_delay is not None:
            time.sleep(self.loop_tick_delay)

        if prometheus.server.debug:
            logging.notice('exiting JsonRestServer.loop_tick')

    def handle_request(self, path, query, sock):
        if path in self.instance.cached_urls.keys():
            logging.notice('found matching command_key')
            value = self.instance.cached_urls[path]  # type: prometheus.RegisteredMethod
            if not self.handle_data(value.command_key, source=sock, context=query):
                if value.return_type != 'str':
                    # give default empty response
                    self.reply(return_value=None, source=sock, context=query)
            return True
        elif path == b'schema':
            schema = dict()
            for key in self.instance.cached_urls.keys():
                value = self.instance.cached_urls[key]  # type: prometheus.RegisteredMethod
                logical_key = value.logical_path.replace('root.', '')
                if logical_key not in schema.keys():
                    schema[logical_key] = {'methods': dict(), 'class': value.class_name,
                                           'path': value.logical_path}
                schema[logical_key]['methods'][value.method_name] = key.decode('utf-8')
            if prometheus.server.debug:
                logging.debug('before api: %s' % str(gc.mem_free()))
            gc.collect()
            if prometheus.server.debug:
                logging.debug('after api: %s' % str(gc.mem_free()))
            self.reply(return_value=schema, source=sock, context=query)
            return True
        elif path == b'schemauri':
            lst = list()
            for key in self.instance.cached_urls.keys():
                lst.append(key.decode('utf-8'))
            self.reply(return_value=lst, source=sock, context=query)
            return True
        elif path == b'favicon.ico':
            self.reply(return_value=prometheus.server.favicon,
                       source=sock,
                       context=query,
                       contenttype='image/x-icon')
            return True
        else:
            return self.handle_data(path, source=sock, context=query)

    def post_loop(self, **kwargs):
        socketserver.SocketServer.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None, context=None, contenttype=None, **kwargs):
        socketserver.SocketServer.reply(self, return_value, **kwargs)

        # JSON contenttype is assumed/default
        if contenttype is None:
            contenttype = 'application/vnd.api+json'

        if contenttype == 'application/vnd.api+json':
            if isinstance(return_value, (dict, list)):
                msg = json.dumps(return_value)
            else:
                if isinstance(return_value, bytes):
                    return_value = return_value.decode('utf-8')
                # print('ret: %s' % repr(return_value))
                msg = json.dumps({'value': return_value})

            if context is not None and 'callback' in context.keys():
                callback = context['callback']  # .decode('utf-8')
                msg = '%s(%s)' % (callback, msg)

            # convert to bytes
            msg = msg.encode('ascii')
            if True:  # prometheus.server.debug:
                logging.notice('returning %s to %s' % (msg, repr(source)))
            else:
                logging.notice('returning %d bytes' % len(msg))
        else:
            # raw mode - could be image or other binary data
            msg = return_value
            logging.notice('returning %d bytes' % len(msg))

        response = b'HTTP/1.1 200 OK\r\n' +\
                   b'Server: ps-%s\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: %s\r\nContent-Length: %d\r\n\r\n'\
                   % (prometheus.server.__version__.encode('ascii'), contenttype.encode('ascii'), len(msg))
        response = response + msg
        # logging.notice(repr(response))

        source.send(response)
