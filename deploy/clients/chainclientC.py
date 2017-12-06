# generated at 2017-09-10 00:20:33
import prometheus
import socket
import machine
import time
import gc
import prometheus_crypto

gc.collect()


class CUdpClientCLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CUdpClientCLed', 'cl0')
    def off(self):
        self.send(b'cl0')

    @prometheus.Registry.register('CUdpClientCLed', 'cl1')
    def on(self):
        self.send(b'cl1')

    @prometheus.Registry.register('CUdpClientCLed', 'clS', 'OUT')
    def state(self):
        self.send(b'clS')
        return self.recv(10)


class CUdpClientBObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.a_object = CUdpClientAObject(self.send, self.recv)
        self.register(a_object=self.a_object)
        self.b_led = CUdpClientBLed(self.send, self.recv)
        self.register(b_led=self.b_led)

    @prometheus.Registry.register('CUdpClientBObject', 'bT')
    def toggle(self):
        self.send(b'bT')


class CUdpClientBLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CUdpClientBLed', 'bl0')
    def off(self):
        self.send(b'bl0')

    @prometheus.Registry.register('CUdpClientBLed', 'bl1')
    def on(self):
        self.send(b'bl1')

    @prometheus.Registry.register('CUdpClientBLed', 'blS', 'OUT')
    def state(self):
        self.send(b'blS')
        return self.recv(10)


class CUdpClientAObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.a_led = CUdpClientALed(self.send, self.recv)
        self.register(a_led=self.a_led)

    @prometheus.Registry.register('CUdpClientAObject', 'aT')
    def toggle(self):
        self.send(b'aT')


class CUdpClientALed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CUdpClientALed', 'al0')
    def off(self):
        self.send(b'al0')

    @prometheus.Registry.register('CUdpClientALed', 'al1')
    def on(self):
        self.send(b'al1')

    @prometheus.Registry.register('CUdpClientALed', 'alS', 'OUT')
    def state(self):
        self.send(b'alS')
        return self.recv(10)


class CUdpClient(prometheus.RemoteTemplate):
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
        
        self.b_object = CUdpClientBObject(self.send, self.recv)
        self.register(b_object=self.b_object)
        self.c_led = CUdpClientCLed(self.send, self.recv)
        self.register(c_led=self.c_led)

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

    @prometheus.Registry.register('CUdpClient', 'T')
    def toggle(self):
        self.send(b'T')


class CTcpClientCLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CTcpClientCLed', 'cl0')
    def off(self):
        self.send(b'cl0')

    @prometheus.Registry.register('CTcpClientCLed', 'cl1')
    def on(self):
        self.send(b'cl1')

    @prometheus.Registry.register('CTcpClientCLed', 'clS', 'OUT')
    def state(self):
        self.send(b'clS')
        return self.recv(10)


class CTcpClientBObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.a_object = CTcpClientAObject(self.send, self.recv)
        self.register(a_object=self.a_object)
        self.b_led = CTcpClientBLed(self.send, self.recv)
        self.register(b_led=self.b_led)

    @prometheus.Registry.register('CTcpClientBObject', 'bT')
    def toggle(self):
        self.send(b'bT')


class CTcpClientBLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CTcpClientBLed', 'bl0')
    def off(self):
        self.send(b'bl0')

    @prometheus.Registry.register('CTcpClientBLed', 'bl1')
    def on(self):
        self.send(b'bl1')

    @prometheus.Registry.register('CTcpClientBLed', 'blS', 'OUT')
    def state(self):
        self.send(b'blS')
        return self.recv(10)


class CTcpClientAObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.a_led = CTcpClientALed(self.send, self.recv)
        self.register(a_led=self.a_led)

    @prometheus.Registry.register('CTcpClientAObject', 'aT')
    def toggle(self):
        self.send(b'aT')


class CTcpClientALed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CTcpClientALed', 'al0')
    def off(self):
        self.send(b'al0')

    @prometheus.Registry.register('CTcpClientALed', 'al1')
    def on(self):
        self.send(b'al1')

    @prometheus.Registry.register('CTcpClientALed', 'alS', 'OUT')
    def state(self):
        self.send(b'alS')
        return self.recv(10)


class CTcpClient(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.b_object = CTcpClientBObject(self.send, self.recv)
        self.register(b_object=self.b_object)
        self.c_led = CTcpClientCLed(self.send, self.recv)
        self.register(c_led=self.c_led)

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

    @prometheus.Registry.register('CTcpClient', 'T')
    def toggle(self):
        self.send(b'T')