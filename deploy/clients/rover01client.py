# generated at 2018-06-18 21:29:51
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region Rover01UdpClient
class Rover01UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Rover01UdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('Rover01UdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('Rover01UdpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class Rover01UdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.integrated_led = Rover01UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)

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

    @prometheus.Registry.register('Rover01UdpClient', 'A')
    def turn_left_fast(self):
        self.send(b'A')

    @prometheus.Registry.register('Rover01UdpClient', 'q')
    def strafe_left_forward_slow(self):
        self.send(b'q')

    @prometheus.Registry.register('Rover01UdpClient', 'C')
    def strafe_right_backward_fast(self):
        self.send(b'C')

    @prometheus.Registry.register('Rover01UdpClient', 'z')
    def strafe_left_backward_slow(self):
        self.send(b'z')

    @prometheus.Registry.register('Rover01UdpClient', 'E')
    def strafe_right_forward_fast(self):
        self.send(b'E')

    @prometheus.Registry.register('Rover01UdpClient', 'W')
    def fast_forward(self):
        self.send(b'W')

    @prometheus.Registry.register('Rover01UdpClient', 'g')
    def full_stop(self):
        self.send(b'g')

    @prometheus.Registry.register('Rover01UdpClient', 'c')
    def strafe_right_backward_slow(self):
        self.send(b'c')

    @prometheus.Registry.register('Rover01UdpClient', 'S')
    def fast_backward(self):
        self.send(b'S')

    @prometheus.Registry.register('Rover01UdpClient', 'd')
    def turn_right_slow(self):
        self.send(b'd')

    @prometheus.Registry.register('Rover01UdpClient', 'Q')
    def strafe_left_forward_fast(self):
        self.send(b'Q')

    @prometheus.Registry.register('Rover01UdpClient', 's')
    def slow_backward(self):
        self.send(b's')

    @prometheus.Registry.register('Rover01UdpClient', 'a')
    def turn_left_slow(self):
        self.send(b'a')

    @prometheus.Registry.register('Rover01UdpClient', 'w')
    def slow_forward(self):
        self.send(b'w')

    @prometheus.Registry.register('Rover01UdpClient', 'e')
    def strafe_right_forward_slow(self):
        self.send(b'e')

    @prometheus.Registry.register('Rover01UdpClient', 'Z')
    def strafe_left_backward_fast(self):
        self.send(b'Z')

    @prometheus.Registry.register('Rover01UdpClient', 'D')
    def turn_right_fast(self):
        self.send(b'D')

# endregion


# region Rover01TcpClient
class Rover01TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Rover01TcpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('Rover01TcpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('Rover01TcpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class Rover01TcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.integrated_led = Rover01TcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)

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
        if self.socket is None:
            self.create_socket()
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

    @prometheus.Registry.register('Rover01TcpClient', 'A')
    def turn_left_fast(self):
        self.send(b'A')

    @prometheus.Registry.register('Rover01TcpClient', 'q')
    def strafe_left_forward_slow(self):
        self.send(b'q')

    @prometheus.Registry.register('Rover01TcpClient', 'C')
    def strafe_right_backward_fast(self):
        self.send(b'C')

    @prometheus.Registry.register('Rover01TcpClient', 'z')
    def strafe_left_backward_slow(self):
        self.send(b'z')

    @prometheus.Registry.register('Rover01TcpClient', 'E')
    def strafe_right_forward_fast(self):
        self.send(b'E')

    @prometheus.Registry.register('Rover01TcpClient', 'W')
    def fast_forward(self):
        self.send(b'W')

    @prometheus.Registry.register('Rover01TcpClient', 'g')
    def full_stop(self):
        self.send(b'g')

    @prometheus.Registry.register('Rover01TcpClient', 'c')
    def strafe_right_backward_slow(self):
        self.send(b'c')

    @prometheus.Registry.register('Rover01TcpClient', 'S')
    def fast_backward(self):
        self.send(b'S')

    @prometheus.Registry.register('Rover01TcpClient', 'd')
    def turn_right_slow(self):
        self.send(b'd')

    @prometheus.Registry.register('Rover01TcpClient', 'Q')
    def strafe_left_forward_fast(self):
        self.send(b'Q')

    @prometheus.Registry.register('Rover01TcpClient', 's')
    def slow_backward(self):
        self.send(b's')

    @prometheus.Registry.register('Rover01TcpClient', 'a')
    def turn_left_slow(self):
        self.send(b'a')

    @prometheus.Registry.register('Rover01TcpClient', 'w')
    def slow_forward(self):
        self.send(b'w')

    @prometheus.Registry.register('Rover01TcpClient', 'e')
    def strafe_right_forward_slow(self):
        self.send(b'e')

    @prometheus.Registry.register('Rover01TcpClient', 'Z')
    def strafe_left_backward_fast(self):
        self.send(b'Z')

    @prometheus.Registry.register('Rover01TcpClient', 'D')
    def turn_right_fast(self):
        self.send(b'D')

# endregion
