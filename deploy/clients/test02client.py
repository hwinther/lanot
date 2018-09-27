# coding=utf-8
# generated at 2018-09-28 00:40:18
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region Test02UdpClient
class Test02UdpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02UdpClientBlueLed', 'bv', str)
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Test02UdpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('Test02UdpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class Test02UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02UdpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('Test02UdpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('Test02UdpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class Test02UdpClientYellowLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02UdpClientYellowLed', 'y1')
    def on(self, **kwargs):
        self.send(b'y1', **kwargs)

    @prometheus.Registry.register('Test02UdpClientYellowLed', 'y0')
    def off(self, **kwargs):
        self.send(b'y0', **kwargs)

    @prometheus.Registry.register('Test02UdpClientYellowLed', 'yv', str)
    def value(self, **kwargs):
        self.send(b'yv', **kwargs)
        return self.recv(10)


class Test02UdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02UdpClientRedLed', 'rv', str)
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Test02UdpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('Test02UdpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class Test02UdpClientUwLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02UdpClientUwLed', 'uv', str)
    def value(self, **kwargs):
        self.send(b'uv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Test02UdpClientUwLed', 'u1')
    def on(self, **kwargs):
        self.send(b'u1', **kwargs)

    @prometheus.Registry.register('Test02UdpClientUwLed', 'u0')
    def off(self, **kwargs):
        self.send(b'u0', **kwargs)


class Test02UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02UdpClientLightsensor', 'sr', str)
    def read(self, **kwargs):
        self.send(b'sr', **kwargs)
        return self.recv(10)


class Test02UdpClientGreenLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02UdpClientGreenLed', 'gv', str)
    def value(self, **kwargs):
        self.send(b'gv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Test02UdpClientGreenLed', 'g1')
    def on(self, **kwargs):
        self.send(b'g1', **kwargs)

    @prometheus.Registry.register('Test02UdpClientGreenLed', 'g0')
    def off(self, **kwargs):
        self.send(b'g0', **kwargs)


class Test02UdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.blue_led = Test02UdpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.green_led = Test02UdpClientGreenLed(self.send, self.recv)
        self.register(green_led=self.green_led)
        self.integrated_led = Test02UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = Test02UdpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)
        self.red_led = Test02UdpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.uw_led = Test02UdpClientUwLed(self.send, self.recv)
        self.register(uw_led=self.uw_led)
        self.yellow_led = Test02UdpClientYellowLed(self.send, self.recv)
        self.register(yellow_led=self.yellow_led)

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
        return self.buffers[addr].pop().packet

    def recv(self, buffersize=10):
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


# endregion


# region Test02TcpClient
class Test02TcpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02TcpClientBlueLed', 'bv', str)
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Test02TcpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('Test02TcpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class Test02TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02TcpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('Test02TcpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('Test02TcpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class Test02TcpClientYellowLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02TcpClientYellowLed', 'y1')
    def on(self, **kwargs):
        self.send(b'y1', **kwargs)

    @prometheus.Registry.register('Test02TcpClientYellowLed', 'y0')
    def off(self, **kwargs):
        self.send(b'y0', **kwargs)

    @prometheus.Registry.register('Test02TcpClientYellowLed', 'yv', str)
    def value(self, **kwargs):
        self.send(b'yv', **kwargs)
        return self.recv(10)


class Test02TcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02TcpClientRedLed', 'rv', str)
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Test02TcpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('Test02TcpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class Test02TcpClientUwLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02TcpClientUwLed', 'uv', str)
    def value(self, **kwargs):
        self.send(b'uv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Test02TcpClientUwLed', 'u1')
    def on(self, **kwargs):
        self.send(b'u1', **kwargs)

    @prometheus.Registry.register('Test02TcpClientUwLed', 'u0')
    def off(self, **kwargs):
        self.send(b'u0', **kwargs)


class Test02TcpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02TcpClientLightsensor', 'sr', str)
    def read(self, **kwargs):
        self.send(b'sr', **kwargs)
        return self.recv(10)


class Test02TcpClientGreenLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test02TcpClientGreenLed', 'gv', str)
    def value(self, **kwargs):
        self.send(b'gv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Test02TcpClientGreenLed', 'g1')
    def on(self, **kwargs):
        self.send(b'g1', **kwargs)

    @prometheus.Registry.register('Test02TcpClientGreenLed', 'g0')
    def off(self, **kwargs):
        self.send(b'g0', **kwargs)


class Test02TcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        
        self.blue_led = Test02TcpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.green_led = Test02TcpClientGreenLed(self.send, self.recv)
        self.register(green_led=self.green_led)
        self.integrated_led = Test02TcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = Test02TcpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)
        self.red_led = Test02TcpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.uw_led = Test02TcpClientUwLed(self.send, self.recv)
        self.register(uw_led=self.uw_led)
        self.yellow_led = Test02TcpClientYellowLed(self.send, self.recv)
        self.register(yellow_led=self.yellow_led)

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
        return self.resolve_response(self.buffers[addr].pop().packet)


# endregion
