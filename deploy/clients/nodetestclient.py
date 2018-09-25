# coding=utf-8
# generated at 2018-09-24 23:41:05
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region NodeTestUdpClient
class NodeTestUdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('NodeTestUdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('NodeTestUdpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class NodeTestUdpClientAds(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientAds', 'adv', 'OUT')
    def read(self):
        self.send(b'adv')
        return self.recv(10)


class NodeTestUdpClientNano(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientNano', 'nadi', 'OUT')
    def digital_in(self):
        self.send(b'nadi')
        return self.recv(10)

    @prometheus.Registry.register('NodeTestUdpClientNano', 'naio')
    def infraout(self):
        self.send(b'naio')

    @prometheus.Registry.register('NodeTestUdpClientNano', 'nado')
    def digital_out(self):
        self.send(b'nado')

    @prometheus.Registry.register('NodeTestUdpClientNano', 'naii', 'OUT')
    def infrain(self):
        self.send(b'naii')
        return self.recv(10)


class NodeTestUdpClientDs1307(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientDs1307', 'dsv', 'OUT')
    def value(self):
        self.send(b'dsv')
        return self.recv(10)


class NodeTestUdpClientNeopixel(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv



class NodeTestUdpClientAdc1(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientAdc1', 'ar', 'OUT')
    def read(self):
        self.send(b'ar')
        return self.recv(10)


class NodeTestUdpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientDsb', 'sv', 'OUT')
    def value(self):
        self.send(b'sv')
        return self.recv(10)


class NodeTestUdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('NodeTestUdpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('NodeTestUdpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('NodeTestUdpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class NodeTestUdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.adc1 = NodeTestUdpClientAdc1(self.send, self.recv)
        self.register(adc1=self.adc1)
        self.ads = NodeTestUdpClientAds(self.send, self.recv)
        self.register(ads=self.ads)
        self.dht11 = NodeTestUdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.ds1307 = NodeTestUdpClientDs1307(self.send, self.recv)
        self.register(ds1307=self.ds1307)
        self.dsb = NodeTestUdpClientDsb(self.send, self.recv)
        self.register(dsb=self.dsb)
        self.integrated_led = NodeTestUdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.nano = NodeTestUdpClientNano(self.send, self.recv)
        self.register(nano=self.nano)
        self.neopixel = NodeTestUdpClientNeopixel(self.send, self.recv)
        self.register(neopixel=self.neopixel)

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


# region NodeTestTcpClient
class NodeTestTcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('NodeTestTcpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('NodeTestTcpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class NodeTestTcpClientAds(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientAds', 'adv', 'OUT')
    def read(self):
        self.send(b'adv')
        return self.recv(10)


class NodeTestTcpClientNano(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientNano', 'nadi', 'OUT')
    def digital_in(self):
        self.send(b'nadi')
        return self.recv(10)

    @prometheus.Registry.register('NodeTestTcpClientNano', 'naio')
    def infraout(self):
        self.send(b'naio')

    @prometheus.Registry.register('NodeTestTcpClientNano', 'nado')
    def digital_out(self):
        self.send(b'nado')

    @prometheus.Registry.register('NodeTestTcpClientNano', 'naii', 'OUT')
    def infrain(self):
        self.send(b'naii')
        return self.recv(10)


class NodeTestTcpClientDs1307(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientDs1307', 'dsv', 'OUT')
    def value(self):
        self.send(b'dsv')
        return self.recv(10)


class NodeTestTcpClientNeopixel(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv



class NodeTestTcpClientAdc1(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientAdc1', 'ar', 'OUT')
    def read(self):
        self.send(b'ar')
        return self.recv(10)


class NodeTestTcpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientDsb', 'sv', 'OUT')
    def value(self):
        self.send(b'sv')
        return self.recv(10)


class NodeTestTcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('NodeTestTcpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('NodeTestTcpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('NodeTestTcpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class NodeTestTcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        
        self.adc1 = NodeTestTcpClientAdc1(self.send, self.recv)
        self.register(adc1=self.adc1)
        self.ads = NodeTestTcpClientAds(self.send, self.recv)
        self.register(ads=self.ads)
        self.dht11 = NodeTestTcpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.ds1307 = NodeTestTcpClientDs1307(self.send, self.recv)
        self.register(ds1307=self.ds1307)
        self.dsb = NodeTestTcpClientDsb(self.send, self.recv)
        self.register(dsb=self.dsb)
        self.integrated_led = NodeTestTcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.nano = NodeTestTcpClientNano(self.send, self.recv)
        self.register(nano=self.nano)
        self.neopixel = NodeTestTcpClientNeopixel(self.send, self.recv)
        self.register(neopixel=self.neopixel)

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
        self.socket.send(data + self.end_chars + self.split_chars)

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
            self.buffers[addr] = prometheus.Buffer(split_chars=self.split_chars, end_chars=self.end_chars)
        self.buffers[addr].parse(data)
        return self.buffers[addr].pop()


# endregion
