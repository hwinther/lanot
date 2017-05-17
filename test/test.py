import prometheus
import machine


class Other(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

    @prometheus.Registry.register("A", '')
    def testmethod(self):
        pass


class Test(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
        blue = machine.Pin("GP0", machine.Pin.OUT)
        self.blue_led = prometheus.Led(blue)
        self.register(blue_led=self.blue_led)
        self.red_led = prometheus.Led(machine.Pin("GP1", machine.Pin.OUT))
        self.register(red_led=self.blue_led)


t = Test()
print('test constructed')
# print('prometheus.Registry.r %s' % prometheus.Registry.r)
# print('t.r %s' % t.r)
print('t.commands %s' % t.commands)
# print('t.blue_led.r %s' % t.blue_led.r)
print('t.blue_led.commands %s' % t.blue_led.commands)
t.blue_led.on()
