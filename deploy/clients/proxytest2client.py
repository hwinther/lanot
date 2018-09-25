# coding=utf-8
# generated at 2018-09-24 23:41:06
import prometheus
import socket
import time
import gc
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

gc.collect()


# region ProxyTest2UdpClient
class ProxyTest2UdpClientSensor02(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.dht11 = ProxyTest2UdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.dsb = ProxyTest2UdpClientDsb(self.send, self.recv)
        self.register(dsb=self.dsb)
        self.integrated_led = ProxyTest2UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = ProxyTest2UdpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)



class ProxyTest2UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class ProxyTest2UdpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDsb', 'bv', 'OUT')
    def value(self):
        self.send(b'bv')
        return self.recv(10)


class ProxyTest2UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientLightsensor', 'lr', 'OUT')
    def read(self):
        self.send(b'lr')
        return self.recv(10)


class ProxyTest2UdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class ProxyTest2UdpClientNodetest(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.adc1 = ProxyTest2UdpClientAdc1(self.send, self.recv)
        self.register(adc1=self.adc1)
        self.ads = ProxyTest2UdpClientAds(self.send, self.recv)
        self.register(ads=self.ads)
        self.dht11 = ProxyTest2UdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.ds1307 = ProxyTest2UdpClientDs1307(self.send, self.recv)
        self.register(ds1307=self.ds1307)
        self.dsb = ProxyTest2UdpClientDsb(self.send, self.recv)
        self.register(dsb=self.dsb)
        self.integrated_led = ProxyTest2UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.nano = ProxyTest2UdpClientNano(self.send, self.recv)
        self.register(nano=self.nano)
        self.neopixel = ProxyTest2UdpClientNeopixel(self.send, self.recv)
        self.register(neopixel=self.neopixel)



class ProxyTest2UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class ProxyTest2UdpClientAds(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientAds', 'adv', 'OUT')
    def read(self):
        self.send(b'adv')
        return self.recv(10)


class ProxyTest2UdpClientNano(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientNano', 'nadi', 'OUT')
    def digital_in(self):
        self.send(b'nadi')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientNano', 'naio')
    def infraout(self):
        self.send(b'naio')

    @prometheus.Registry.register('ProxyTest2UdpClientNano', 'nado')
    def digital_out(self):
        self.send(b'nado')

    @prometheus.Registry.register('ProxyTest2UdpClientNano', 'naii', 'OUT')
    def infrain(self):
        self.send(b'naii')
        return self.recv(10)


class ProxyTest2UdpClientDs1307(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDs1307', 'dsv', 'OUT')
    def value(self):
        self.send(b'dsv')
        return self.recv(10)


class ProxyTest2UdpClientNeopixel(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv



class ProxyTest2UdpClientAdc1(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientAdc1', 'ar', 'OUT')
    def read(self):
        self.send(b'ar')
        return self.recv(10)


class ProxyTest2UdpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDsb', 'sv', 'OUT')
    def value(self):
        self.send(b'sv')
        return self.recv(10)


class ProxyTest2UdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class ProxyTest2UdpClientSensor01(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.dht11 = ProxyTest2UdpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.integrated_led = ProxyTest2UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = ProxyTest2UdpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)



class ProxyTest2UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class ProxyTest2UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientLightsensor', 'lr', 'OUT')
    def read(self):
        self.send(b'lr')
        return self.recv(10)


class ProxyTest2UdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class ProxyTest2UdpClientTest02(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.blue_led = ProxyTest2UdpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.green_led = ProxyTest2UdpClientGreenLed(self.send, self.recv)
        self.register(green_led=self.green_led)
        self.integrated_led = ProxyTest2UdpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = ProxyTest2UdpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)
        self.red_led = ProxyTest2UdpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.uw_led = ProxyTest2UdpClientUwLed(self.send, self.recv)
        self.register(uw_led=self.uw_led)
        self.yellow_led = ProxyTest2UdpClientYellowLed(self.send, self.recv)
        self.register(yellow_led=self.yellow_led)



class ProxyTest2UdpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientBlueLed', 'bv', 'OUT')
    def value(self):
        self.send(b'bv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientBlueLed', 'b0')
    def off(self):
        self.send(b'b0')

    @prometheus.Registry.register('ProxyTest2UdpClientBlueLed', 'b1')
    def on(self):
        self.send(b'b1')


class ProxyTest2UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class ProxyTest2UdpClientYellowLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientYellowLed', 'y1')
    def on(self):
        self.send(b'y1')

    @prometheus.Registry.register('ProxyTest2UdpClientYellowLed', 'y0')
    def off(self):
        self.send(b'y0')

    @prometheus.Registry.register('ProxyTest2UdpClientYellowLed', 'yv', 'OUT')
    def value(self):
        self.send(b'yv')
        return self.recv(10)


class ProxyTest2UdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientRedLed', 'rv', 'OUT')
    def value(self):
        self.send(b'rv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientRedLed', 'r0')
    def off(self):
        self.send(b'r0')

    @prometheus.Registry.register('ProxyTest2UdpClientRedLed', 'r1')
    def on(self):
        self.send(b'r1')


class ProxyTest2UdpClientUwLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientUwLed', 'uv', 'OUT')
    def value(self):
        self.send(b'uv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientUwLed', 'u1')
    def on(self):
        self.send(b'u1')

    @prometheus.Registry.register('ProxyTest2UdpClientUwLed', 'u0')
    def off(self):
        self.send(b'u0')


class ProxyTest2UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientLightsensor', 'sr', 'OUT')
    def read(self):
        self.send(b'sr')
        return self.recv(10)


class ProxyTest2UdpClientGreenLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientGreenLed', 'gv', 'OUT')
    def value(self):
        self.send(b'gv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientGreenLed', 'g1')
    def on(self):
        self.send(b'g1')

    @prometheus.Registry.register('ProxyTest2UdpClientGreenLed', 'g0')
    def off(self):
        self.send(b'g0')


class ProxyTest2UdpClient(prometheus.misc.RemoteTemplate):
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
        
        self.nodetest = ProxyTest2UdpClientNodetest(self.send, self.recv)
        self.register(nodetest=self.nodetest)
        self.sensor01 = ProxyTest2UdpClientSensor01(self.send, self.recv)
        self.register(sensor01=self.sensor01)
        self.sensor02 = ProxyTest2UdpClientSensor02(self.send, self.recv)
        self.register(sensor02=self.sensor02)
        self.test02 = ProxyTest2UdpClientTest02(self.send, self.recv)
        self.register(test02=self.test02)

    def send(self, data):
        self.socket.sendto(data + self.endChars + self.splitChars, self.remote_addr)

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


# endregion


# region ProxyTest2TcpClient
class ProxyTest2TcpClientSensor02(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.dht11 = ProxyTest2TcpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.dsb = ProxyTest2TcpClientDsb(self.send, self.recv)
        self.register(dsb=self.dsb)
        self.integrated_led = ProxyTest2TcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = ProxyTest2TcpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)



class ProxyTest2TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class ProxyTest2TcpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDsb', 'bv', 'OUT')
    def value(self):
        self.send(b'bv')
        return self.recv(10)


class ProxyTest2TcpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientLightsensor', 'lr', 'OUT')
    def read(self):
        self.send(b'lr')
        return self.recv(10)


class ProxyTest2TcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class ProxyTest2TcpClientNodetest(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.adc1 = ProxyTest2TcpClientAdc1(self.send, self.recv)
        self.register(adc1=self.adc1)
        self.ads = ProxyTest2TcpClientAds(self.send, self.recv)
        self.register(ads=self.ads)
        self.dht11 = ProxyTest2TcpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.ds1307 = ProxyTest2TcpClientDs1307(self.send, self.recv)
        self.register(ds1307=self.ds1307)
        self.dsb = ProxyTest2TcpClientDsb(self.send, self.recv)
        self.register(dsb=self.dsb)
        self.integrated_led = ProxyTest2TcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.nano = ProxyTest2TcpClientNano(self.send, self.recv)
        self.register(nano=self.nano)
        self.neopixel = ProxyTest2TcpClientNeopixel(self.send, self.recv)
        self.register(neopixel=self.neopixel)



class ProxyTest2TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class ProxyTest2TcpClientAds(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientAds', 'adv', 'OUT')
    def read(self):
        self.send(b'adv')
        return self.recv(10)


class ProxyTest2TcpClientNano(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientNano', 'nadi', 'OUT')
    def digital_in(self):
        self.send(b'nadi')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientNano', 'naio')
    def infraout(self):
        self.send(b'naio')

    @prometheus.Registry.register('ProxyTest2TcpClientNano', 'nado')
    def digital_out(self):
        self.send(b'nado')

    @prometheus.Registry.register('ProxyTest2TcpClientNano', 'naii', 'OUT')
    def infrain(self):
        self.send(b'naii')
        return self.recv(10)


class ProxyTest2TcpClientDs1307(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDs1307', 'dsv', 'OUT')
    def value(self):
        self.send(b'dsv')
        return self.recv(10)


class ProxyTest2TcpClientNeopixel(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv



class ProxyTest2TcpClientAdc1(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientAdc1', 'ar', 'OUT')
    def read(self):
        self.send(b'ar')
        return self.recv(10)


class ProxyTest2TcpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDsb', 'sv', 'OUT')
    def value(self):
        self.send(b'sv')
        return self.recv(10)


class ProxyTest2TcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class ProxyTest2TcpClientSensor01(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.dht11 = ProxyTest2TcpClientDht11(self.send, self.recv)
        self.register(dht11=self.dht11)
        self.integrated_led = ProxyTest2TcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = ProxyTest2TcpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)



class ProxyTest2TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class ProxyTest2TcpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientLightsensor', 'lr', 'OUT')
    def read(self):
        self.send(b'lr')
        return self.recv(10)


class ProxyTest2TcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dv', 'OUT')
    def value(self):
        self.send(b'dv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dt', 'OUT')
    def temperature(self):
        self.send(b'dt')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dm')
    def measure(self):
        self.send(b'dm')

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dh', 'OUT')
    def humidity(self):
        self.send(b'dh')
        return self.recv(10)


class ProxyTest2TcpClientTest02(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        
        self.blue_led = ProxyTest2TcpClientBlueLed(self.send, self.recv)
        self.register(blue_led=self.blue_led)
        self.green_led = ProxyTest2TcpClientGreenLed(self.send, self.recv)
        self.register(green_led=self.green_led)
        self.integrated_led = ProxyTest2TcpClientIntegratedLed(self.send, self.recv)
        self.register(integrated_led=self.integrated_led)
        self.lightsensor = ProxyTest2TcpClientLightsensor(self.send, self.recv)
        self.register(lightsensor=self.lightsensor)
        self.red_led = ProxyTest2TcpClientRedLed(self.send, self.recv)
        self.register(red_led=self.red_led)
        self.uw_led = ProxyTest2TcpClientUwLed(self.send, self.recv)
        self.register(uw_led=self.uw_led)
        self.yellow_led = ProxyTest2TcpClientYellowLed(self.send, self.recv)
        self.register(yellow_led=self.yellow_led)



class ProxyTest2TcpClientBlueLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientBlueLed', 'bv', 'OUT')
    def value(self):
        self.send(b'bv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientBlueLed', 'b0')
    def off(self):
        self.send(b'b0')

    @prometheus.Registry.register('ProxyTest2TcpClientBlueLed', 'b1')
    def on(self):
        self.send(b'b1')


class ProxyTest2TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i1')
    def on(self):
        self.send(b'i1')

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i0')
    def off(self):
        self.send(b'i0')

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'iv', 'OUT')
    def value(self):
        self.send(b'iv')
        return self.recv(10)


class ProxyTest2TcpClientYellowLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientYellowLed', 'y1')
    def on(self):
        self.send(b'y1')

    @prometheus.Registry.register('ProxyTest2TcpClientYellowLed', 'y0')
    def off(self):
        self.send(b'y0')

    @prometheus.Registry.register('ProxyTest2TcpClientYellowLed', 'yv', 'OUT')
    def value(self):
        self.send(b'yv')
        return self.recv(10)


class ProxyTest2TcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientRedLed', 'rv', 'OUT')
    def value(self):
        self.send(b'rv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientRedLed', 'r0')
    def off(self):
        self.send(b'r0')

    @prometheus.Registry.register('ProxyTest2TcpClientRedLed', 'r1')
    def on(self):
        self.send(b'r1')


class ProxyTest2TcpClientUwLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientUwLed', 'uv', 'OUT')
    def value(self):
        self.send(b'uv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientUwLed', 'u1')
    def on(self):
        self.send(b'u1')

    @prometheus.Registry.register('ProxyTest2TcpClientUwLed', 'u0')
    def off(self):
        self.send(b'u0')


class ProxyTest2TcpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientLightsensor', 'sr', 'OUT')
    def read(self):
        self.send(b'sr')
        return self.recv(10)


class ProxyTest2TcpClientGreenLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientGreenLed', 'gv', 'OUT')
    def value(self):
        self.send(b'gv')
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientGreenLed', 'g1')
    def on(self):
        self.send(b'g1')

    @prometheus.Registry.register('ProxyTest2TcpClientGreenLed', 'g0')
    def off(self):
        self.send(b'g0')


class ProxyTest2TcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        
        self.nodetest = ProxyTest2TcpClientNodetest(self.send, self.recv)
        self.register(nodetest=self.nodetest)
        self.sensor01 = ProxyTest2TcpClientSensor01(self.send, self.recv)
        self.register(sensor01=self.sensor01)
        self.sensor02 = ProxyTest2TcpClientSensor02(self.send, self.recv)
        self.register(sensor02=self.sensor02)
        self.test02 = ProxyTest2TcpClientTest02(self.send, self.recv)
        self.register(test02=self.test02)

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.bind_host is not None:
            logging.notice('bound to %s:%d' % (self.bind_host, self.bind_port))
            self.socket.bind((self.bind_host, self.bind_port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(5)
        logging.info('Connecting to %s' % repr(self.remote_addr))
        self.socket.connect(self.remote_addr)

    def send_once(self, data):
        self.socket.send(data + self.endChars + self.splitChars)

    def send(self, data):
        if self.socket is None:
            self.create_socket()
        try:
            self.send_once(data)
        except prometheus.psocket.socket_error:
            self.create_socket()
            self.send_once(data)

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
            self.buffers[addr] = prometheus.Buffer(split_chars=self.splitChars, end_chars=self.endChars)
        self.buffers[addr].parse(data)
        return self.buffers[addr].pop()


# endregion
