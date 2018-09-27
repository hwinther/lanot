# coding=utf-8
# generated at 2018-09-27 23:51:45
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region TankProxyUdpClient
class TankProxyUdpClientTankclient(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.blue_led = TankProxyUdpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.lightControl = TankProxyUdpClientLightControl(self.send, self.recv)
        self.register(lightControl=self.lightControl)
        self.red_led = TankProxyUdpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tW')
    def fast_forward(self, **kwargs):
        self.send(b'tW', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tS')
    def fast_backward(self, **kwargs):
        self.send(b'tS', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'ts')
    def slow_backward(self, **kwargs):
        self.send(b'ts', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tw')
    def slow_forward(self, **kwargs):
        self.send(b'tw', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tg')
    def full_stop(self, **kwargs):
        self.send(b'tg', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tD')
    def turn_right_fast(self, **kwargs):
        self.send(b'tD', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'ta')
    def turn_left_slow(self, **kwargs):
        self.send(b'ta', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tb')
    def blink_lights(self, **kwargs):
        self.send(b'tb', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'td')
    def turn_right_slow(self, **kwargs):
        self.send(b'td', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tA')
    def turn_left_fast(self, **kwargs):
        self.send(b'tA', **kwargs)


class TankProxyUdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyUdpClientRedLed', 'rv', 'OUT')
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class TankProxyUdpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyUdpClientBlueLed', 'bv', 'OUT')
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('TankProxyUdpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class TankProxyUdpClientLightControl(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '1', 'OUT')
    def main_on(self, **kwargs):
        self.send(b'1', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '0', 'OUT')
    def all_off(self, **kwargs):
        self.send(b'0', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '3', 'OUT')
    def right_on(self, **kwargs):
        self.send(b'3', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '2', 'OUT')
    def left_on(self, **kwargs):
        self.send(b'2', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '5', 'OUT')
    def all_on(self, **kwargs):
        self.send(b'5', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '4', 'OUT')
    def front_on(self, **kwargs):
        self.send(b'4', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', 'V', 'OUT')
    def version(self, **kwargs):
        self.send(b'V', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '?', 'OUT')
    def capability(self, **kwargs):
        self.send(b'?', **kwargs)
        return self.recv(10)


class TankProxyUdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.tankclient = TankProxyUdpClientTankclient(self.send, self.recv)
        self.register(tankclient=self.tankclient)

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


# region TankProxyTcpClient
class TankProxyTcpClientTankclient(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.blue_led = TankProxyTcpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.lightControl = TankProxyTcpClientLightControl(self.send, self.recv)
        self.register(lightControl=self.lightControl)
        self.red_led = TankProxyTcpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tW')
    def fast_forward(self, **kwargs):
        self.send(b'tW', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tS')
    def fast_backward(self, **kwargs):
        self.send(b'tS', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'ts')
    def slow_backward(self, **kwargs):
        self.send(b'ts', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tw')
    def slow_forward(self, **kwargs):
        self.send(b'tw', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tg')
    def full_stop(self, **kwargs):
        self.send(b'tg', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tD')
    def turn_right_fast(self, **kwargs):
        self.send(b'tD', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'ta')
    def turn_left_slow(self, **kwargs):
        self.send(b'ta', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tb')
    def blink_lights(self, **kwargs):
        self.send(b'tb', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'td')
    def turn_right_slow(self, **kwargs):
        self.send(b'td', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tA')
    def turn_left_fast(self, **kwargs):
        self.send(b'tA', **kwargs)


class TankProxyTcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyTcpClientRedLed', 'rv', 'OUT')
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class TankProxyTcpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyTcpClientBlueLed', 'bv', 'OUT')
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('TankProxyTcpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class TankProxyTcpClientLightControl(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '1', 'OUT')
    def main_on(self, **kwargs):
        self.send(b'1', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '0', 'OUT')
    def all_off(self, **kwargs):
        self.send(b'0', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '3', 'OUT')
    def right_on(self, **kwargs):
        self.send(b'3', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '2', 'OUT')
    def left_on(self, **kwargs):
        self.send(b'2', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '5', 'OUT')
    def all_on(self, **kwargs):
        self.send(b'5', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '4', 'OUT')
    def front_on(self, **kwargs):
        self.send(b'4', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', 'V', 'OUT')
    def version(self, **kwargs):
        self.send(b'V', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '?', 'OUT')
    def capability(self, **kwargs):
        self.send(b'?', **kwargs)
        return self.recv(10)


class TankProxyTcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        
        self.tankclient = TankProxyTcpClientTankclient(self.send, self.recv)
        self.register(tankclient=self.tankclient)

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
        return self.resolve_response(self.buffers[addr].pop().packet)


# endregion
