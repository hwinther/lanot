# coding=utf-8
# generated at 2018-09-28 23:25:52
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region LocalTestUdpClient
class LocalTestUdpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientBlueLed', 'bv', str)
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestUdpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('LocalTestUdpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class LocalTestUdpClientDigital0(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientDigital0', 'tv', str)
    def value(self, **kwargs):
        self.send(b'tv', **kwargs)
        return self.recv()


class LocalTestUdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientRedLed', 'rv', str)
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestUdpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('LocalTestUdpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class LocalTestUdpClientSsd(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientSsd', 'sst', str)
    def text(self, **kwargs):
        self.send(b'sst', **kwargs)
        return self.recv()


class LocalTestUdpClientHygrometer(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientHygrometer', 'hr', str)
    def read(self, **kwargs):
        self.send(b'hr', **kwargs)
        return self.recv()


class LocalTestUdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestUdpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestUdpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('LocalTestUdpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
        return self.recv()


class LocalTestUdpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host='', bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((bind_host, bind_port))
        logging.info('listening on %s:%d' % (bind_host, bind_port))
        self.socket.settimeout(0)
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.blue_led = LocalTestUdpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.dht11 = LocalTestUdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.digital0 = LocalTestUdpClientDigital0(self.send, self.recv)
        self.register(digital0=self.digital0)
        self.hygrometer = LocalTestUdpClientHygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.red_led = LocalTestUdpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.ssd = LocalTestUdpClientSsd(self.send, self.recv)
        self.register(ssd=self.ssd)

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)
        self.socket.sendto(data + self.endChars + args + self.splitChars, self.remote_addr)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except prometheus.psocket.socket_error:
            return None, None

    def recv_once(self, buffersize=10):
        data, addr = self.try_recv(buffersize)
        if data is None:
            return None
        if addr not in self.buffers:
            self.buffers[addr] = prometheus.Buffer(split_chars=self.splitChars, end_chars=self.endChars)
        self.buffers[addr].parse(data)
        bufferpacket = self.buffers[addr].pop()
        if bufferpacket is None:
            return None
        return bufferpacket.packet

    def recv(self, buffersize=20):
        return self.recv_timeout(buffersize, 0.5)

    def recv_timeout(self, buffersize, timeout):
        """
        :param buffersize: int
        :param timeout: float
        :return: str
        """
        timestamp = time.time()
        while (time.time() - timestamp) < timeout:
            data = self.recv_once(buffersize)
            if data is not None:
                return data
        return None

    @prometheus.Registry.register('LocalTestUdpClient', '1', str)
    def test1(self, **kwargs):
        self.send(b'1', **kwargs)
        return self.resolve_response(self.recv_timeout(20, 0.5))

    @prometheus.Registry.register('LocalTestUdpClient', '3', str)
    def test3(self, **kwargs):
        self.send(b'3', **kwargs)
        return self.resolve_response(self.recv_timeout(20, 0.5))

    @prometheus.Registry.register('LocalTestUdpClient', '2', str)
    def test2(self, **kwargs):
        self.send(b'2', **kwargs)
        return self.resolve_response(self.recv_timeout(20, 0.5))

    @prometheus.Registry.register('LocalTestUdpClient', '5', str)
    def test5(self, **kwargs):
        self.send(b'5', **kwargs)
        return self.resolve_response(self.recv_timeout(20, 0.5))

    @prometheus.Registry.register('LocalTestUdpClient', '4')
    def test4(self, **kwargs):
        self.send(b'4', **kwargs)

    @prometheus.Registry.register('LocalTestUdpClient', '7', str)
    def test7(self, **kwargs):
        self.send(b'7', **kwargs)
        return self.resolve_response(self.recv_timeout(20, 0.5))

    @prometheus.Registry.register('LocalTestUdpClient', '6', str)
    def test6(self, **kwargs):
        self.send(b'6', **kwargs)
        return self.resolve_response(self.recv_timeout(20, 0.5))

    @prometheus.Registry.register('LocalTestUdpClient', '8', str)
    def test8(self, **kwargs):
        self.send(b'8', **kwargs)
        return self.resolve_response(self.recv_timeout(20, 0.5))

# endregion


# region LocalTestTcpClient
class LocalTestTcpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientBlueLed', 'bv', str)
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestTcpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('LocalTestTcpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class LocalTestTcpClientDigital0(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientDigital0', 'tv', str)
    def value(self, **kwargs):
        self.send(b'tv', **kwargs)
        return self.recv()


class LocalTestTcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientRedLed', 'rv', str)
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestTcpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('LocalTestTcpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class LocalTestTcpClientSsd(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientSsd', 'sst', str)
    def text(self, **kwargs):
        self.send(b'sst', **kwargs)
        return self.recv()


class LocalTestTcpClientHygrometer(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientHygrometer', 'hr', str)
    def read(self, **kwargs):
        self.send(b'hr', **kwargs)
        return self.recv()


class LocalTestTcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestTcpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestTcpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('LocalTestTcpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
        return self.recv()


class LocalTestTcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        
        self.blue_led = LocalTestTcpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.dht11 = LocalTestTcpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.digital0 = LocalTestTcpClientDigital0(self.send, self.recv)
        self.register(digital0=self.digital0)
        self.hygrometer = LocalTestTcpClientHygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.red_led = LocalTestTcpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.ssd = LocalTestTcpClientSsd(self.send, self.recv)
        self.register(ssd=self.ssd)

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.bind_host is not None:
            logging.notice('bound to %s:%d' % (self.bind_host, self.bind_port))
            self.socket.bind((self.bind_host, self.bind_port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(5)
        logging.info('Connecting to %s' % repr(self.remote_addr))
        self.socket.connect(self.remote_addr)

    def send_once(self, data, args):
        self.socket.send(data + self.end_chars + args + self.split_chars)

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)
        if self.socket is None:
            self.create_socket()
        try:
            self.send_once(data, args)
        except prometheus.psocket.socket_error:
            self.create_socket()
            self.send_once(data, args)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except prometheus.psocket.socket_error:
            return None, None

    def recv(self, buffersize=10):
        data, addr = self.try_recv(buffersize)
        if data is None:
            return None
        if addr not in self.buffers:
            self.buffers[addr] = prometheus.Buffer(split_chars=self.split_chars, end_chars=self.end_chars)
        self.buffers[addr].parse(data)
        bufferpacket = self.buffers[addr].pop()
        if bufferpacket is None:
            return None
        return bufferpacket.packet

    @prometheus.Registry.register('LocalTestTcpClient', '1', str)
    def test1(self, **kwargs):
        self.send(b'1', **kwargs)
        return self.resolve_response(self.recv(50))

    @prometheus.Registry.register('LocalTestTcpClient', '3', str)
    def test3(self, **kwargs):
        self.send(b'3', **kwargs)
        return self.resolve_response(self.recv(50))

    @prometheus.Registry.register('LocalTestTcpClient', '2', str)
    def test2(self, **kwargs):
        self.send(b'2', **kwargs)
        return self.resolve_response(self.recv(50))

    @prometheus.Registry.register('LocalTestTcpClient', '5', str)
    def test5(self, **kwargs):
        self.send(b'5', **kwargs)
        return self.resolve_response(self.recv(50))

    @prometheus.Registry.register('LocalTestTcpClient', '4')
    def test4(self, **kwargs):
        self.send(b'4', **kwargs)

    @prometheus.Registry.register('LocalTestTcpClient', '7', str)
    def test7(self, **kwargs):
        self.send(b'7', **kwargs)
        return self.resolve_response(self.recv(50))

    @prometheus.Registry.register('LocalTestTcpClient', '6', str)
    def test6(self, **kwargs):
        self.send(b'6', **kwargs)
        return self.resolve_response(self.recv(50))

    @prometheus.Registry.register('LocalTestTcpClient', '8', str)
    def test8(self, **kwargs):
        self.send(b'8', **kwargs)
        return self.resolve_response(self.recv(50))

# endregion


# region LocalTestJsonRestClient
class LocalTestJsonRestClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestJsonRestClientBlueLed', 'api/blue_led/value', str)
    def value(self, **kwargs):
        self.send(b'api/blue_led/value', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestJsonRestClientBlueLed', 'api/blue_led/on')
    def on(self, **kwargs):
        self.send(b'api/blue_led/on', **kwargs)

    @prometheus.Registry.register('LocalTestJsonRestClientBlueLed', 'api/blue_led/off')
    def off(self, **kwargs):
        self.send(b'api/blue_led/off', **kwargs)


class LocalTestJsonRestClientDigital0(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestJsonRestClientDigital0', 'api/digital0/value', str)
    def value(self, **kwargs):
        self.send(b'api/digital0/value', **kwargs)
        return self.recv()


class LocalTestJsonRestClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestJsonRestClientRedLed', 'api/red_led/value', str)
    def value(self, **kwargs):
        self.send(b'api/red_led/value', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestJsonRestClientRedLed', 'api/red_led/on')
    def on(self, **kwargs):
        self.send(b'api/red_led/on', **kwargs)

    @prometheus.Registry.register('LocalTestJsonRestClientRedLed', 'api/red_led/off')
    def off(self, **kwargs):
        self.send(b'api/red_led/off', **kwargs)


class LocalTestJsonRestClientSsd(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestJsonRestClientSsd', 'api/ssd/text', str)
    def text(self, **kwargs):
        self.send(b'api/ssd/text', **kwargs)
        return self.recv()


class LocalTestJsonRestClientHygrometer(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestJsonRestClientHygrometer', 'api/hygrometer/read', str)
    def read(self, **kwargs):
        self.send(b'api/hygrometer/read', **kwargs)
        return self.recv()


class LocalTestJsonRestClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestJsonRestClientDht11', 'api/dht11/measure')
    def measure(self, **kwargs):
        self.send(b'api/dht11/measure', **kwargs)

    @prometheus.Registry.register('LocalTestJsonRestClientDht11', 'api/dht11/temperature', str)
    def temperature(self, **kwargs):
        self.send(b'api/dht11/temperature', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestJsonRestClientDht11', 'api/dht11/value', str)
    def value(self, **kwargs):
        self.send(b'api/dht11/value', **kwargs)
        return self.recv()

    @prometheus.Registry.register('LocalTestJsonRestClientDht11', 'api/dht11/humidity', str)
    def humidity(self, **kwargs):
        self.send(b'api/dht11/humidity', **kwargs)
        return self.recv()


class LocalTestJsonRestClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=8080, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        
        self.blue_led = LocalTestJsonRestClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.dht11 = LocalTestJsonRestClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.digital0 = LocalTestJsonRestClientDigital0(self.send, self.recv)
        self.register(digital0=self.digital0)
        self.hygrometer = LocalTestJsonRestClientHygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.red_led = LocalTestJsonRestClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.ssd = LocalTestJsonRestClientSsd(self.send, self.recv)
        self.register(ssd=self.ssd)

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.bind_host is not None:
            logging.notice('bound to %s:%d' % (self.bind_host, self.bind_port))
            self.socket.bind((self.bind_host, self.bind_port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(5)
        self.socket.connect(self.remote_addr)

    def send_once(self, data, args):
        if len(args) is not 0:
            args = b'?' + args
        request = b'GET /%s%s HTTP/1.1\r\nHost: %s\r\n' % (data, args, self.remote_addr[0].encode('utf-8'))
        self.socket.send(request)

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)

        self.create_socket()
        self.send_once(data, args)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except prometheus.psocket.socket_error:
            return None, None

    def recv(self, buffersize=200):
        data, addr = self.try_recv(buffersize)

        self.socket.close()
        if data is None:
            return None

        head, body = data.split(b'\r\n\r\n', 1)
        import json
        json_body = json.loads(body)

        return json_body['value']

    @prometheus.Registry.register('LocalTestJsonRestClient', 'v', str)
    def value(self, **kwargs):
        self.send(b'api/blue_led/value', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', 'v', str)
    def value(self, **kwargs):
        self.send(b'api/digital0/value', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', '1')
    def on(self, **kwargs):
        self.send(b'api/blue_led/on', **kwargs)

    @prometheus.Registry.register('LocalTestJsonRestClient', '2', str)
    def test2(self, **kwargs):
        self.send(b'api/test2', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', 'h', str)
    def humidity(self, **kwargs):
        self.send(b'api/dht11/humidity', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', '8', str)
    def test8(self, **kwargs):
        self.send(b'api/test8', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', 'm')
    def measure(self, **kwargs):
        self.send(b'api/dht11/measure', **kwargs)

    @prometheus.Registry.register('LocalTestJsonRestClient', 't', str)
    def temperature(self, **kwargs):
        self.send(b'api/dht11/temperature', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', '6', str)
    def test6(self, **kwargs):
        self.send(b'api/test6', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', 'r', str)
    def read(self, **kwargs):
        self.send(b'api/hygrometer/read', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', '4')
    def test4(self, **kwargs):
        self.send(b'api/test4', **kwargs)

    @prometheus.Registry.register('LocalTestJsonRestClient', '5', str)
    def test5(self, **kwargs):
        self.send(b'api/test5', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', '0')
    def off(self, **kwargs):
        self.send(b'api/red_led/off', **kwargs)

    @prometheus.Registry.register('LocalTestJsonRestClient', '7', str)
    def test7(self, **kwargs):
        self.send(b'api/test7', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', '1', str)
    def test1(self, **kwargs):
        self.send(b'api/test1', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', 'v', str)
    def value(self, **kwargs):
        self.send(b'api/dht11/value', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', '3', str)
    def test3(self, **kwargs):
        self.send(b'api/test3', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', 'v', str)
    def value(self, **kwargs):
        self.send(b'api/red_led/value', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', 't', str)
    def text(self, **kwargs):
        self.send(b'api/ssd/text', **kwargs)
        return self.resolve_response(self.recv(200))

    @prometheus.Registry.register('LocalTestJsonRestClient', '1')
    def on(self, **kwargs):
        self.send(b'api/red_led/on', **kwargs)

    @prometheus.Registry.register('LocalTestJsonRestClient', '0')
    def off(self, **kwargs):
        self.send(b'api/blue_led/off', **kwargs)

# endregion
