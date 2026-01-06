# generated at 2017-06-18 23:11:22
import prometheus
import socket
import machine


class ALed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ALed', 'A')
    def off(self):
        self.send(b'A')

    @prometheus.Registry.register('ALed', 'C', 'OUT')
    def state(self):
        self.send(b'C')
        return self.recv(4)

    @prometheus.Registry.register('ALed', 'B')
    def on(self):
        self.send(b'B')


class BLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('BLed', 'E')
    def off(self):
        self.send(b'E')

    @prometheus.Registry.register('BLed', 'G', 'OUT')
    def state(self):
        self.send(b'G')
        return self.recv(4)

    @prometheus.Registry.register('BLed', 'F')
    def on(self):
        self.send(b'F')


class AObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('AObject', 'D')
    def toggle(self):
        self.send(b'D')


class BUdp(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, local_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', local_port))
        self.remote_addr = (remote_host, remote_port)
        
        self.a_led = ALed(self.send, self.recv)
        self.register(a_led=self.a_led)
        self.b_led = BLed(self.send, self.recv)
        self.register(b_led=self.b_led)
        self.a_object = AObject(self.send, self.recv)
        self.register(a_object=self.a_object)

    def send(self, data):
        self.socket.sendto(data, self.remote_addr)

    def recv(self, buffersize=10):
        self.socket.setblocking(False)
        data, addr = self.socket.recvfrom(buffersize)
        self.socket.setblocking(True)
        return data


    @prometheus.Registry.register('BUdp', 'H')
    def toggle(self):
        self.send(b'H')


