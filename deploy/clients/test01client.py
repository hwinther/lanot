# coding=utf-8
# generated at 2018-10-12 21:38:39
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region Test01UdpClient
class Test01UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('Test01UdpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('Test01UdpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv()


class Test01UdpClientLaser(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientLaser', 'lv', str)
    def value(self, **kwargs):
        self.send(b'lv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('Test01UdpClientLaser', 'l0')
    def off(self, **kwargs):
        self.send(b'l0', **kwargs)

    @prometheus.Registry.register('Test01UdpClientLaser', 'l1')
    def on(self, **kwargs):
        self.send(b'l1', **kwargs)


class Test01UdpClientJoysticky(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientJoysticky', 'yr', str)
    def read(self, **kwargs):
        self.send(b'yr', **kwargs)
        return self.recv()


class Test01UdpClientJoystickx(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientJoystickx', 'xr', str)
    def read(self, **kwargs):
        self.send(b'xr', **kwargs)
        return self.recv()


class Test01UdpClientSwitch(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientSwitch', 'sv', str)
    def value(self, **kwargs):
        self.send(b'sv', **kwargs)
        return self.recv()


class Test01UdpClientJoystickswitch(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientJoystickswitch', 'jv', str)
    def value(self, **kwargs):
        self.send(b'jv', **kwargs)
        return self.recv()


class Test01UdpClientWindow01digital(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientWindow01digital', 'w1v', str)
    def value(self, **kwargs):
        self.send(b'w1v', **kwargs)
        return self.recv()


class Test01UdpClientWindow02digital(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01UdpClientWindow02digital', 'w2v', str)
    def value(self, **kwargs):
        self.send(b'w2v', **kwargs)
        return self.recv()


class Test01UdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.integrated_led = Test01UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.joystickswitch = Test01UdpClientJoystickswitch(self.send, self.recv)
        self.register(joystickswitch=self.joystickswitch)
        self.joystickx = Test01UdpClientJoystickx(self.send, self.recv)
        self.register(joystickx=self.joystickx)
        self.joysticky = Test01UdpClientJoysticky(self.send, self.recv)
        self.register(joysticky=self.joysticky)
        self.laser = Test01UdpClientLaser(self.send, self.recv)
        self.register(laser=self.laser)
        self.switch = Test01UdpClientSwitch(self.send, self.recv)
        self.register(switch=self.switch)
        self.window01digital = Test01UdpClientWindow01digital(self.send, self.recv)
        self.register(window01digital=self.window01digital)
        self.window02digital = Test01UdpClientWindow02digital(self.send, self.recv)
        self.register(window02digital=self.window02digital)

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


# region Test01TcpClient
class Test01TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('Test01TcpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('Test01TcpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv()


class Test01TcpClientLaser(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientLaser', 'lv', str)
    def value(self, **kwargs):
        self.send(b'lv', **kwargs)
        return self.recv()

    @prometheus.Registry.register('Test01TcpClientLaser', 'l0')
    def off(self, **kwargs):
        self.send(b'l0', **kwargs)

    @prometheus.Registry.register('Test01TcpClientLaser', 'l1')
    def on(self, **kwargs):
        self.send(b'l1', **kwargs)


class Test01TcpClientJoysticky(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientJoysticky', 'yr', str)
    def read(self, **kwargs):
        self.send(b'yr', **kwargs)
        return self.recv()


class Test01TcpClientJoystickx(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientJoystickx', 'xr', str)
    def read(self, **kwargs):
        self.send(b'xr', **kwargs)
        return self.recv()


class Test01TcpClientSwitch(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientSwitch', 'sv', str)
    def value(self, **kwargs):
        self.send(b'sv', **kwargs)
        return self.recv()


class Test01TcpClientJoystickswitch(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientJoystickswitch', 'jv', str)
    def value(self, **kwargs):
        self.send(b'jv', **kwargs)
        return self.recv()


class Test01TcpClientWindow01digital(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientWindow01digital', 'w1v', str)
    def value(self, **kwargs):
        self.send(b'w1v', **kwargs)
        return self.recv()


class Test01TcpClientWindow02digital(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Test01TcpClientWindow02digital', 'w2v', str)
    def value(self, **kwargs):
        self.send(b'w2v', **kwargs)
        return self.recv()


class Test01TcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        
        self.integrated_led = Test01TcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.joystickswitch = Test01TcpClientJoystickswitch(self.send, self.recv)
        self.register(joystickswitch=self.joystickswitch)
        self.joystickx = Test01TcpClientJoystickx(self.send, self.recv)
        self.register(joystickx=self.joystickx)
        self.joysticky = Test01TcpClientJoysticky(self.send, self.recv)
        self.register(joysticky=self.joysticky)
        self.laser = Test01TcpClientLaser(self.send, self.recv)
        self.register(laser=self.laser)
        self.switch = Test01TcpClientSwitch(self.send, self.recv)
        self.register(switch=self.switch)
        self.window01digital = Test01TcpClientWindow01digital(self.send, self.recv)
        self.register(window01digital=self.window01digital)
        self.window02digital = Test01TcpClientWindow02digital(self.send, self.recv)
        self.register(window02digital=self.window02digital)

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
