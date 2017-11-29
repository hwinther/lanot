# generated at 2017-09-10 00:20:34
import prometheus
import socket
import machine
import time
import gc
import prometheus_crypto

gc.collect()


class Sensor01UdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01UdpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)

    @prometheus.Registry.register('Sensor01UdpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('Sensor01UdpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('Sensor01UdpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)


class Sensor01UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01UdpClientLightsensor', 'lr', 'OUT')
    def read(self):
        self.send(b'lr')
        return self.recv(10)


class Sensor01UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01UdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('Sensor01UdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('Sensor01UdpClientIntegratedLed', 'iS', 'OUT')
    def state(self):
        self.send(b'iS')
        return self.recv(10)


class Sensor01UdpClient(prometheus.RemoteTemplate):
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
        
        self.dht11 = Sensor01UdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.integrated_led = Sensor01UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = Sensor01UdpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)

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



class Sensor01RsaUdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01RsaUdpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)

    @prometheus.Registry.register('Sensor01RsaUdpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('Sensor01RsaUdpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('Sensor01RsaUdpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)


class Sensor01RsaUdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01RsaUdpClientLightsensor', 'lr', 'OUT')
    def read(self):
        self.send(b'lr')
        return self.recv(10)


class Sensor01RsaUdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('Sensor01RsaUdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('Sensor01RsaUdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('Sensor01RsaUdpClientIntegratedLed', 'iS', 'OUT')
    def state(self):
        self.send(b'iS')
        return self.recv(10)


class Sensor01RsaUdpClient(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host='', bind_port=9195, clientencrypt=False):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((bind_host, bind_port))
        print('listening on %s:%d' % (bind_host, bind_port))
        self.socket.settimeout(0)
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        self.negotiated = False
        self.remote_key = (0, 0)
        self.clientencrypt = clientencrypt
        self.private_key = None
        self.public_key = None
        
        self.dht11 = Sensor01RsaUdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.integrated_led = Sensor01RsaUdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = Sensor01RsaUdpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)

    def negotiate(self, revalidate=False):
        d = prometheus_crypto.get_local_key_registry()
        if self.remote_addr[0] in d.keys() and revalidate is False:
            print('found cached pubkey for %s' % self.remote_addr[0])
            self.remote_key = d[self.remote_addr[0]]
            self.negotiated = True
        else:
            print('requesting pubkey')
            self.send_raw(b'pubkey')
            data = self.recv_timeout(250, 1)
            print('pubkey recv: %s' % repr(data))

            self.remote_key = data.split(b'\t')
            self.remote_key = (int(self.remote_key[0]), int(self.remote_key[1]))
            update = True
            if self.remote_addr[0] in d.keys():
                if d[self.remote_addr[0]][0] != self.remote_key[0] or d[self.remote_addr[0]][1] != self.remote_key[1]:
                    print('! alert - public key does not match')
                    print('%s and %s' % (d[self.remote_addr[0]][0], self.remote_key[0]))
                    print('%s and %s' % (d[self.remote_addr[0]][1], self.remote_key[1]))
                else:
                    print('valid pubkey for %s' % self.remote_addr[0])
                    update = False
            if update:
                d[self.remote_addr[0]] = self.remote_key
                prometheus_crypto.set_local_key_registry(d)

        if self.clientencrypt:
            if self.private_key is None:
                print('generating new keys')
                self.public_key, self.private_key = prometheus_crypto.get_or_create_local_keys()

            print('sending version')
            self.send_raw(b'version')
            reply = self.recv()
            print('repr(reply)=%s' % repr(reply))

            msg = b'%d\t\t\t%d' % (self.public_key[0], self.public_key[1])
            print('returning public key')
            self.send_raw(msg)

        self.negotiated = True

    def send_raw(self, data):
        self.socket.sendto(data + self.endChars + self.splitChars, self.remote_addr)

    def send_crypted(self, data):
        print('send_crypted: cleartext is %d bytes' % len(data))
        if self.clientencrypt:
            data = prometheus_crypto.encrypt_packet(data, self.remote_key, self.private_key)
        else:
            data = prometheus_crypto.encrypt_packet(data, self.remote_key)
        self.send_raw(data)

    def send(self, data):
        if self.negotiated is False:
            self.negotiate(revalidate=False)
        self.send_crypted(data)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except:  # they said i could use OSError here, they lied (cpython/micropython issue, solve it later if necessary)
            return None, None

    def recv_once(self, buffersize=250):
        data, addr = self.try_recv(buffersize)  # type: bytes, int
        if data is None:
            return None
        if addr not in self.buffers:
            self.buffers[addr] = prometheus.Buffer(split_chars=self.splitChars, end_chars=self.endChars)
        self.buffers[addr].parse(data)
        return self.buffers[addr].pop()

    def recv(self, buffersize=250):
        data = self.recv_timeout(buffersize, 0.5)
        if self.negotiated:
            if self.clientencrypt:
                data = prometheus_crypto.decrypt_packet(data, self.remote_key, self.private_key)
            else:
                data = prometheus_crypto.decrypt_packet(data, self.remote_key)
        return data

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

