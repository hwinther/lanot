import machine
import gc


__version__ = '0.1.1'
__author__ = 'Hans Christian Winther-Sorensen'

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
            # print('segment[%s].find %s = %s' % (repr(segment), repr(self.endChars), segment.find(self.endChars) != -1))
            if segment == '':
                # the segment empty or only POLYNOMIAL, ignore it
                pass
            elif segment.find(self.endChars) != -1:
                s = segment.split(self.endChars)[0]  # discard everything after
                # print('appending packet')
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
        self.logical_path = None
        self.command_key = None

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
        self.cached_remap = dict()
        self.cached_urls = dict()

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

    def recursive_remap(self, ignorecache=False):
        if not ignorecache and len(self.cached_remap) != 0:
            return self.cached_remap

        self.cached_remap = self.data_commands()
        prometheus_attributes = self.recursive_attributes()  # type: list(PrometheusAttribute)

        for prometheus_attribute in prometheus_attributes:
            attribute_commands = prometheus_attribute.instance.data_commands(data_value_prefix=prometheus_attribute.prefix)
            for akey in attribute_commands.keys():
                self.cached_remap[akey] = attribute_commands[akey]
        return self.cached_remap

    def data_commands(self, data_value_prefix=None):
        commands = dict()

        command_keys = list(self.commands.keys())
        command_keys.sort()
        for key in command_keys:
            value = self.commands[key]
            if isinstance(value, RegisteredMethod):
                if data_value_prefix:
                    command_key = data_value_prefix + value.data_value
                else:
                    command_key = value.data_value
                if command_key in commands.keys():
                    print('Warning: overwriting reference for data_value %s' % command_key)
                value.command_key = command_key
                commands[command_key] = value
                value.logical_path = ''
                if value.instance:
                    logical_path = value.instance.logical_path()
                    value.logical_path = logical_path
                print('%s\t-> %s\t%s\t%s' % (command_key, value.method_name, value.logical_path, value.method_reference))

        return commands

    def update_urls(self, ignorecache=False):
        if not ignorecache and len(self.cached_urls) != 0:
            return

        for key in self.cached_remap.keys():
            value = self.cached_remap[key]
            url = '/'.join(value.logical_path.split('.')).replace('root/', 'api/').encode('ascii')
            url = b'/' + url + b'/' + value.method_name.encode('ascii')
            self.cached_urls[url] = value


class Led(Prometheus):
    def __init__(self, pin, inverted=False, state=False):
        """
        :type pin: machine.Pin
        :type inverted: bool
        :type state: bool
        """
        Prometheus.__init__(self)
        self.pin = pin
        self.inverted = inverted
        # set initial state if it differs from what we have
        if self.pin.value() is not state:
            if self.inverted:
                self.pin.value(not state)
            else:
                self.pin.value(state)

    @Registry.register('Led', '1')
    def on(self):
        if self.inverted:
            self.pin.value(False)
        else:
            self.pin.value(True)

    @Registry.register('Led', '0')
    def off(self):
        if self.inverted:
            self.pin.value(True)
        else:
            self.pin.value(False)

    @Registry.register('Led', 'S', 'OUT')
    def state(self):
        if self.inverted:
            return not self.pin.value()
        else:
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
