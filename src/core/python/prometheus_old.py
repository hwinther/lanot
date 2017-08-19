import machine


class RegisteredMethod:
    def __init__(self, class_name, method_name, method_reference, data_value, return_type):
        self.class_name = class_name
        self.method_name = method_name
        self.method_reference = method_reference
        self.data_value = data_value
        self.return_type = return_type

    def __repr__(self):
        return u"RegisteredMethod(class_name='%s' method_name='%s' method_reference=%s data_value='%s' return_type=%s)" % (self.class_name, self.method_name, self.method_reference, self.data_value, self.return_type)


class Registry:
    r = dict()

    @classmethod
    def register(cls, *args):
        # class_name = inspect.getouterframes(inspect.currentframe())[1][3]

        def decorator(fn):
            class_name = args[0]
            if class_name not in cls.r:
                cls.r[class_name] = dict()
            data_value = args[1]
            return_type = None
            if len(args) == 3:
                return_type = 'str'
            cls.r[class_name][fn.__name__] = RegisteredMethod(class_name=class_name, method_name=fn.__name__,
                                                              method_reference=None, data_value=data_value,
                                                              return_type=return_type)
            return fn

        return decorator


class Prometheus:
    def __init__(self):
        self.commands = dict()
        if self.__class__.__name__ in Registry.r:
            for key in Registry.r[self.__class__.__name__]:
                value = Registry.r[self.__class__.__name__][key]
                method_reference = getattr(self, value.method_name)
                # print('method ref: %s %s %d' %(method_reference, self, len(self.commands)))
                self.commands[key] = RegisteredMethod(class_name=value.class_name, method_name=value.method_name,
                                                      method_reference=method_reference, data_value=value.data_value,
                                                      return_type=value.return_type)

    def register(self, **kwargs):
        for key in kwargs:
            self.commands[key] = kwargs[key].commands

    def start_socket_server(self, remap=True):
        data_commands = dict()
        map_data_commands(self.commands, data_commands, remap)

        import socket
        host = ''  # Symbolic name meaning all available interfaces
        port = 9195  # Arbitrary non-privileged port
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))
        print('listening on *:%d' % (port))
        looping = True
        while looping:
            data, addr = s.recvfrom(1024)
            print('recv', addr)
            for cmd in data.decode('utf-8').split('\n'):
                if cmd == '':
                    continue

                print('input:', cmd)

                if cmd in data_commands:
                    data_commands[cmd]()
                elif cmd == 'die':
                    print('die command received')
                    looping = False
                    break
                # if cmd == 'w':
                #     tank.fast_forward(1)
                # elif cmd == 's':
                #     tank.fast_backward(1)
                # elif cmd == 'a':
                #     tank.turn_left_fast(1)
                # elif cmd == 'd':
                #     tank.turn_right_fast(1)
                # elif cmd == '0':  # all leds off
                #     lights.write('0\n')
                # elif cmd == '1':  # bright led on
                #     lights.write('2\n')
                # elif cmd == '2':  # right led
                #     lights.write('3\n')
                # elif cmd == '3':  # left led
                #     lights.write('3\n')
                # elif cmd == '4':  # right and left led
                #     lights.write('4\n')
                # elif cmd == '5':  # all leds on
                #     lights.write('5\n')
                # elif cmd == '9':
                #     reading = tank.sensor_reading()
                #     if reading is None:
                #         s.sendto(b'No reading', addr)
                #     else:
                #         s.sendto(b'Reading: left=%dcm right=%dcm', addr)
                else:
                    print('invalid cmd', cmd)
        s.close()


class Led(Prometheus):
    def __init__(self, pin):
        """
        :type pin: machine.Pin
        """
        Prometheus.__init__(self)
        self.pin = pin

    @Registry.register('Led', '1')
    def on(self):
        self.pin.value(True)

    @Registry.register('Led', '0')
    def off(self):
        self.pin.value(False)

    @Registry.register('Led', 'S', 'OUT')
    def state(self):
        return self.pin.value()


class InputOutputProxy(Prometheus):
    def __init__(self, send, recv):
        # Could pass on send, recv method refs an template inherit self to be able to issubclassof check these
        Prometheus.__init__(self)
        self.send = send
        self.recv = recv


class RemoteTemplate(Prometheus):
    def __init__(self):
        Prometheus.__init__(self)

    def send(self, data):
        print('send: ' +repr(data))

    def recv(self, buffersize=None):
        print('recv buffersize=%s' % buffersize)
        return None


class RemapCounter:
    def __init__(self, value):
        # :type value: int
        self.counter = value

    def next(self):
        self.counter += 1
        return self.counter -1


def map_data_commands(commands, data_commands, remap=True, remap_counter=None, context='self'):
    """
    :type commands: dict
    :type data_commands: dict
    :type remap: bool
    :type remap_counter: RemapCounter
    :type context: str
    """
    if remap_counter is None:
        remap_counter = RemapCounter(65)

    command_keys = list(commands.keys())
    command_keys.sort()

    for key in command_keys:
        value = commands[key]
        if isinstance(value, RegisteredMethod):
            if not remap:
                command_key = value.data_value
            else:
                # re-map the bytes
                command_key = chr(remap_counter.next())
            if command_key in data_commands.keys():
                print('Warning: overwriting reference for data_value %s' % command_key)
            data_commands[command_key] = value.method_reference
            print('Added reference for %s.%s (%s) data_value %s (%d)' % (context, value.method_name, value.method_reference, command_key, ord(command_key)))
        elif isinstance(value, dict):
            # print('its a dict, going derper: %s' % value)
            map_data_commands(value, data_commands, remap, remap_counter, context=key)
