import sys
import os
import machine
import time
import prometheus.pgc as gc
import prometheus
import prometheus.logging as logging
import prometheus.pnetwork

__version__ = '0.1.7a'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()

favicon = b'\x00\x00\x01\x00\x01\x00\x10\x10\x10\x00\x01\x00\x04\x00(\x01\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10' \
          b'\x00\x00\x00 \x00\x00\x00\x01\x00\x04\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
          b'\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x84\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
          b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
          b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
          b'\x00\x00\x00\x00\x00\x00\x00\x00\x10\x10\x10\x00\x00\x00\x00\x00\x10\x01\x01\x00\x00\x00\x00\x00\x10\x01' \
          b'\x01\x00\x00\x00\x00\x01\x10\x01\x01\x00\x11\x00\x01\x00\x10\x00\x10\x01\x00\x10\x01\x00\x00\x00\x00\x01' \
          b'\x00\x10\x01\x00\x00\x00\x00\x01\x00\x10\x01\x00\x00\x00\x00\x00\x11\x00\x11\x10\x00\x00\x00\x00\x00\x00' \
          b'\x00\x00\x00\x00\x00\x01\x11\x01\x01\x01\x00\x10\x00\x01\x00\x01\x11\x01\x01\x10\x00\x01\x00\x01\x01\x01' \
          b'\x10\x10\x00\x01\x00\x00\x10\x01\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\xff\xd5\x00' \
          b'\x00\xff\xda\x00\x00\xff\xda\x00\x00\xff\x9a\x00\x00\xce\xdd\x00\x00\xb6\xff\x00\x00\xb6\xff\x00\x00\xb6' \
          b'\xff\x00\x00\xcc\x7f\x00\x00\xff\xff\x00\x00\x8a\xb7\x00\x00\xb8\xa7\x00\x00\xba\x97\x00\x00\xbd\xb7\x00' \
          b'\x00\xff\xff\x00\x00'
debug = False
os_enabled = True
reset_enabled = True


