import gc
import sys

__version__ = '0.1.1'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()

__black = u'\u001b[30m'
__red = u'\u001b[31m' #
__green = u'\u001b[32m' #
__yellow = u'\u001b[33m' #
__blue = u'\u001b[34m' #
__magenta = u'\u001b[35m'
__cyan = u'\u001b[36m' #
__white = u'\u001b[37m' #
__reset = u'\u001b[0m'


def success(text):
    print('%s%s%s' % (__green, text, __reset))
    gc.collect()


def info(text):
    print('%s%s%s' % (__blue, text, __reset))
    gc.collect()


def notice(text):
    print('%s%s%s' % (__cyan, text, __reset))
    gc.collect()


def warn(text):
    print('%s%s%s' % (__yellow, text, __reset))
    gc.collect()


def error(text):
    print('%s%s%s' % (__red, text, __reset))
    gc.collect()


def debug(text):
    print('%s%s%s' % (__magenta, text, __reset))
    gc.collect()


def boot(srv):
    print('%sversion%s: %s%s%s' % (__magenta, __white, __cyan, srv.version(), __reset))
    print('%suname%s: %s%s%s' % (__magenta, __white, __cyan, srv.uname(), __reset))
    print('%smem_free%s: %s%s%s' % (__magenta, __white, __cyan, gc.mem_free(), __reset))
