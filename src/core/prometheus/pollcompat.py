# coding=utf-8
import prometheus
import prometheus.logging as logging
import gc
import select
import sys

gc.collect()


class PollCompat(object):
    # borrowed from stream.h
    # // These poll ioctl values are compatible with Linux
    POLLIN = 0x0001
    POLLOUT = 0x0004
    POLLERR = 0x0008
    POLLHUP = 0x0010

    def __init__(self):
        self.is_windows = False
        self.is_linux = False

        if prometheus.is_micro:
            self.pollable = select.poll()
        elif sys.platform == 'win32':
            self.is_windows = True
            self.pollable = None
            self.objects = dict()
        elif sys.platform == 'linux2':
            self.is_linux = True
            self.pollable = select.poll()
        else:
            logging.error('Unsupported platform: %s' % sys.platform)

    def register(self, obj, eventmask):
        if self.pollable is not None:
            self.pollable.register(obj, eventmask)
        else:
            self.objects[obj] = eventmask

    def unregister(self, obj):
        if self.pollable is not None:
            self.pollable.unregister(obj)
        else:
            del self.objects[obj]

    def modify(self, obj, eventmask):
        if self.pollable is not None:
            self.pollable.modify(obj, eventmask)
        else:
            self.objects[obj] = eventmask

    def poll(self, timeout=-1, flags=0):
        if prometheus.is_micro:
            # returns iterator
            return self.pollable.ipoll(timeout, flags)
        elif self.is_windows:
            rlist = list()
            wlist = list()
            xlist = list()
            # ignoring xlist for now
            for obj in self.objects:
                eventmask = self.objects[obj]
                if eventmask & PollCompat.POLLIN:
                    rlist.append(obj)
                if eventmask & PollCompat.POLLOUT:
                    wlist.append(obj)
            ravailable, wavailable, xavailable = select.select(rlist, wlist, xlist, timeout)
            returnlist = list()
            for obj in ravailable:
                returnlist.append((obj, PollCompat.POLLIN))
            for obj in wavailable:
                returnlist.append((obj, PollCompat.POLLOUT))
            return returnlist
        elif self.is_linux:
            return self.pollable.poll(timeout)
