# generated at 2017-08-30 23:03:13
import prometheus
import socket
import machine
import time
import gc

gc.collect()


class LightControl(prometheus.RemoteTemplate):
    def __init__(self, channel, baudrate):
        prometheus.RemoteTemplate.__init__(self)
        self.uart = machine.UART(channel, baudrate=baudrate)
        self.buffer = prometheus.Buffer(split_chars=b'\n', end_chars=b'\r')

    def send(self, data):
        self.uart.write(data + self.buffer.endChars + self.buffer.splitChars)

    def recv(self, buffersize=None):
        if buffersize:
            self.buffer.parse(self.uart.read(buffersize))
        else:
            self.buffer.parse(self.uart.read())
        return self.buffer.pop()

    def recv_timeout(self, buffersize, timeout):
        raise Exception('Not implemented due to lazyness')

    @prometheus.Registry.register('LightControl', '0', 'OUT')
    def all_off(self):
        self.send(b'0')
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '1', 'OUT')
    def main_on(self):
        self.send(b'1')
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '2', 'OUT')
    def left_on(self):
        self.send(b'2')
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '3', 'OUT')
    def right_on(self):
        self.send(b'3')
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '4', 'OUT')
    def front_on(self):
        self.send(b'4')
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '5', 'OUT')
    def all_on(self):
        self.send(b'5')
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '?', 'OUT')
    def capability(self):
        self.send(b'?')
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', 'V', 'OUT')
    def version(self):
        self.send(b'V')
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

