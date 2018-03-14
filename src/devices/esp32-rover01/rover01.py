import prometheus
import prometheus_esp8266
import machine
import gc
import time
import ssd1306


gc.collect()


class Rover01(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), state=False)
        self.register(prefix='i', integrated_led=self.integrated_led)

        self.uart1 = machine.UART(1, baudrate=115200)

        self.i2c = machine.I2C(freq=400000, scl=machine.Pin(22, machine.Pin.OUT), sda=machine.Pin(21, machine.Pin.OUT))
        self.ssd = ssd1306.SSD1306_I2C(width=128, height=64, i2c=self.i2c)

        self.ssd.text('init', 0, 0)
        self.ssd.show()
        self.driving = False

    @prometheus.Registry.register('Rover01', 'W')
    def fast_forward(self, sec=1):
        self.uart1.write('W')
        self.driving = True

    @prometheus.Registry.register('Rover01', 'w')
    def slow_forward(self, sec=1):
        self.uart1.write('w')
        self.driving = True

    @prometheus.Registry.register('Rover01', 'S')
    def fast_backward(self, sec=1):
        self.uart1.write('S')
        self.driving = True

    @prometheus.Registry.register('Rover01', 's')
    def slow_backward(self, sec=1):
        self.uart1.write('s')
        self.driving = True

    @prometheus.Registry.register('Rover01', 'A')
    def turn_left_fast(self, sec=1):
        self.uart1.write('A')
        self.driving = True

    @prometheus.Registry.register('Rover01', 'a')
    def turn_left_slow(self, sec=1):
        self.uart1.write('a')
        self.driving = True

    @prometheus.Registry.register('Rover01', 'D')
    def turn_right_fast(self, sec=1):
        self.uart1.write('D')
        self.driving = True

    @prometheus.Registry.register('Rover01', 'd')
    def turn_right_slow(self, sec=1):
        self.uart1.write('d')
        self.driving = True

    @prometheus.Registry.register('Rover01', 'g')
    def full_stop(self):
        self.uart1.write(b'\x00')
        self.driving = False
