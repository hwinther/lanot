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
        self.driving = 0

    @prometheus.Registry.register('Rover01', 'W')
    def fast_forward(self, sec=1):
        self.uart1.write('W')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'w')
    def slow_forward(self, sec=1):
        self.uart1.write('w')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'S')
    def fast_backward(self, sec=1):
        self.uart1.write('S')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 's')
    def slow_backward(self, sec=1):
        self.uart1.write('s')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'A')
    def turn_left_fast(self, sec=1):
        self.uart1.write('A')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'a')
    def turn_left_slow(self, sec=1):
        self.uart1.write('a')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'D')
    def turn_right_fast(self, sec=1):
        self.uart1.write('D')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'd')
    def turn_right_slow(self, sec=1):
        self.uart1.write('d')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'g')
    def full_stop(self):
        self.uart1.write(b'\x00')
        self.driving = 0

    # region test

    @prometheus.Registry.register('Rover01', 'q')
    def strafe_left_forward_slow(self, sec=1):
        self.uart1.write('q')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'Q')
    def strafe_left_forward_fast(self, sec=1):
        self.uart1.write('Q')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'e')
    def strafe_right_forward_slow(self, sec=1):
        self.uart1.write('e')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'E')
    def strafe_right_forward_fast(self, sec=1):
        self.uart1.write('E')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'z')
    def strafe_left_backward_slow(self, sec=1):
        self.uart1.write('z')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'Z')
    def strafe_left_backward_fast(self, sec=1):
        self.uart1.write('Z')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'c')
    def strafe_right_backward_slow(self, sec=1):
        self.uart1.write('c')
        self.driving = time.time()

    @prometheus.Registry.register('Rover01', 'C')
    def strafe_right_backward_fast(self, sec=1):
        self.uart1.write('C')
        self.driving = time.time()

    # endregion
