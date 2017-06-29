import machine
import socket
import gc


gc.collect()


class Buffer(object):
    """
    Copied from RadioNetwork.Handlers.PacketParser
    :type Packets: list(str)
    :type packetBuffer: str
    :type splitChars: str
    :type endChars: str
    """
    def __init__(self, split_chars, end_chars):
        """
        :rtype: Buffer
        """
        self.Packets = list()
        self.packetBuffer = ''
        self.splitChars = split_chars
        self.endChars = end_chars

    def parse(self, packetdata):
        # type: (str) -> None
        # TODO: add cleanup routine, clear buffer after x seconds
        if packetdata == '':
            return

        self.packetBuffer += packetdata
        rest = ''
        # print('for segment in split on %s len=%d' % (self.splitChars, len(self.packetBuffer.split(self.splitChars))))
        for segment in self.packetBuffer.split(self.splitChars):
            print('segment[%s].find %s = %s' % (repr(segment), repr(self.endChars), segment.find(self.endChars) != -1))
            if segment == '':
                # the segment empty or only POLYNOMIAL, ignore it
                pass
            elif segment.find(self.endChars) != -1:
                s = segment.split(self.endChars)[0]  # discard everything after
                print('appending packet')
                self.Packets.append(s)
            else:
                rest += self.splitChars + segment
        self.packetBuffer = rest

    def pop(self):
        # rtype: str
        if len(self.Packets) != 0:
            return self.Packets.pop(0)
        return None


class RegisteredMethod(object):
    def __init__(self, class_name, method_name, method_reference, data_value, return_type, instance=None):
        self.class_name = class_name
        self.method_name = method_name
        self.method_reference = method_reference
        self.data_value = data_value
        self.return_type = return_type
        self.instance = instance

    def __repr__(self):
        return u"RegisteredMethod(class_name='%s' method_name='%s' method_reference=%s data_value='%s' return_type=%s)" % (self.class_name, self.method_name, self.method_reference, self.data_value, self.return_type)


class Registry(object):
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


class PrometheusAttribute(object):
    def __init__(self, instance, prefix):
        """
        :param instance: Prometheus
        :param prefix: str
        """
        self.instance = instance
        self.prefix = prefix


class Prometheus(object):
    def __init__(self, parent=None, name=None):
        """
        :param parent: Prometheus
        :param name: str
        """
        self.parent = parent
        self.name = name
        self.commands = dict()
        self.attributes = dict()
        if self.__class__.__name__ in Registry.r:
            for key in Registry.r[self.__class__.__name__]:
                value = Registry.r[self.__class__.__name__][key]
                method_reference = getattr(self, value.method_name)
                # print('method ref: %s %s %d' %(method_reference, self, len(self.commands)))
                self.commands[key] = RegisteredMethod(class_name=value.class_name, method_name=value.method_name,
                                                      method_reference=method_reference, data_value=value.data_value,
                                                      return_type=value.return_type, instance=self)

    def path(self, paths=None):
        if paths is None:
            paths = list()
        if self.name is None:
            paths.append('root')
        else:
            paths.append(self.name)
        if self.parent is not None:
            self.parent.path(paths)
        return paths

    def logical_path(self):
        path = self.path()
        path.reverse()
        return '.'.join(path)

    def register(self, prefix=None, **kwargs):
        for key in kwargs:
            value = kwargs[key]  # type: Prometheus
            value.parent = self
            value.name = key
            self.attributes[key] = PrometheusAttribute(value, prefix)

    def recursive_attributes(self):
        instances = list()
        for key in self.attributes.keys():
            value = self.attributes[key]  # :type PrometheusAttribute
            instances.append(value)
            instances.extend(value.instance.recursive_attributes())
        return instances

    def recursive_remap(self):  # remap=True
        # remap_counter = None
        # if remap:
        #     remap_counter = RemapCounter(65)
        commands = self.data_commands()

        # TODO: clean up the whole map thing? it doesnt help now
        prometheus_attributes = self.recursive_attributes()  # type: list(PrometheusAttribute)
        # blah = dict()
        # for prometheus_attribute in prometheus_attributes:
        #     # print('%s %s' % (repr(prometheus_attribute.instance), repr(prometheus_attribute.prefix)))
        #     blah[prometheus_attribute.instance.logical_path()] = prometheus_attribute

        # keys = blah.keys()
        # keys.sort()
        # prefix = None

        # for key in keys:
        #     prometheus_attribute = blah[key]
        for prometheus_attribute in prometheus_attributes:
            # if remap:
            #     prefix = chr(remap_counter.next())
            attribute_commands = prometheus_attribute.instance.data_commands(data_value_prefix=prometheus_attribute.prefix)
            # data_value_prefix=prefix
            # print key, attribute_commands
            for akey in attribute_commands.keys():
                commands[akey] = attribute_commands[akey]
        return commands

    def data_commands(self, data_value_prefix=None):  # remap_counter=None,
        commands = dict()

        command_keys = list(self.commands.keys())
        command_keys.sort()
        for key in command_keys:
            value = self.commands[key]
            if isinstance(value, RegisteredMethod):
                # if remap_counter:
                #     command_key = chr(remap_counter.next()) + value.data_value
                if data_value_prefix:
                    command_key = data_value_prefix + value.data_value
                else:
                    command_key = value.data_value
                if command_key in commands.keys():
                    print('Warning: overwriting reference for data_value %s' % command_key)
                commands[command_key] = value
                logical_path = ''
                if value.instance:
                    logical_path = value.instance.logical_path()
                print('%s\t-> %s\t%s\t%s' % (command_key, value.method_name, logical_path, value.method_reference))

        return commands


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


class Adc(Prometheus):
    def __init__(self, pin):
        """
        TODO: Warning - pin in analog mode requires max 1.8v, use volt divider to ensure this
        :type pin: int
        """
        Prometheus.__init__(self)
        self.pin = pin
        self.adc = machine.ADC(pin)

    @Registry.register('Adc', 'r', 'OUT')
    def read(self):
        return self.adc.read()


class InputOutputProxy(Prometheus):
    def __init__(self, send, recv):
        # Could pass on send, recv method refs an template inherit self to be able to issubclassof check these
        Prometheus.__init__(self)
        self.send = send
        self.recv = recv
        # POST_INIT

    # cut

    # noinspection PyPep8Naming
    @Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self):
        self.send(b'VALUE')

    # noinspection PyPep8Naming
    @Registry.register('CLASS_NAME', 'VALUE', 'OUT')
    def METHOD_NAME_OUT(self):
        self.send(b'VALUE')
        # TODO: determine output size declaratively in source?
        return self.recv(10)


class RemoteTemplate(Prometheus):
    def __init__(self):
        Prometheus.__init__(self)

    def send(self, data):
        print('send: %s' % repr(data))

    def recv(self, buffersize=None):
        print('recv buffersize=%s' % buffersize)
        return None


class RemapCounter(object):
    def __init__(self, value):
        # :type value: int
        self.counter = value

    def next(self):
        self.counter += 1
        return self.counter - 1
