# coding=utf-8
# generated at 2018-10-12 21:38:38
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
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('NodeTestUdpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('NodeTestUdpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv()


class NodeTestUdpClientAds(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientAds', 'adv', str)
    def read(self, **kwargs):
        self.send(b'adv', **kwargs)
        return self.recv()


class NodeTestUdpClientNano(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientNano', 'nadi', str)
    def digital_in(self, **kwargs):
        self.send(b'nadi', **kwargs)
        return self.recv()

    @prometheus.Registry.register('NodeTestUdpClientNano', 'naio')
    def infraout(self, **kwargs):
        self.send(b'naio', **kwargs)

    @prometheus.Registry.register('NodeTestUdpClientNano', 'nado')
    def digital_out(self, **kwargs):
        self.send(b'nado', **kwargs)

    @prometheus.Registry.register('NodeTestUdpClientNano', 'naii', str)
    def infrain(self, **kwargs):
        self.send(b'naii', **kwargs)
        return self.recv()


class NodeTestUdpClientMax(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientMax', 'mab', str)
    def brightness(self, **kwargs):
        self.send(b'mab', **kwargs)
        return self.recv()

    @prometheus.Registry.register('NodeTestUdpClientMax', 'mat', str)
    def text(self, **kwargs):
        self.send(b'mat', **kwargs)
        return self.recv()


class NodeTestUdpClientNeopixel(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientNeopixel', 'ps')
    def set(self, **kwargs):
        self.send(b'ps', **kwargs)

    @prometheus.Registry.register('NodeTestUdpClientNeopixel', 'psp')
    def set_pixel(self, **kwargs):
        self.send(b'psp', **kwargs)

    @prometheus.Registry.register('NodeTestUdpClientNeopixel', 'pwr')
    def write(self, **kwargs):
        self.send(b'pwr', **kwargs)


class NodeTestUdpClientDs1307(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientDs1307', 'dsv', str)
    def value(self, **kwargs):
        self.send(b'dsv', **kwargs)
        return self.recv()


class NodeTestUdpClientAdc1(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientAdc1', 'ar', str)
    def read(self, **kwargs):
        self.send(b'ar', **kwargs)
        return self.recv()


class NodeTestUdpClientSsd(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientSsd', 'sst', str)
    def text(self, **kwargs):
        self.send(b'sst', **kwargs)
        return self.recv()


class NodeTestUdpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientDsb', 'sv', str)
    def value(self, **kwargs):
        self.send(b'sv', **kwargs)
        return self.recv()


class NodeTestUdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestUdpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('NodeTestUdpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv()

    @prometheus.Registry.register('NodeTestUdpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('NodeTestUdpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
        return self.recv()


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
        self.max = NodeTestUdpClientMax(self.send, self.recv)
        self.register(max=self.max)
        self.nano = NodeTestUdpClientNano(self.send, self.recv)
        self.register(nano=self.nano)
        self.neopixel = NodeTestUdpClientNeopixel(self.send, self.recv)
        self.register(neopixel=self.neopixel)
        self.ssd = NodeTestUdpClientSsd(self.send, self.recv)
        self.register(ssd=self.ssd)

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
        bufferpacket = self.buffers[addr].pop()
        if bufferpacket is None:
            return None
        return bufferpacket.packet

    def recv(self, buffersize=20):
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
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('NodeTestTcpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('NodeTestTcpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv()


class NodeTestTcpClientAds(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientAds', 'adv', str)
    def read(self, **kwargs):
        self.send(b'adv', **kwargs)
        return self.recv()


class NodeTestTcpClientNano(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientNano', 'nadi', str)
    def digital_in(self, **kwargs):
        self.send(b'nadi', **kwargs)
        return self.recv()

    @prometheus.Registry.register('NodeTestTcpClientNano', 'naio')
    def infraout(self, **kwargs):
        self.send(b'naio', **kwargs)

    @prometheus.Registry.register('NodeTestTcpClientNano', 'nado')
    def digital_out(self, **kwargs):
        self.send(b'nado', **kwargs)

    @prometheus.Registry.register('NodeTestTcpClientNano', 'naii', str)
    def infrain(self, **kwargs):
        self.send(b'naii', **kwargs)
        return self.recv()


class NodeTestTcpClientMax(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientMax', 'mab', str)
    def brightness(self, **kwargs):
        self.send(b'mab', **kwargs)
        return self.recv()

    @prometheus.Registry.register('NodeTestTcpClientMax', 'mat', str)
    def text(self, **kwargs):
        self.send(b'mat', **kwargs)
        return self.recv()


class NodeTestTcpClientNeopixel(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientNeopixel', 'ps')
    def set(self, **kwargs):
        self.send(b'ps', **kwargs)

    @prometheus.Registry.register('NodeTestTcpClientNeopixel', 'psp')
    def set_pixel(self, **kwargs):
        self.send(b'psp', **kwargs)

    @prometheus.Registry.register('NodeTestTcpClientNeopixel', 'pwr')
    def write(self, **kwargs):
        self.send(b'pwr', **kwargs)


class NodeTestTcpClientDs1307(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientDs1307', 'dsv', str)
    def value(self, **kwargs):
        self.send(b'dsv', **kwargs)
        return self.recv()


class NodeTestTcpClientAdc1(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientAdc1', 'ar', str)
    def read(self, **kwargs):
        self.send(b'ar', **kwargs)
        return self.recv()


class NodeTestTcpClientSsd(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientSsd', 'sst', str)
    def text(self, **kwargs):
        self.send(b'sst', **kwargs)
        return self.recv()


class NodeTestTcpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientDsb', 'sv', str)
    def value(self, **kwargs):
        self.send(b'sv', **kwargs)
        return self.recv()


class NodeTestTcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('NodeTestTcpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('NodeTestTcpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv()

    @prometheus.Registry.register('NodeTestTcpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('NodeTestTcpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
        return self.recv()


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
        self.max = NodeTestTcpClientMax(self.send, self.recv)
        self.register(max=self.max)
        self.nano = NodeTestTcpClientNano(self.send, self.recv)
        self.register(nano=self.nano)
        self.neopixel = NodeTestTcpClientNeopixel(self.send, self.recv)
        self.register(neopixel=self.neopixel)
        self.ssd = NodeTestTcpClientSsd(self.send, self.recv)
        self.register(ssd=self.ssd)

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
        bufferpacket = self.buffers[addr].pop()
        if bufferpacket is None:
            return None
        return bufferpacket.packet


# endregion
