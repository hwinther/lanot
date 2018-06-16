# generated at 2018-06-16 23:51:14
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
class LocalTestUdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientRedLed', 'rv', 'OUT')
    def value(self):
        self.send(b'rv')
        return self.recv(10)

    @prometheus.Registry.register('LocalTestUdpClientRedLed', 'r0')
    def off(self):
        self.send(b'r0')

    @prometheus.Registry.register('LocalTestUdpClientRedLed', 'r1')
    def on(self):
        self.send(b'r1')


class LocalTestUdpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientBlueLed', 'bv', 'OUT')
    def value(self):
        self.send(b'bv')
        return self.recv(10)

    @prometheus.Registry.register('LocalTestUdpClientBlueLed', 'b0')
    def off(self):
        self.send(b'b0')

    @prometheus.Registry.register('LocalTestUdpClientBlueLed', 'b1')
    def on(self):
        self.send(b'b1')


class LocalTestUdpClientHygrometer(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientHygrometer', 'hr', 'OUT')
    def read(self):
        self.send(b'hr')
        return self.recv(10)


class LocalTestUdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestUdpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('LocalTestUdpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('LocalTestUdpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('LocalTestUdpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


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
        self.hygrometer = LocalTestUdpClientHygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.red_led = LocalTestUdpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)

    def send(self, data):
        self.socket.sendto(data + self.endChars + self.splitChars, self.remote_addr)

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
        return self.buffers[addr].pop()

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


# region LocalTestTcpClient
class LocalTestTcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientRedLed', 'rv', 'OUT')
    def value(self):
        self.send(b'rv')
        return self.recv(10)

    @prometheus.Registry.register('LocalTestTcpClientRedLed', 'r0')
    def off(self):
        self.send(b'r0')

    @prometheus.Registry.register('LocalTestTcpClientRedLed', 'r1')
    def on(self):
        self.send(b'r1')


class LocalTestTcpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientBlueLed', 'bv', 'OUT')
    def value(self):
        self.send(b'bv')
        return self.recv(10)

    @prometheus.Registry.register('LocalTestTcpClientBlueLed', 'b0')
    def off(self):
        self.send(b'b0')

    @prometheus.Registry.register('LocalTestTcpClientBlueLed', 'b1')
    def on(self):
        self.send(b'b1')


class LocalTestTcpClientHygrometer(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientHygrometer', 'hr', 'OUT')
    def read(self):
        self.send(b'hr')
        return self.recv(10)


class LocalTestTcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LocalTestTcpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('LocalTestTcpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('LocalTestTcpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('LocalTestTcpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class LocalTestTcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.blue_led = LocalTestTcpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.dht11 = LocalTestTcpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.hygrometer = LocalTestTcpClientHygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.red_led = LocalTestTcpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.bind_host is not None:
            logging.notice('bound to %s:%d' % (self.bind_host, self.bind_port))
            self.socket.bind((self.bind_host, self.bind_port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(5)
        logging.info('Connecting to %s' % repr(self.remote_addr))
        self.socket.connect(self.remote_addr)

    def send_once(self, data):
        self.socket.send(data + self.endChars + self.splitChars)

    def send(self, data):
        try:
            self.send_once(data)
        except prometheus.psocket.socket_error:
            self.create_socket()
            self.send_once(data)

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
            self.buffers[addr] = prometheus.Buffer(split_chars=self.splitChars, end_chars=self.endChars)
        self.buffers[addr].parse(data)
        return self.buffers[addr].pop()


# endregion
