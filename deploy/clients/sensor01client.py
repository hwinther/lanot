# coding=utf-8
# generated at 2018-09-28 00:40:15
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region Sensor01UdpClient
class Sensor01UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01UdpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('Sensor01UdpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('Sensor01UdpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class Sensor01UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01UdpClientLightsensor', 'lr', str)
    def read(self, **kwargs):
        self.send(b'lr', **kwargs)
        return self.recv(10)


class Sensor01UdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01UdpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Sensor01UdpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('Sensor01UdpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('Sensor01UdpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
        return self.recv(10)


class Sensor01UdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.dht11 = Sensor01UdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.integrated_led = Sensor01UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = Sensor01UdpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)

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
        return self.buffers[addr].pop().packet

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
