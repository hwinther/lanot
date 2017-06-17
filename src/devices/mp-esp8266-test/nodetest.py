import prometheus
import machine


class NodeTest(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
        blue = machine.Pin(14, machine.Pin.OUT)
        self.blue_led = prometheus.Led(blue)
        self.register(blue_led=self.blue_led)
        self.red_led = prometheus.Led(machine.Pin(15, machine.Pin.OUT))
        self.register(red_led=self.red_led)
        self.dht11 = prometheus.Dht11(machine.Pin(13, machine.Pin.OUT))
        self.register(dht11=self.dht11)
        self.hygrometer = prometheus.Adc(0)
        self.register(hydrometer=self.hygrometer)

if __name__ == '__main__':
    nt = NodeTest()
    nt.start_socket_server()
