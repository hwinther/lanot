# coding=utf-8
# generated at 2018-10-12 21:38:33
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region CUdpClient
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
    def toggle(self, **kwargs):
        self.send(b'bT', **kwargs)


class CUdpClientBLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CUdpClientBLed', 'blv', str)
    def value(self, **kwargs):
        self.send(b'blv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('CUdpClientBLed', 'bl1')
    def on(self, **kwargs):
        self.send(b'bl1', **kwargs)

    @prometheus.Registry.register('CUdpClientBLed', 'bl0')
    def off(self, **kwargs):
        self.send(b'bl0', **kwargs)


class CUdpClientAObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.a_led = CUdpClientALed(self.send, self.recv)
        self.register(a_led=self.a_led)

    @prometheus.Registry.register('CUdpClientAObject', 'aT')
    def toggle(self, **kwargs):
        self.send(b'aT', **kwargs)


class CUdpClientALed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CUdpClientALed', 'alv', str)
    def value(self, **kwargs):
        self.send(b'alv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('CUdpClientALed', 'al0')
    def off(self, **kwargs):
        self.send(b'al0', **kwargs)

    @prometheus.Registry.register('CUdpClientALed', 'al1')
    def on(self, **kwargs):
        self.send(b'al1', **kwargs)


class CUdpClientCLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CUdpClientCLed', 'clv', str)
    def value(self, **kwargs):
        self.send(b'clv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('CUdpClientCLed', 'cl0')
    def off(self, **kwargs):
        self.send(b'cl0', **kwargs)

    @prometheus.Registry.register('CUdpClientCLed', 'cl1')
    def on(self, **kwargs):
        self.send(b'cl1', **kwargs)


class CUdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.b_object = CUdpClientBObject(self.send, self.recv)
        self.register(b_object=self.b_object)
        self.c_led = CUdpClientCLed(self.send, self.recv)
        self.register(c_led=self.c_led)

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

    @prometheus.Registry.register('CUdpClient', 'T')
    def toggle(self, **kwargs):
        self.send(b'T', **kwargs)

# endregion


# region CTcpClient
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
    def toggle(self, **kwargs):
        self.send(b'bT', **kwargs)


class CTcpClientBLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CTcpClientBLed', 'blv', str)
    def value(self, **kwargs):
        self.send(b'blv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('CTcpClientBLed', 'bl1')
    def on(self, **kwargs):
        self.send(b'bl1', **kwargs)

    @prometheus.Registry.register('CTcpClientBLed', 'bl0')
    def off(self, **kwargs):
        self.send(b'bl0', **kwargs)


class CTcpClientAObject(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.a_led = CTcpClientALed(self.send, self.recv)
        self.register(a_led=self.a_led)

    @prometheus.Registry.register('CTcpClientAObject', 'aT')
    def toggle(self, **kwargs):
        self.send(b'aT', **kwargs)


class CTcpClientALed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CTcpClientALed', 'alv', str)
    def value(self, **kwargs):
        self.send(b'alv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('CTcpClientALed', 'al0')
    def off(self, **kwargs):
        self.send(b'al0', **kwargs)

    @prometheus.Registry.register('CTcpClientALed', 'al1')
    def on(self, **kwargs):
        self.send(b'al1', **kwargs)


class CTcpClientCLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('CTcpClientCLed', 'clv', str)
    def value(self, **kwargs):
        self.send(b'clv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('CTcpClientCLed', 'cl0')
    def off(self, **kwargs):
        self.send(b'cl0', **kwargs)

    @prometheus.Registry.register('CTcpClientCLed', 'cl1')
    def on(self, **kwargs):
        self.send(b'cl1', **kwargs)


class CTcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        
        self.b_object = CTcpClientBObject(self.send, self.recv)
        self.register(b_object=self.b_object)
        self.c_led = CTcpClientCLed(self.send, self.recv)
        self.register(c_led=self.c_led)

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

    @prometheus.Registry.register('CTcpClient', 'T')
    def toggle(self, **kwargs):
        self.send(b'T', **kwargs)

# endregion
