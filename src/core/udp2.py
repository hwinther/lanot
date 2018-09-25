# coding=utf-8
import socket
import gc
import select
import sys
import time
import machine
import prometheus
import prometheus.server.socketserver as socketserver
import prometheus.logging as logging
import prometheus.psocket

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


class UdpSocketServer2(socketserver.SocketServer):
    def __init__(self, instance, socketwrapper=None):
        socketserver.SocketServer.__init__(self, instance, socketwrapper)
        self.socket = self.socketwrapper(socket.AF_INET, socket.SOCK_DGRAM)
        self.split_chars = '\n'
        self.end_chars = '\r'
        self.buffers = dict()  # :type dict(Buffer)
        self.poll_compat = PollCompat()

    def start(self, bind_host='', bind_port=9195, **kwargs):
        socketserver.SocketServer.start(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

    def pre_loop(self, bind_host='', bind_port=9195, **kwargs):
        socketserver.SocketServer.pre_loop(self, bind_host=bind_host, bind_port=bind_port, **kwargs)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except prometheus.psocket.socket_error:
            logging.warn('could not bind with reuse flag')  # TODO: look into this
        self.socket.bind((bind_host, bind_port))
        self.socket.setblocking(0)
        logging.success('listening on %s:%d (udp)' % (bind_host, bind_port))
        self.poll_compat.register(self.socket, PollCompat.POLLIN)

    def loop_tick(self, **kwargs):
        socketserver.SocketServer.loop_tick(self, **kwargs)

        # TODO: buffer could be higher, but then the buffer class needs to prune its rest buffer over time
        # should probably bear in mind that the underlying fd buffer on mpy platforms will be limited to around
        #  500 bytes in the first place
        data, addr = None, None
        for pair in self.poll_compat.poll(0):
            if PollCompat.POLLIN & pair[1]:
                # its input (what else could it be?:)
                data, addr = self.socket.recvfrom(500)

        if data is None:
            return

        logging.notice('recv %s from %s' % (repr(data), repr(addr)))

        if addr not in self.buffers.keys():
            if prometheus.server.debug:
                logging.debug('Creating new buffer context')
            # TODO: clean up buffer contexts over time!
            # TODO: this must be done in Tcp implementation also
            if len(self.buffers) > 2:
                if prometheus.server.debug:
                    logging.debug('Cleaning up old buffers')
                del self.buffers
                self.buffers = dict()
                gc.collect()
            self.buffers[addr] = prometheus.Buffer(split_chars=self.split_chars, end_chars=self.end_chars)

        if type(data) is str:
            # convert to bytes?
            data = data.decode('ascii')
        self.buffers[addr].parse(data)

        while True:
            command = self.buffers[addr].pop()
            if command is None:
                # logging.notice('Breaking command loop')
                break
            if type(command) is bytes:
                command = command.decode('ascii')
            if prometheus.server.debug:
                logging.debug('Calling handle data')
            self.handle_data(command, addr)

        gc.collect()

        # to reduce cpu/energy usage
        # if prometheus.is_micro:
        #     machine.idle()
        # else:
        #     time.sleep(0.001)

    def post_loop(self, **kwargs):
        socketserver.SocketServer.post_loop(self, **kwargs)

        self.socket.close()

    def reply(self, return_value, source=None, **kwargs):
        socketserver.SocketServer.reply(self, return_value, **kwargs)

        if type(return_value) is str:
            return_value = return_value.encode('ascii')
        elif type(return_value) is bytes:
            pass
        else:
            return_value = b'%s' % return_value
        logging.notice('Returning %s to %s' % (return_value, repr(source)))
        self.socket.sendto(b'%s%s%s' % (return_value, self.end_chars.encode('ascii'),
                                        self.split_chars.encode('ascii')), source)
        gc.collect()
