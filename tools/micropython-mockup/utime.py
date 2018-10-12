from time import *


def sleep_ms(ms):
    sleep(ms / 1000.0)


def ticks_ms():
    return time() * 1000


def ticks_diff(start, end):
    return start - end
