import logging
import time


class UART:
    def __init__(self, channel, baudrate=None, pins=None):
        pass

    def write(self, bytes):
        print('UART.write')

    def any(self):
        return 4

    def read(self, length=None):
        return b'test'  # [0:length]


class Pin:
    """'init', 'value', 'toggle', 'id', 'mode', 'pull', 'drive', 'alt_list', 'irq', 'board', 'IN', 'OUT', 'OPEN_DRAIN',
     'ALT', 'ALT_OPEN_DRAIN', 'PULL_UP', 'PULL_DOWN', 'LOW_POWER', 'MED_POWER', 'HIGH_POWER', 'IRQ_FALLING',
     'IRQ_RISING', 'IRQ_LOW_LEVEL', 'IRQ_HIGH_LEVEL'"""

    IN = 0
    OUT = 0
    OPEN_DRAIN = 0
    ALT = 0
    ALT_OPEN_DRAIN = 0
    PULL_UP = 0
    PULL_DOWN = 0
    LOW_POWER = 0
    MED_POWER = 0
    HIGH_POWER = 0
    IRQ_FALLING = 0
    IRQ_RISING = 0
    IRQ_LOW_LEVEL = 0
    IRQ_HIGH_LEVEL = 0

    def __init__(self, pin, mode, alt=None):
        self.pin = pin
        self.mode = mode
        self.alt = alt

    def init(self, pin, mode, alt=None):
        self.pin = pin
        self.mode = mode
        self.alt = alt

    def value(self, value=None):
        if not value:
            print('Pin %s returning default true' % self.pin)
            return True

        print('Pin %s value set to %s' %(self.pin, value))
        return None

    def toggle(self):
        pass


class Timer:
    A = 0
    B = 0
    ONE_SHOT = 0
    PERIODIC = 0
    PWM = 0
    POSITIVE = 0
    NEGATIVE = 0
    TIMEOUT = 0
    MATCH = 0

    def __init__(self, id, mode=None):
        self.id = id
        self.mode = mode
        self.type = None

    def init(self, type):
        self.type = type

    def deinit(self):
        pass

    def channel(self, channel, freq=None, period=None, polarity=0, duty_cycle=0):
        return TimerChannel()


class TimerChannel:
    def __init__(self):
        pass

    def irq(self, handler=None, trigger=None):
        pass

    def duty_cycle(self, duty_cycle):
        pass


class RTC:
    def __init__(self):
        pass

    def init(self, t):
        pass


# make time.sleep_ms valid :D
def sleep_ms(ms):
    time.sleep(ms / 1000.0)

try:
    getattr(time, 'sleep_ms')
except:
    time.sleep_ms = sleep_ms


def idle():
    pass
