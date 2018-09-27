# coding=utf-8
# generated at 2018-09-28 00:40:19
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
class ProxyTest2UdpClientTest(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientTest', 'tv', str)
    def value(self, **kwargs):
        self.send(b'tv', **kwargs)
        return self.recv(10)


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
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDsb', 'bv', str)
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientLightsensor', 'lr', str)
    def read(self, **kwargs):
        self.send(b'lr', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
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
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientLightsensor', 'lr', str)
    def read(self, **kwargs):
        self.send(b'lr', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
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
        self.ssd = ProxyTest2UdpClientSsd(self.send, self.recv)
        self.register(ssd=self.ssd)



class ProxyTest2UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientAds(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientAds', 'adv', str)
    def read(self, **kwargs):
        self.send(b'adv', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientNano(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientNano', 'nadi', str)
    def digital_in(self, **kwargs):
        self.send(b'nadi', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientNano', 'naio')
    def infraout(self, **kwargs):
        self.send(b'naio', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientNano', 'nado')
    def digital_out(self, **kwargs):
        self.send(b'nado', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientNano', 'naii', str)
    def infrain(self, **kwargs):
        self.send(b'naii', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientDs1307(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDs1307', 'dsv', str)
    def value(self, **kwargs):
        self.send(b'dsv', **kwargs)
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

    @prometheus.Registry.register('ProxyTest2UdpClientAdc1', 'ar', str)
    def read(self, **kwargs):
        self.send(b'ar', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientSsd(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientSsd', 'sst')
    def text(self, **kwargs):
        self.send(b'sst', **kwargs)


class ProxyTest2UdpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDsb', 'sv', str)
    def value(self, **kwargs):
        self.send(b'sv', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
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

    @prometheus.Registry.register('ProxyTest2UdpClientBlueLed', 'bv', str)
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class ProxyTest2UdpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientYellowLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientYellowLed', 'y1')
    def on(self, **kwargs):
        self.send(b'y1', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientYellowLed', 'y0')
    def off(self, **kwargs):
        self.send(b'y0', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientYellowLed', 'yv', str)
    def value(self, **kwargs):
        self.send(b'yv', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientRedLed', 'rv', str)
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class ProxyTest2UdpClientUwLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientUwLed', 'uv', str)
    def value(self, **kwargs):
        self.send(b'uv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientUwLed', 'u1')
    def on(self, **kwargs):
        self.send(b'u1', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientUwLed', 'u0')
    def off(self, **kwargs):
        self.send(b'u0', **kwargs)


class ProxyTest2UdpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientLightsensor', 'sr', str)
    def read(self, **kwargs):
        self.send(b'sr', **kwargs)
        return self.recv(10)


class ProxyTest2UdpClientGreenLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2UdpClientGreenLed', 'gv', str)
    def value(self, **kwargs):
        self.send(b'gv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2UdpClientGreenLed', 'g1')
    def on(self, **kwargs):
        self.send(b'g1', **kwargs)

    @prometheus.Registry.register('ProxyTest2UdpClientGreenLed', 'g0')
    def off(self, **kwargs):
        self.send(b'g0', **kwargs)


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
        self.test = ProxyTest2UdpClientTest(self.send, self.recv)
        self.register(test=self.test)
        self.test02 = ProxyTest2UdpClientTest02(self.send, self.recv)
        self.register(test02=self.test02)

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


# region ProxyTest2TcpClient
class ProxyTest2TcpClientTest(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientTest', 'tv', str)
    def value(self, **kwargs):
        self.send(b'tv', **kwargs)
        return self.recv(10)


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
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDsb', 'bv', str)
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientLightsensor', 'lr', str)
    def read(self, **kwargs):
        self.send(b'lr', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
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
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientLightsensor', 'lr', str)
    def read(self, **kwargs):
        self.send(b'lr', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
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
        self.ssd = ProxyTest2TcpClientSsd(self.send, self.recv)
        self.register(ssd=self.ssd)



class ProxyTest2TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientAds(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientAds', 'adv', str)
    def read(self, **kwargs):
        self.send(b'adv', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientNano(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientNano', 'nadi', str)
    def digital_in(self, **kwargs):
        self.send(b'nadi', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientNano', 'naio')
    def infraout(self, **kwargs):
        self.send(b'naio', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientNano', 'nado')
    def digital_out(self, **kwargs):
        self.send(b'nado', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientNano', 'naii', str)
    def infrain(self, **kwargs):
        self.send(b'naii', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientDs1307(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDs1307', 'dsv', str)
    def value(self, **kwargs):
        self.send(b'dsv', **kwargs)
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

    @prometheus.Registry.register('ProxyTest2TcpClientAdc1', 'ar', str)
    def read(self, **kwargs):
        self.send(b'ar', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientSsd(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientSsd', 'sst')
    def text(self, **kwargs):
        self.send(b'sst', **kwargs)


class ProxyTest2TcpClientDsb(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDsb', 'sv', str)
    def value(self, **kwargs):
        self.send(b'sv', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientDht11(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dv', str)
    def value(self, **kwargs):
        self.send(b'dv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dt', str)
    def temperature(self, **kwargs):
        self.send(b'dt', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dm')
    def measure(self, **kwargs):
        self.send(b'dm', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientDht11', 'dh', str)
    def humidity(self, **kwargs):
        self.send(b'dh', **kwargs)
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

    @prometheus.Registry.register('ProxyTest2TcpClientBlueLed', 'bv', str)
    def value(self, **kwargs):
        self.send(b'bv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientBlueLed', 'b0')
    def off(self, **kwargs):
        self.send(b'b0', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientBlueLed', 'b1')
    def on(self, **kwargs):
        self.send(b'b1', **kwargs)


class ProxyTest2TcpClientIntegratedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i1')
    def on(self, **kwargs):
        self.send(b'i1', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'i0')
    def off(self, **kwargs):
        self.send(b'i0', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientIntegratedLed', 'iv', str)
    def value(self, **kwargs):
        self.send(b'iv', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientYellowLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientYellowLed', 'y1')
    def on(self, **kwargs):
        self.send(b'y1', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientYellowLed', 'y0')
    def off(self, **kwargs):
        self.send(b'y0', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientYellowLed', 'yv', str)
    def value(self, **kwargs):
        self.send(b'yv', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientRedLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientRedLed', 'rv', str)
    def value(self, **kwargs):
        self.send(b'rv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientRedLed', 'r0')
    def off(self, **kwargs):
        self.send(b'r0', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientRedLed', 'r1')
    def on(self, **kwargs):
        self.send(b'r1', **kwargs)


class ProxyTest2TcpClientUwLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientUwLed', 'uv', str)
    def value(self, **kwargs):
        self.send(b'uv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientUwLed', 'u1')
    def on(self, **kwargs):
        self.send(b'u1', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientUwLed', 'u0')
    def off(self, **kwargs):
        self.send(b'u0', **kwargs)


class ProxyTest2TcpClientLightsensor(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientLightsensor', 'sr', str)
    def read(self, **kwargs):
        self.send(b'sr', **kwargs)
        return self.recv(10)


class ProxyTest2TcpClientGreenLed(prometheus.Prometheus):
    def __init__(self, send, recv):
        prometheus.Prometheus.__init__(self)
        self.send = send
        self.recv = recv

    @prometheus.Registry.register('ProxyTest2TcpClientGreenLed', 'gv', str)
    def value(self, **kwargs):
        self.send(b'gv', **kwargs)
        return self.recv(10)

    @prometheus.Registry.register('ProxyTest2TcpClientGreenLed', 'g1')
    def on(self, **kwargs):
        self.send(b'g1', **kwargs)

    @prometheus.Registry.register('ProxyTest2TcpClientGreenLed', 'g0')
    def off(self, **kwargs):
        self.send(b'g0', **kwargs)


class ProxyTest2TcpClient(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        
        self.nodetest = ProxyTest2TcpClientNodetest(self.send, self.recv)
        self.register(nodetest=self.nodetest)
        self.sensor01 = ProxyTest2TcpClientSensor01(self.send, self.recv)
        self.register(sensor01=self.sensor01)
        self.sensor02 = ProxyTest2TcpClientSensor02(self.send, self.recv)
        self.register(sensor02=self.sensor02)
        self.test = ProxyTest2TcpClientTest(self.send, self.recv)
        self.register(test=self.test)
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
