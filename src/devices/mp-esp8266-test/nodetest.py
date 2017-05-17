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

if __name__ == '__main__':
    nt = NodeTest()
    nt.start_socket_server()
