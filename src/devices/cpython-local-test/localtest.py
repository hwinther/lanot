import prometheus
import prometheus_esp8266
import prometheus_servers
import prometheus_crypto
import machine


class LocalTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
        blue = machine.Pin(14, machine.Pin.OUT)
        self.blue_led = prometheus.Led(blue)
        self.register(prefix='b', blue_led=self.blue_led)
        self.red_led = prometheus.Led(machine.Pin(15, machine.Pin.OUT))
        self.register(prefix='r', red_led=self.red_led)
        self.dht11 = prometheus_esp8266.Dht11(machine.Pin(13, machine.Pin.OUT))
        self.register(prefix='d', dht11=self.dht11)
        self.hygrometer = prometheus.Adc(0)
        self.register(prefix='h', hygrometer=self.hygrometer)

    @prometheus.Registry.register('LocalTest', 'V', 'OUT')
    def version(self):
        return prometheus.__version__

if __name__ == '__main__':
    localtest = LocalTest()

    # udpserver = prometheus_servers.UdpSocketServer(localtest)
    # udpserver.start()

    # multiserver = prometheus_servers.MultiServer()
    #
    # udpserver = prometheus_servers.UdpSocketServer(localtest)
    # multiserver.add(udpserver, bind_host='', bind_port=9195)
    #
    # jsonrestserver = prometheus_servers.JsonRestServer(localtest)
    # multiserver.add(jsonrestserver, bind_host='', bind_port=8080)
    #
    # multiserver.start()

    rsaserver = prometheus_crypto.RsaUdpSocketServer(localtest)
    rsaserver.start()
