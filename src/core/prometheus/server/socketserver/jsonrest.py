# coding=utf-8
import socket
import time
import json
import prometheus
import prometheus.pgc as gc
import prometheus.server
import prometheus.server.socketserver as socketserver
import prometheus.logging as logging
import prometheus.psocket

gc.collect()


class JsonRestServer(socketserver.SocketServer):
    def __init__(self, instance, socketwrapper=None, settimeout=0, loop_tick_delay=None):
        socketserver.SocketServer.__init__(self, instance, socketwrapper)

        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_STREAM)
        self.settimeout = settimeout
        self.loop_tick_delay = loop_tick_delay

    def start(self, bind_host='', bind_port=8080, **kwargs):
        socketserver.SocketServer.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host='', bind_port=8080, **kwargs):
        socketserver.SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except prometheus.psocket.socket_error:
            logging.warn('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.listen(4)
        if prometheus.server.debug:
            logging.notice('settimeout: %s' % self.settimeout)
        self.socket.settimeout(self.settimeout)
        logging.success('listening on %s:%d (http/json)' % (bind_host, bind_port))

        # TODO: optimize memory usage
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

            data = None
            try:
                data = sock.recv(1024)
            except prometheus.psocket.socket_error as exception:
                if prometheus.is_micro:
                    if exception.args[0] != 11 and exception.args[0] != 110 and exception.args[0] != 23:
                        logging.error(exception)
                        raise
                else:
                    if exception.errno != 11 and exception.errno != 110 and exception.errno != 10035:
                        logging.error(exception)
                        raise

            found = False
            if data is not None and data.find(b'\r\n') != -1:
                for line in data.split(b'\r\n'):
                    if not line:
                        continue

                    if line.find(b'GET /') != -1:
                        # GET /url?param=value HTTP/1.1
                        path = line.split(b' ')[1][1:]
                        # path should be url, query should be (dict) param=value
                        query = dict()
                        if path.find(b'?') != -1:
                            path, querystr = path.split(b'?', 1)
                            query = prometheus.parse_args(querystr)

                        logging.notice('get: %s (%s)' % (path, query))

                        if self.handle_request(path, query, sock):
                            found = True
                            break

            if not found and data is not None:
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
            self.handle_data(value.command_key, source=sock, context=query)
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
                print('ret: %s' % repr(return_value))
                msg = json.dumps({'value': return_value})

            if context is not None and b'callback' in context.keys():
                callback = context[b'callback'].decode('utf-8')
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
