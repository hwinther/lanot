# generated at 2018-09-27 18:05:14
import prometheus
import machine
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


class LightControl(prometheus.misc.RemoteTemplate):
    def __init__(self, channel, baudrate):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.uart = machine.UART(channel, baudrate=baudrate)
        self.buffer = prometheus.Buffer(split_chars=b'\n', end_chars=b'\r')

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)
        self.uart.write(data + self.buffer.end_chars + args + self.buffer.split_chars)

    def recv(self, buffersize=None):
        if buffersize:
            self.buffer.parse(self.uart.read(buffersize))
        else:
            self.buffer.parse(self.uart.read())
        return self.buffer.pop()

    def recv_timeout(self, buffersize, timeout):
        raise Exception('Not implemented due to lazyness')

    @prometheus.Registry.register('LightControl', '0', 'OUT')
    def all_off(self, **kwargs):
        self.send(b'0', **kwargs)
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '1', 'OUT')
    def main_on(self, **kwargs):
        self.send(b'1', **kwargs)
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '2', 'OUT')
    def left_on(self, **kwargs):
        self.send(b'2', **kwargs)
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '3', 'OUT')
    def right_on(self, **kwargs):
        self.send(b'3', **kwargs)
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '4', 'OUT')
    def front_on(self, **kwargs):
        self.send(b'4', **kwargs)
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '5', 'OUT')
    def all_on(self, **kwargs):
        self.send(b'5', **kwargs)
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', '?', 'OUT')
    def capability(self, **kwargs):
        self.send(b'?', **kwargs)
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()

    @prometheus.Registry.register('LightControl', 'V', 'OUT')
    def version(self, **kwargs):
        self.send(b'V', **kwargs)
        self.recv(10)
        time.sleep(0.5)
        return self.buffer.pop()


