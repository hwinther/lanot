import prometheus
import machine


class A(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.a_led = prometheus.Led(machine.Pin(15, machine.Pin.OUT))
        self.register(prefix='al', a_led=self.a_led)

    @prometheus.Registry.register('A', 'T')
    def toggle(self):
        print('A.toggle')


class B(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.b_led = prometheus.Led(machine.Pin(16, machine.Pin.OUT))
        self.register(prefix='bl', b_led=self.b_led)

        self.a_object = A()
        self.register(prefix='a', a_object=self.a_object)

    @prometheus.Registry.register('B', 'T')
    def toggle(self):
        print('B.toggle')


class C(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.c_led = prometheus.Led(machine.Pin(17, machine.Pin.OUT))
        self.register(prefix='cl', c_led=self.c_led)

        self.b_object = B()
        self.register(prefix='b', b_object=self.b_object)

    @prometheus.Registry.register('C', 'T')
    def toggle(self):
        print('C.toggle')


if __name__ == '__main__':
    a = A()
    # audp = prometheus.UdpSocketServer(a)
    b = B()
    c = C()
