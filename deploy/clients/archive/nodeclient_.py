# generated at 2017-06-18 01:48:16
import prometheus
import socket
import machine


class RedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('RedLed', 'I')
    def on(self):
        self.send(b'I')

    @prometheus.Registry.register('RedLed', 'H')
    def off(self):
        self.send(b'H')

    @prometheus.Registry.register('RedLed', 'J', 'OUT')
    def state(self):
        self.send(b'J')
        return self.recv(4)


class Hygrometer(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Hygrometer', 'G', 'OUT')
    def read(self):
        self.send(b'G')
        return self.recv(4)


class BlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('BlueLed', 'A')
    def off(self):
        self.send(b'A')

    @prometheus.Registry.register('BlueLed', 'C', 'OUT')
    def state(self):
        self.send(b'C')
        return self.recv(4)

    @prometheus.Registry.register('BlueLed', 'B')
    def on(self):
        self.send(b'B')


class Dht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Dht11', 'E')
    def measure(self):
        self.send(b'E')

    @prometheus.Registry.register('Dht11', 'D', 'OUT')
    def humidity(self):
        self.send(b'D')
        return self.recv(4)

    @prometheus.Registry.register('Dht11', 'F', 'OUT')
    def temperature(self):
        self.send(b'F')
        return self.recv(4)


class NodeTestTcp(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, local_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', local_port))
        self.remote_addr = (remote_host, remote_port)
        self.socket.connect(self.remote_addr)
        
        self.red_led = RedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.hygrometer = Hygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.blue_led = BlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.dht11 = Dht11(self.send, self.recv)
        self.register(dht11=self.dht11)

    def send(self, data):
        self.socket.sendall(data)

    def recv(self, buffersize=10):
        return self.socket.recv(buffersize)


class NodeTestUdp(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, local_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', local_port))
        self.remote_addr = (remote_host, remote_port)
        
        self.red_led = RedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.hygrometer = Hygrometer(self.send, self.recv)
        self.register(hygrometer=self.hygrometer)
        self.blue_led = BlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.dht11 = Dht11(self.send, self.recv)
        self.register(dht11=self.dht11)

    def send(self, data):
        self.socket.sendto(data, self.remote_addr)

    def recv(self, buffersize=10):
        self.socket.setblocking(False)
        data, addr = self.socket.recvfrom(buffersize)
        self.socket.setblocking(True)
        return data

