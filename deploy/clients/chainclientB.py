# generated at 2018-07-03 00:00:29
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region BUdpClient
class BUdpClientBLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('BUdpClientBLed', 'blv', 'OUT')
    def value(self):
        self.send(b'blv')
        return self.recv(10)

    @prometheus.Registry.register('BUdpClientBLed', 'bl1')
    def on(self):
        self.send(b'bl1')

    @prometheus.Registry.register('BUdpClientBLed', 'bl0')
    def off(self):
        self.send(b'bl0')


class BUdpClientAObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.a_led = BUdpClientALed(self.send, self.recv)
        self.register(a_led=self.a_led)

    @prometheus.Registry.register('BUdpClientAObject', 'aT')
    def toggle(self):
        self.send(b'aT')


class BUdpClientALed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('BUdpClientALed', 'alv', 'OUT')
    def value(self):
        self.send(b'alv')
        return self.recv(10)

    @prometheus.Registry.register('BUdpClientALed', 'al0')
    def off(self):
        self.send(b'al0')

    @prometheus.Registry.register('BUdpClientALed', 'al1')
    def on(self):
        self.send(b'al1')


class BUdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.a_object = BUdpClientAObject(self.send, self.recv)
        self.register(a_object=self.a_object)
        self.b_led = BUdpClientBLed(self.send, self.recv)
        self.register(b_led=self.b_led)

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

    @prometheus.Registry.register('BUdpClient', 'T')
    def toggle(self):
        self.send(b'T')

# endregion


# region BTcpClient
class BTcpClientBLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('BTcpClientBLed', 'blv', 'OUT')
    def value(self):
        self.send(b'blv')
        return self.recv(10)

    @prometheus.Registry.register('BTcpClientBLed', 'bl1')
    def on(self):
        self.send(b'bl1')

    @prometheus.Registry.register('BTcpClientBLed', 'bl0')
    def off(self):
        self.send(b'bl0')


class BTcpClientAObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.a_led = BTcpClientALed(self.send, self.recv)
        self.register(a_led=self.a_led)

    @prometheus.Registry.register('BTcpClientAObject', 'aT')
    def toggle(self):
        self.send(b'aT')


class BTcpClientALed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('BTcpClientALed', 'alv', 'OUT')
    def value(self):
        self.send(b'alv')
        return self.recv(10)

    @prometheus.Registry.register('BTcpClientALed', 'al0')
    def off(self):
        self.send(b'al0')

    @prometheus.Registry.register('BTcpClientALed', 'al1')
    def on(self):
        self.send(b'al1')


class BTcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.a_object = BTcpClientAObject(self.send, self.recv)
        self.register(a_object=self.a_object)
        self.b_led = BTcpClientBLed(self.send, self.recv)
        self.register(b_led=self.b_led)

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

    @prometheus.Registry.register('BTcpClient', 'T')
    def toggle(self):
        self.send(b'T')

# endregion
