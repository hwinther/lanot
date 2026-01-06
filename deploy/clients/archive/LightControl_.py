# generated at 2017-06-18 01:48:14
import prometheus
import machine


class LightControl(prometheus.RemoteTemplate):
    def __init__(self, channel, baudrate):
        prometheus.RemoteTemplate.__init__(self)
        self.uart = machine.UART(channel, baudrate=baudrate)

    def send(self, data):
        self.uart.write(data + b'\n')

    def recv(self, buffersize=None):
        if buffersize:
            return self.uart.read(buffersize)
        else:
            return self.uart.read()

    @prometheus.Registry.register('LightControl', '0', 'OUT')
    def all_off(self):
        self.send(b'0')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', '1', 'OUT')
    def main_on(self):
        self.send(b'1')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', '2', 'OUT')
    def left_on(self):
        self.send(b'2')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', '3', 'OUT')
    def right_on(self):
        self.send(b'3')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', '4', 'OUT')
    def front_on(self):
        self.send(b'4')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', '5', 'OUT')
    def all_on(self):
        self.send(b'5')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', '?', 'OUT')
    def capability(self):
        self.send(b'?')
        return self.recv(4)

    @prometheus.Registry.register('LightControl', 'V', 'OUT')
    def version(self):
        self.send(b'V')
        return self.recv(4)


