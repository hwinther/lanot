# generated at 2017-06-18 01:48:15
import prometheus
import socket
import machine


class LedBlue(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LedBlue', 'E')
    def off(self):
        self.send(b'E')

    @prometheus.Registry.register('LedBlue', 'G', 'OUT')
    def state(self):
        self.send(b'G')
        return self.recv(4)

    @prometheus.Registry.register('LedBlue', 'F')
    def on(self):
        self.send(b'F')


class LedRed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LedRed', 'I')
    def on(self):
        self.send(b'I')

    @prometheus.Registry.register('LedRed', 'H')
    def off(self):
        self.send(b'H')

    @prometheus.Registry.register('LedRed', 'J', 'OUT')
    def state(self):
        self.send(b'J')
        return self.recv(4)


class LightControl(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('LightControl', 'K', 'OUT')
    def all_off(self):
        self.send(b'K')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', 'M', 'OUT')
    def capability(self):
        self.send(b'M')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', 'L', 'OUT')
    def all_on(self):
        self.send(b'L')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', 'O', 'OUT')
    def left_on(self):
        self.send(b'O')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', 'N', 'OUT')
    def front_on(self):
        self.send(b'N')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', 'Q', 'OUT')
    def right_on(self):
        self.send(b'Q')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', 'P', 'OUT')
    def main_on(self):
        self.send(b'P')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', 'R', 'OUT')
    def version(self):
        self.send(b'R')
        return self.recv(4)


class TankTestTcp(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, local_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', local_port))
        self.remote_addr = (remote_host, remote_port)
        self.socket.connect(self.remote_addr)
        
        self.led_blue = LedBlue(self.send, self.recv)
        self.register(led_blue=self.led_blue)
        self.led_red = LedRed(self.send, self.recv)
        self.register(led_red=self.led_red)
        self.lightControl = LightControl(self.send, self.recv)
        self.register(lightControl=self.lightControl)

    def send(self, data):
        self.socket.sendall(data)

    def recv(self, buffersize=10):
        return self.socket.recv(buffersize)


    @prometheus.Registry.register('TankTestTcp', 'A')
    def blink_lights(self):
        self.send(b'A')

    @prometheus.Registry.register('TankTestTcp', 'C')
    def fast_forward(self):
        self.send(b'C')

    @prometheus.Registry.register('TankTestTcp', 'B')
    def fast_backward(self):
        self.send(b'B')

    @prometheus.Registry.register('TankTestTcp', 'D')
    def full_stop(self):
        self.send(b'D')

    @prometheus.Registry.register('TankTestTcp', 'S')
    def slow_backward(self):
        self.send(b'S')

    @prometheus.Registry.register('TankTestTcp', 'U')
    def turn_left_fast(self):
        self.send(b'U')

    @prometheus.Registry.register('TankTestTcp', 'T')
    def slow_forward(self):
        self.send(b'T')

    @prometheus.Registry.register('TankTestTcp', 'W')
    def turn_right_fast(self):
        self.send(b'W')

    @prometheus.Registry.register('TankTestTcp', 'V')
    def turn_left_slow(self):
        self.send(b'V')

    @prometheus.Registry.register('TankTestTcp', 'X')
    def turn_right_slow(self):
        self.send(b'X')



class TankTestUdp(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, local_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', local_port))
        self.remote_addr = (remote_host, remote_port)
        
        self.led_blue = LedBlue(self.send, self.recv)
        self.register(led_blue=self.led_blue)
        self.led_red = LedRed(self.send, self.recv)
        self.register(led_red=self.led_red)
        self.lightControl = LightControl(self.send, self.recv)
        self.register(lightControl=self.lightControl)

    def send(self, data):
        self.socket.sendto(data, self.remote_addr)

    def recv(self, buffersize=10):
        self.socket.setblocking(False)
        data, addr = self.socket.recvfrom(buffersize)
        self.socket.setblocking(True)
        return data


    @prometheus.Registry.register('TankTestUdp', 'A')
    def blink_lights(self):
        self.send(b'A')

    @prometheus.Registry.register('TankTestUdp', 'C')
    def fast_forward(self):
        self.send(b'C')

    @prometheus.Registry.register('TankTestUdp', 'B')
    def fast_backward(self):
        self.send(b'B')

    @prometheus.Registry.register('TankTestUdp', 'D')
    def full_stop(self):
        self.send(b'D')

    @prometheus.Registry.register('TankTestUdp', 'S')
    def slow_backward(self):
        self.send(b'S')

    @prometheus.Registry.register('TankTestUdp', 'U')
    def turn_left_fast(self):
        self.send(b'U')

    @prometheus.Registry.register('TankTestUdp', 'T')
    def slow_forward(self):
        self.send(b'T')

    @prometheus.Registry.register('TankTestUdp', 'W')
    def turn_right_fast(self):
        self.send(b'W')

    @prometheus.Registry.register('TankTestUdp', 'V')
    def turn_left_slow(self):
        self.send(b'V')

    @prometheus.Registry.register('TankTestUdp', 'X')
    def turn_right_slow(self):
        self.send(b'X')


