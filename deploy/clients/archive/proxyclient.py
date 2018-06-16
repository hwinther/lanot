# generated at 2017-09-10 00:20:33
import prometheus
import socket
import machine
import time
import gc
import prometheus_crypto

gc.collect()


class ProxyTestUdpClientNodeclient(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.blue_led = ProxyTestUdpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.dht11 = ProxyTestUdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.hygrometer = ProxyTestUdpClientHygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.red_led = ProxyTestUdpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)



class ProxyTestUdpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTestUdpClientBlueLed', 'b0')
    def off(self):
        self.send(b'b0')

    @prometheus.Registry.register('ProxyTestUdpClientBlueLed', 'b1')
    def on(self):
        self.send(b'b1')

    @prometheus.Registry.register('ProxyTestUdpClientBlueLed', 'bS', 'OUT')
    def state(self):
        self.send(b'bS')
        return self.recv(10)


class ProxyTestUdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTestUdpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTestUdpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('ProxyTestUdpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)


class ProxyTestUdpClientHygrometer(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTestUdpClientHygrometer', 'hr', 'OUT')
    def read(self):
        self.send(b'hr')
        return self.recv(10)


class ProxyTestUdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTestUdpClientRedLed', 'r0')
    def off(self):
        self.send(b'r0')

    @prometheus.Registry.register('ProxyTestUdpClientRedLed', 'r1')
    def on(self):
        self.send(b'r1')

    @prometheus.Registry.register('ProxyTestUdpClientRedLed', 'rS', 'OUT')
    def state(self):
        self.send(b'rS')
        return self.recv(10)


class ProxyTestUdpClient(prometheus.RemoteTemplate):
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
        
        self.nodeclient = ProxyTestUdpClientNodeclient(self.send, self.recv)
        self.register(nodeclient=self.nodeclient)

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



class ProxyTestTcpClientNodeclient(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.blue_led = ProxyTestTcpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.dht11 = ProxyTestTcpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.hygrometer = ProxyTestTcpClientHygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.red_led = ProxyTestTcpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)



class ProxyTestTcpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTestTcpClientBlueLed', 'b0')
    def off(self):
        self.send(b'b0')

    @prometheus.Registry.register('ProxyTestTcpClientBlueLed', 'b1')
    def on(self):
        self.send(b'b1')

    @prometheus.Registry.register('ProxyTestTcpClientBlueLed', 'bS', 'OUT')
    def state(self):
        self.send(b'bS')
        return self.recv(10)


class ProxyTestTcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTestTcpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTestTcpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('ProxyTestTcpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)


class ProxyTestTcpClientHygrometer(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTestTcpClientHygrometer', 'hr', 'OUT')
    def read(self):
        self.send(b'hr')
        return self.recv(10)


class ProxyTestTcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTestTcpClientRedLed', 'r0')
    def off(self):
        self.send(b'r0')

    @prometheus.Registry.register('ProxyTestTcpClientRedLed', 'r1')
    def on(self):
        self.send(b'r1')

    @prometheus.Registry.register('ProxyTestTcpClientRedLed', 'rS', 'OUT')
    def state(self):
        self.send(b'rS')
        return self.recv(10)


class ProxyTestTcpClient(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.nodeclient = ProxyTestTcpClientNodeclient(self.send, self.recv)
        self.register(nodeclient=self.nodeclient)

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

