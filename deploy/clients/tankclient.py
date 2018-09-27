# coding=utf-8
# generated at 2018-09-27 23:51:44
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region TankUdpClient
class TankUdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankUdpClientRedLed', 'rv', 'OUT')
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('TankUdpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class TankUdpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankUdpClientBlueLed', 'bv', 'OUT')
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('TankUdpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class TankUdpClientLightControl(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankUdpClientLightControl', '1', 'OUT')
    def main_on(self, **kwargs):
        self.send(b'1', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientLightControl', '0', 'OUT')
    def all_off(self, **kwargs):
        self.send(b'0', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientLightControl', '3', 'OUT')
    def right_on(self, **kwargs):
        self.send(b'3', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientLightControl', '2', 'OUT')
    def left_on(self, **kwargs):
        self.send(b'2', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientLightControl', '5', 'OUT')
    def all_on(self, **kwargs):
        self.send(b'5', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientLightControl', '4', 'OUT')
    def front_on(self, **kwargs):
        self.send(b'4', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientLightControl', 'V', 'OUT')
    def version(self, **kwargs):
        self.send(b'V', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankUdpClientLightControl', '?', 'OUT')
    def capability(self, **kwargs):
        self.send(b'?', **kwargs)
        return self.recv(10)


class TankUdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.blue_led = TankUdpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.lightControl = TankUdpClientLightControl(self.send, self.recv)
        self.register(lightControl=self.lightControl)
        self.red_led = TankUdpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)

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

    @prometheus.Registry.register('TankUdpClient', 'A')
    def turn_left_fast(self, **kwargs):
        self.send(b'A', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 'a')
    def turn_left_slow(self, **kwargs):
        self.send(b'a', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 'b')
    def blink_lights(self, **kwargs):
        self.send(b'b', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 'W')
    def fast_forward(self, **kwargs):
        self.send(b'W', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 'g')
    def full_stop(self, **kwargs):
        self.send(b'g', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 'S')
    def fast_backward(self, **kwargs):
        self.send(b'S', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 'd')
    def turn_right_slow(self, **kwargs):
        self.send(b'd', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 's')
    def slow_backward(self, **kwargs):
        self.send(b's', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 'w')
    def slow_forward(self, **kwargs):
        self.send(b'w', **kwargs)

    @prometheus.Registry.register('TankUdpClient', 'D')
    def turn_right_fast(self, **kwargs):
        self.send(b'D', **kwargs)

# endregion


# region TankTcpClient
class TankTcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankTcpClientRedLed', 'rv', 'OUT')
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('TankTcpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class TankTcpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankTcpClientBlueLed', 'bv', 'OUT')
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('TankTcpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class TankTcpClientLightControl(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankTcpClientLightControl', '1', 'OUT')
    def main_on(self, **kwargs):
        self.send(b'1', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientLightControl', '0', 'OUT')
    def all_off(self, **kwargs):
        self.send(b'0', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientLightControl', '3', 'OUT')
    def right_on(self, **kwargs):
        self.send(b'3', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientLightControl', '2', 'OUT')
    def left_on(self, **kwargs):
        self.send(b'2', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientLightControl', '5', 'OUT')
    def all_on(self, **kwargs):
        self.send(b'5', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientLightControl', '4', 'OUT')
    def front_on(self, **kwargs):
        self.send(b'4', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientLightControl', 'V', 'OUT')
    def version(self, **kwargs):
        self.send(b'V', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('TankTcpClientLightControl', '?', 'OUT')
    def capability(self, **kwargs):
        self.send(b'?', **kwargs)
        return self.recv(10)


class TankTcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        
        self.blue_led = TankTcpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.lightControl = TankTcpClientLightControl(self.send, self.recv)
        self.register(lightControl=self.lightControl)
        self.red_led = TankTcpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)

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

    @prometheus.Registry.register('TankTcpClient', 'A')
    def turn_left_fast(self, **kwargs):
        self.send(b'A', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 'a')
    def turn_left_slow(self, **kwargs):
        self.send(b'a', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 'b')
    def blink_lights(self, **kwargs):
        self.send(b'b', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 'W')
    def fast_forward(self, **kwargs):
        self.send(b'W', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 'g')
    def full_stop(self, **kwargs):
        self.send(b'g', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 'S')
    def fast_backward(self, **kwargs):
        self.send(b'S', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 'd')
    def turn_right_slow(self, **kwargs):
        self.send(b'd', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 's')
    def slow_backward(self, **kwargs):
        self.send(b's', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 'w')
    def slow_forward(self, **kwargs):
        self.send(b'w', **kwargs)

    @prometheus.Registry.register('TankTcpClient', 'D')
    def turn_right_fast(self, **kwargs):
        self.send(b'D', **kwargs)

# endregion
