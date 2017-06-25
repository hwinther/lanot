import machine
import gc
import time
import servo
import prometheus
import LightControl


gc.collect()

# region Constants
# micropython.alloc_emergency_exception_buf(100)

# Servo specific constants
PULSE_MIN = 900  # in
PULSE_MAX = 2100  # in
FREQUENCY = 50  # Hz
ROTATIONAL_RANGE_100 = 12000  # 120deg * 100

LS_FULL_STOP = -90 * 100
LS_FAST_BACKWARD = 40 * 100
LS_SLOW_BACKWARD = 50 * 100
# 60 = idle
LS_SLOW_FORWARD = 70 * 100
LS_FAST_FORWARD = 80 * 100

RS_FULL_STOP = -90 * 100
RS_FAST_BACKWARD = 80 * 100
RS_SLOW_BACKWARD = 70 * 100
# 60 = idle
RS_SLOW_FORWARD = 50 * 100
RS_FAST_FORWARD = 40 * 100
# endregion


class Tank(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.ls = servo.Servo(10, FREQUENCY, ROTATIONAL_RANGE_100, PULSE_MIN, PULSE_MAX)
        self.rs = servo.Servo(9, FREQUENCY, ROTATIONAL_RANGE_100, PULSE_MIN, PULSE_MAX)
        self.lightControl = LightControl.LightControl(1, baudrate=4800)
        self.register(lightControl=self.lightControl)
        self.sensors = machine.UART(0, baudrate=2400, pins=('GP1', 'GP2'))
        self.led_blue = prometheus.Led(machine.Pin('GP16', mode=machine.Pin.OUT))
        self.register(led_blue=self.led_blue)
        self.led_red = prometheus.Led(machine.Pin('GP11', mode=machine.Pin.OUT))
        self.register(led_red=self.led_red)

    @prometheus.Registry.register('Tank', 'W')
    def fast_forward(self, sec=1):
        self.ls.angle(LS_FAST_FORWARD)
        self.rs.angle(RS_FAST_FORWARD)
        time.sleep(sec)
        self.full_stop()

    @prometheus.Registry.register('Tank', 'w')
    def slow_forward(self, sec=1):
        self.ls.angle(LS_SLOW_FORWARD)
        self.rs.angle(RS_SLOW_FORWARD)
        time.sleep(sec)
        self.full_stop()

    @prometheus.Registry.register('Tank', 'S')
    def fast_backward(self, sec=1):
        self.ls.angle(LS_FAST_BACKWARD)
        self.rs.angle(RS_FAST_BACKWARD)
        time.sleep(sec)
        self.full_stop()

    @prometheus.Registry.register('Tank', 's')
    def slow_backward(self, sec=1):
        self.ls.angle(LS_SLOW_BACKWARD)
        self.rs.angle(RS_SLOW_BACKWARD)
        time.sleep(sec)
        self.full_stop()

    @prometheus.Registry.register('Tank', 'A')
    def turn_left_fast(self, sec=1):
        self.ls.angle(LS_FAST_BACKWARD)
        self.rs.angle(RS_FAST_FORWARD)
        time.sleep(sec)
        self.full_stop()

    @prometheus.Registry.register('Tank', 'a')
    def turn_left_slow(self, sec=1):
        self.ls.angle(LS_SLOW_BACKWARD)
        self.rs.angle(RS_SLOW_FORWARD)
        time.sleep(sec)
        self.full_stop()

    @prometheus.Registry.register('Tank', 'D')
    def turn_right_fast(self, sec=1):
        self.ls.angle(LS_FAST_FORWARD)
        self.rs.angle(RS_FAST_BACKWARD)
        time.sleep(sec)
        self.full_stop()

    @prometheus.Registry.register('Tank', 'd')
    def turn_right_slow(self, sec=1):
        self.ls.angle(LS_SLOW_FORWARD)
        self.rs.angle(RS_SLOW_BACKWARD)
        time.sleep(sec)
        self.full_stop()

    @prometheus.Registry.register('Tank', 'g')
    def full_stop(self):
        self.ls.angle(LS_FULL_STOP)
        self.rs.angle(RS_FULL_STOP)

    @prometheus.Registry.register('Tank', 'b')
    def blink_lights(self, ms=200):
        # lights.write('5\n')
        self.lightControl.all_on()
        time.sleep_ms(ms)
        # lights.write('0\n')
        self.lightControl.all_off()

    def sensor_reading(self):
        if self.sensors.any() < 4:
            return
        b0 = None
        b1 = None
        b2 = None
        b3 = None
        first = False
        second = False
        found = False
        i = 0
        for x in self.sensors.read():
            print(repr(x), repr(b0), repr(b1), repr(b2), repr(b3), repr(first), repr(second), repr(i))
            if x == 10:  # \n
                first = True
                i = 0
            elif first and i == 1:
                b0 = x
            elif first and i == 2:
                b1 = x
            elif first and i == 3 and x == 9:  # \t
                first = False
                second = True
            elif second and i == 4:
                b2 = x
            elif second and i == 5:
                b3 = x
                second = False
                found = True
            i = i + 1
        if found:
            print('Sensor ranges: %d (%d) %d (%d)' % (b0, b1, b2, b3))
            return b0, b2