# noinspection PyMethodMayBeStatic
class Server(object):
    # :type data_commands: dict
    # :type instance: Prometheus
    # :type loopActive: bool
    def __init__(self, instance):
        """
        :type instance: Prometheus
        :param instance: Instance of Prometheus
        """
        self.instance = instance
        self.loop_active = False

    def start(self, **kwargs):
        self.pre_loop(**kwargs)
        self.loop_active = True
        while self.loop_active:
            self.loop_tick(**kwargs)
        self.post_loop(**kwargs)

    def pre_loop(self, **kwargs):
        gc.collect()
        if debug and prometheus.is_micro:
            logging.debug('mem_free before remap: %s' % gc.mem_free())
        self.instance.recursive_remap()
        gc.collect()
        if debug and prometheus.is_micro:
            logging.debug('mem_free after remap: %s' % gc.mem_free())
        self.instance.recursive_cleanup()
        gc.collect()
        if debug and prometheus.is_micro:
            logging.debug('mem_free after cleanup: %s' % gc.mem_free())

    def loop_tick(self, **kwargs):
        gc.collect()

    def post_loop(self, **kwargs):
        pass

    def reply(self, return_value, source=None, **kwargs):
        pass

    def handle_data(self, command, source=None, **kwargs):
        if debug:
            logging.notice('entering Server.handle_data')
        if command is b'' or command is None:
            return

        if debug:
            logging.notice('input: %s' % repr(command))

        # TODO: handle byte data instead of converting to string, might same some memory
        if type(command) is bytes:
            command = command.decode('utf-8')

        command_length = len(command)

        if command == 'cap':
            # capability
            return_value = ''
            for command in self.instance.cached_remap:
                return_value = return_value + command
            self.reply(return_value, source=source, **kwargs)
        elif command == 'uname':
            self.reply(self.uname(), source=source, **kwargs)
        elif command == 'version':
            self.reply(self.version(), source=source, **kwargs)
        elif command == 'sysinfo':
            self.reply(self.sysinfo(), source=source, **kwargs)
        elif command_length > 10 and command[0:8] == 'connect ':
            self.reply(self.connect(command[8:]), source=source, **kwargs)
        elif command in self.instance.cached_remap:
            registered_method = self.instance.cached_remap[command]  # type: prometheus.RegisteredMethod
            return_value = registered_method.method_reference()
            if registered_method.return_type == 'str':
                self.reply(return_value, source=source, **kwargs)
        elif os_enabled and self.handle_data_os(command=command, command_length=command_length,
                                                source=source, **kwargs):
            pass
        elif reset_enabled and command == 'die':
            logging.warn('die command received')
            self.loop_active = False
            return
        elif reset_enabled and command == 'reset':
            logging.warn('reset command received')
            machine.reset()
        else:
            logging.error('invalid cmd: %s' % command)
        if debug:
            logging.notice('exiting Server.handle_data')

        gc.collect()

    def handle_data_os(self, command, command_length, source, **kwargs):
        # extended os module commmands
        cwd = None

        if command_length > 6 and command[0:6] == 'chdir ':
            self.os_safe_function(os.chdir, command[6:])
        elif command_length > 3 and command[0:3] == 'cd ':
            self.os_safe_function(os.chdir, command[3:])
        elif command == 'getcwd':
            cwd = os.getcwd()
            self.reply(self.os_safe_function(os.getcwd), source=source, **kwargs)
        elif prometheus.is_micro and (command == 'listdir' or command == 'ls'):
            self.reply(self.os_safe_function(os.listdir), source=source, **kwargs)
        elif command_length > 8 and command[0:8] == 'listdir ':
            self.reply(self.os_safe_function(os.listdir, command[8:]), source=source, **kwargs)
        elif command_length > 3 and command[0:3] == 'ls ':
            self.reply(self.os_safe_function(os.listdir, command[3:]), source=source, **kwargs)
        elif command_length > 6 and command[0:6] == 'mkdir ':
            self.reply(self.os_safe_function(os.mkdir, command[6:]), source=source, **kwargs)
        elif command_length > 7 and command[0:7] == 'remove ':
            self.reply(self.os_safe_function(os.remove, command[7:]), source=source, **kwargs)
        elif command_length > 7 and command[0:7] == 'rename ' and command[7:].find(' ') is not -1:
            self.reply(self.os_safe_function(os.rename, command[7:].split(' ', 1)), source=source, **kwargs)
        elif command_length > 6 and command[0:6] == 'rmdir ':
            self.reply(self.os_safe_function(os.rmdir, command[6:]), source=source, **kwargs)
        elif command_length > 5 and command[0:5] == 'eval ':
            self.reply(self.os_safe_function(eval, command[5:]), source=source, **kwargs)
        else:
            return False

        gc.collect()
        # prompt, just for the lulz
        if cwd is None:
            cwd = os.getcwd()
        prompt = '%s >' % cwd
        self.reply(prompt, source=source, **kwargs)
        gc.collect()
        return True

    def os_safe_function(self, func, *args):
        try:
            return func(*args)
        except Exception as e:
            return str(e)

    def uname(self):
        if debug:
            logging.notice('Server.uname')
        hostname = self.instance.__class__.__name__
        if prometheus.is_micro:
            un = os.uname()
            return '%s %s %s %s %s MicroPython' % (un[0], hostname, un[2], un[3], un[4])
        else:
            # assume win32 or unix
            import platform
            un = platform.uname()
            return '%s-%s %s@%s %s %s %s CPython' % (un[0], un[2], hostname, un[1], un[3],
                                                     str(sys.version).split(' ')[0], un[4])

    def version(self):
        return '%s/%s' % (__version__, prometheus.__version__)

    def sysinfo(self):
        # struct statvfs {
        #     unsigned long  f_bsize;    /* file system block size */
        #     unsigned long  f_frsize;   /* fragment size */
        #     fsblkcnt_t     f_blocks;   /* size of fs in f_frsize units */
        #     fsblkcnt_t     f_bfree;    /* # free blocks */
        #     fsblkcnt_t     f_bavail;   /* # free blocks for unprivileged users */
        #     fsfilcnt_t     f_files;    /* # inodes */
        #     fsfilcnt_t     f_ffree;    /* # free inodes */
        #     fsfilcnt_t     f_favail;   /* # free inodes for unprivileged users */
        #     unsigned long  f_fsid;     /* file system ID */
        #     unsigned long  f_flag;     /* mount flags */
        #     unsigned long  f_namemax;  /* maximum filename length */
        # };
        if prometheus.is_micro:
            stvfs = os.statvfs('/')
            freespace = (stvfs[0] * stvfs[3]) / 1048576
            gc.collect()
            return '%.2fMB vfs free, %.2fKB mem free' % (freespace, gc.mem_free()/1024)
        else:
            return 'Not implemented for this platform'

    def connect(self, network_info):
        if network_info.find(':') is -1:
            return 'Missing : between ssid and password'

        if not prometheus.is_micro:
            return 'Not implemented for this platform'

        ssid, password = network_info.split(':', 1)
        logging.notice('Connecting to %s' % ssid)

        if not prometheus.pnetwork.sta_if.active():
            prometheus.pnetwork.sta_if.active(True)
            prometheus.pnetwork.sta_if.connect(ssid, password)
        time_start = time.time()
        while not prometheus.pnetwork.sta_if.isconnected() and not (time.time() - time_start) >= 5:
            machine.idle()

        if prometheus.pnetwork.sta_if.isconnected():
            logging.notice('Connected successfully')
            # save config and disable ap
            prometheus.pnetwork.save_config(ssid, password)
            prometheus.pnetwork.ap_if.active(False)
            return 'Connected successfully'
        else:
            logging.notice('Connection timed out')
            return 'Connection timed out'
