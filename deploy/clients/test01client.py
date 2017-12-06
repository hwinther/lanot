# generated at 2017-12-04 20:53:52
import prometheus
import socket
import machine
import time
import gc
import prometheus_crypto

gc.collect()


# region Test01UdpClient
class Test01UdpClientWindow01digital(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientWindow01digital', 'w1v', 'OUT')
    def value(self):
        self.send(b'w1v')
        return self.recv(10)


class Test01UdpClientWindow02digital(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientWindow02digital', 'w2v', 'OUT')
    def value(self):
        self.send(b'w2v')
        return self.recv(10)


class Test01UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('Test01UdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('Test01UdpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class Test01UdpClientLaser(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientLaser', 'lv', 'OUT')
    def value(self):
        self.send(b'lv')
        return self.recv(10)

    @prometheus.Registry.register('Test01UdpClientLaser', 'l0')
    def off(self):
        self.send(b'l0')

    @prometheus.Registry.register('Test01UdpClientLaser', 'l1')
    def on(self):
        self.send(b'l1')


class Test01UdpClient(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host='', bind_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((bind_host, bind_port))
        print('listening on %s:%d' % (bind_host, bind_port))
        self.socket.settimeout(0)
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.integrated_led = Test01UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.laser = Test01UdpClientLaser(self.send, self.recv)
        self.register(laser=self.laser)
        self.window01digital = Test01UdpClientWindow01digital(self.send, self.recv)
        self.register(window01digital=self.window01digital)
        self.window02digital = Test01UdpClientWindow02digital(self.send, self.recv)
        self.register(window02digital=self.window02digital)

    def send(self, data):
        self.socket.sendto(data + self.endChars + self.splitChars, self.remote_addr)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except:  # they said i could use OSError here, they lied (cpython/micropython issue, solve it later if necessary)
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


# region Test01TcpClient
class Test01TcpClientWindow01digital(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientWindow01digital', 'w1v', 'OUT')
    def value(self):
        self.send(b'w1v')
        return self.recv(10)


class Test01TcpClientWindow02digital(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientWindow02digital', 'w2v', 'OUT')
    def value(self):
        self.send(b'w2v')
        return self.recv(10)


class Test01TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('Test01TcpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('Test01TcpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class Test01TcpClientLaser(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientLaser', 'lv', 'OUT')
    def value(self):
        self.send(b'lv')
        return self.recv(10)

    @prometheus.Registry.register('Test01TcpClientLaser', 'l0')
    def off(self):
        self.send(b'l0')

    @prometheus.Registry.register('Test01TcpClientLaser', 'l1')
    def on(self):
        self.send(b'l1')


class Test01TcpClient(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.integrated_led = Test01TcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.laser = Test01TcpClientLaser(self.send, self.recv)
        self.register(laser=self.laser)
        self.window01digital = Test01TcpClientWindow01digital(self.send, self.recv)
        self.register(window01digital=self.window01digital)
        self.window02digital = Test01TcpClientWindow02digital(self.send, self.recv)
        self.register(window02digital=self.window02digital)

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.bind_host is not None:
            print('bound to %s:%d' % (self.bind_host, self.bind_port))
            self.socket.bind((self.bind_host, self.bind_port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(5)
        print('Connecting to %s' % repr(self.remote_addr))
        self.socket.connect(self.remote_addr)

    def send_once(self, data):
        self.socket.send(data + self.endChars + self.splitChars)

    def send(self, data):
        try:
            self.send_once(data)
        except:
            self.create_socket()
            self.send_once(data)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except:  # they said i could use OSError here, they lied (cpython/micropython issue, solve it later if necessary)
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
