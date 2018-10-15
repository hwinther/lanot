import prometheus
import machine
import gc
import utime
# import prometheus.pssd1306
import prometheus.pneopixel
import prometheus.logging as logging
import ssd1306

gc.collect()


class Rover01(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        # esp32:
        #  self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), state=False)
        self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), inverted=True)
        self.register(prefix='i', integrated_led=self.integrated_led)

        # self.uart1 = machine.UART(1, baudrate=115200)

        # esp32:
        #  self.i2c = machine.I2C(freq=400000, scl=machine.Pin(22, machine.Pin.OUT),
        #    sda=machine.Pin(21, machine.Pin.OUT))
        self.i2c = machine.I2C(scl=machine.Pin(0), sda=machine.Pin(4), freq=400000)
        logging.notice(self.i2c.scan())
        self.ssd = ssd1306.SSD1306_I2C(width=128, height=64, i2c=self.i2c)

        self.neopixel = prometheus.pneopixel.NeoPixel(machine.Pin(2), 50)
        self.register(prefix='p', neopixel=self.neopixel)

        self.ssd.fill(False)
        self.ssd.text('init', 0, 0)
        self.ssd.show()
        self.driving = 0
        self.last_write = b''

    def write(self, data):
        # self.uart1.write(data)
        i = 0
        while True:
            i += 1
            if i > 5:
                logging.warn('i2c timeout to dev 9')
                break
            try:
                self.i2c.writeto(9, data)
                # to let the device have more time for the next cmd
                # time.sleep(0.1)
                break
            except:
                machine.idle()

    def write_no_repeat(self, data, set_driving=True):
        if set_driving:
            self.driving = utime.ticks_ms()

        if self.last_write == data:
            print('not repeating')
            return

        self.write(data)
        self.last_write = data

    # region directional

    @prometheus.Registry.register('Rover01', 'W')
    def fast_forward(self, sec=1):
        self.write_no_repeat(b'W')

    @prometheus.Registry.register('Rover01', 'w')
    def slow_forward(self, sec=1):
        self.write_no_repeat(b'w')

    @prometheus.Registry.register('Rover01', 'S')
    def fast_backward(self, sec=1):
        self.write_no_repeat(b'S')

    @prometheus.Registry.register('Rover01', 's')
    def slow_backward(self, sec=1):
        self.write_no_repeat(b's')

    @prometheus.Registry.register('Rover01', 'A')
    def turn_left_fast(self, sec=1):
        self.write_no_repeat(b'A')

    @prometheus.Registry.register('Rover01', 'a')
    def turn_left_slow(self, sec=1):
        self.write_no_repeat(b'a')

    @prometheus.Registry.register('Rover01', 'D')
    def turn_right_fast(self, sec=1):
        self.write_no_repeat(b'D')

    @prometheus.Registry.register('Rover01', 'd')
    def turn_right_slow(self, sec=1):
        self.write_no_repeat(b'd')

    @prometheus.Registry.register('Rover01', 'g')
    def full_stop(self):
        self.write_no_repeat(b'\x00', False)
        self.driving = 0

    # endregion

    # region test

    @prometheus.Registry.register('Rover01', 'q')
    def strafe_left_forward_slow(self, sec=1):
        self.write_no_repeat(b'q')

    @prometheus.Registry.register('Rover01', 'Q')
    def strafe_left_forward_fast(self, sec=1):
        self.write_no_repeat(b'Q')

    @prometheus.Registry.register('Rover01', 'e')
    def strafe_right_forward_slow(self, sec=1):
        self.write_no_repeat(b'e')

    @prometheus.Registry.register('Rover01', 'E')
    def strafe_right_forward_fast(self, sec=1):
        self.write_no_repeat(b'E')

    @prometheus.Registry.register('Rover01', 'z')
    def strafe_left_backward_slow(self, sec=1):
        self.write_no_repeat(b'z')

    @prometheus.Registry.register('Rover01', 'Z')
    def strafe_left_backward_fast(self, sec=1):
        self.write_no_repeat(b'Z')

    @prometheus.Registry.register('Rover01', 'c')
    def strafe_right_backward_slow(self, sec=1):
        self.write_no_repeat(b'c')

    @prometheus.Registry.register('Rover01', 'C')
    def strafe_right_backward_fast(self, sec=1):
        self.write_no_repeat(b'C')

    # endregion
