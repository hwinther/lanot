# generated at 2017-09-10 00:20:33
import prometheus
import socket
import machine
import time
import gc
import prometheus_crypto

gc.collect()


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

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tb')
    def blink_lights(self):
        self.send(b'tb')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tS')
    def fast_backward(self):
        self.send(b'tS')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tW')
    def fast_forward(self):
        self.send(b'tW')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tg')
    def full_stop(self):
        self.send(b'tg')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'ts')
    def slow_backward(self):
        self.send(b'ts')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tw')
    def slow_forward(self):
        self.send(b'tw')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tA')
    def turn_left_fast(self):
        self.send(b'tA')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'ta')
    def turn_left_slow(self):
        self.send(b'ta')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'tD')
    def turn_right_fast(self):
        self.send(b'tD')

    @prometheus.Registry.register('TankProxyUdpClientTankclient', 'td')
    def turn_right_slow(self):
        self.send(b'td')


class TankProxyUdpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyUdpClientBlueLed', 'b0')
    def off(self):
        self.send(b'b0')

    @prometheus.Registry.register('TankProxyUdpClientBlueLed', 'b1')
    def on(self):
        self.send(b'b1')

    @prometheus.Registry.register('TankProxyUdpClientBlueLed', 'bS', 'OUT')
    def state(self):
        self.send(b'bS')
        return self.recv(10)


class TankProxyUdpClientLightControl(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '0', 'OUT')
    def all_off(self):
        self.send(b'0')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '5', 'OUT')
    def all_on(self):
        self.send(b'5')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '?', 'OUT')
    def capability(self):
        self.send(b'?')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '4', 'OUT')
    def front_on(self):
        self.send(b'4')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '2', 'OUT')
    def left_on(self):
        self.send(b'2')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '1', 'OUT')
    def main_on(self):
        self.send(b'1')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', '3', 'OUT')
    def right_on(self):
        self.send(b'3')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyUdpClientLightControl', 'V', 'OUT')
    def version(self):
        self.send(b'V')
        return self.recv(10)


class TankProxyUdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyUdpClientRedLed', 'r0')
    def off(self):
        self.send(b'r0')

    @prometheus.Registry.register('TankProxyUdpClientRedLed', 'r1')
    def on(self):
        self.send(b'r1')

    @prometheus.Registry.register('TankProxyUdpClientRedLed', 'rS', 'OUT')
    def state(self):
        self.send(b'rS')
        return self.recv(10)


class TankProxyUdpClient(prometheus.RemoteTemplate):
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
        
        self.tankclient = TankProxyUdpClientTankclient(self.send, self.recv)
        self.register(tankclient=self.tankclient)

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

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tb')
    def blink_lights(self):
        self.send(b'tb')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tS')
    def fast_backward(self):
        self.send(b'tS')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tW')
    def fast_forward(self):
        self.send(b'tW')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tg')
    def full_stop(self):
        self.send(b'tg')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'ts')
    def slow_backward(self):
        self.send(b'ts')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tw')
    def slow_forward(self):
        self.send(b'tw')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tA')
    def turn_left_fast(self):
        self.send(b'tA')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'ta')
    def turn_left_slow(self):
        self.send(b'ta')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'tD')
    def turn_right_fast(self):
        self.send(b'tD')

    @prometheus.Registry.register('TankProxyTcpClientTankclient', 'td')
    def turn_right_slow(self):
        self.send(b'td')


class TankProxyTcpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyTcpClientBlueLed', 'b0')
    def off(self):
        self.send(b'b0')

    @prometheus.Registry.register('TankProxyTcpClientBlueLed', 'b1')
    def on(self):
        self.send(b'b1')

    @prometheus.Registry.register('TankProxyTcpClientBlueLed', 'bS', 'OUT')
    def state(self):
        self.send(b'bS')
        return self.recv(10)


class TankProxyTcpClientLightControl(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '0', 'OUT')
    def all_off(self):
        self.send(b'0')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '5', 'OUT')
    def all_on(self):
        self.send(b'5')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '?', 'OUT')
    def capability(self):
        self.send(b'?')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '4', 'OUT')
    def front_on(self):
        self.send(b'4')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '2', 'OUT')
    def left_on(self):
        self.send(b'2')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '1', 'OUT')
    def main_on(self):
        self.send(b'1')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', '3', 'OUT')
    def right_on(self):
        self.send(b'3')
        return self.recv(10)

    @prometheus.Registry.register('TankProxyTcpClientLightControl', 'V', 'OUT')
    def version(self):
        self.send(b'V')
        return self.recv(10)


class TankProxyTcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('TankProxyTcpClientRedLed', 'r0')
    def off(self):
        self.send(b'r0')

    @prometheus.Registry.register('TankProxyTcpClientRedLed', 'r1')
    def on(self):
        self.send(b'r1')

    @prometheus.Registry.register('TankProxyTcpClientRedLed', 'rS', 'OUT')
    def state(self):
        self.send(b'rS')
        return self.recv(10)


class TankProxyTcpClient(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.tankclient = TankProxyTcpClientTankclient(self.send, self.recv)
        self.register(tankclient=self.tankclient)

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
