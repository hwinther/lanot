# coding=utf-8
import gc
from prometheus import Prometheus, Registry
import prometheus.logging as logging

gc.collect()


class InputOutputProxy(Prometheus):
    def __init__(self, send, recv):
        # Could pass on send, recv method refs an template inherit self to be able to issubclassof check these
        Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        # POST_INIT

    # cut

    # noinspection PyPep8Naming
    @Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self):
        self.send(b'VALUE')

    # noinspection PyPep8Naming
    @Registry.register('CLASS_NAME', 'VALUE', 'OUT')
    def METHOD_NAME_OUT(self):
        self.send(b'VALUE')
        # TODO: determine output size declaratively in source?
        return self.recv(10)


class RemoteTemplate(Prometheus):
    def __init__(self):
        Prometheus.__init__(self)

    def send(self, data):
        logging.notice('send: %s' % repr(data))

    def recv(self, buffersize=None):
        logging.notice('recv buffersize=%s' % buffersize)
        return None

    def die(self):
        self.send(b'die')

    def cap(self):
        self.send(b'cap')
        data = self.recv(100)
        logging.notice('cap: %s' % repr(data))
        return data

    def uname(self):
        self.send(b'uname')
        data = self.recv(100)
        logging.notice('uname: %s' % repr(data))
        return data

    def version(self):
        self.send(b'version')
        data = self.recv(100)
        logging.notice('version: %s' % repr(data))
        return data

    def sysinfo(self):
        self.send(b'sysinfo')
        data = self.recv(100)
        logging.notice('sysinfo: %s' % repr(data))
        return data
