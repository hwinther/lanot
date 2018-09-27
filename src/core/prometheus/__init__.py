# coding=utf-8
import machine
import gc
import sys
import prometheus.logging as logging

__version__ = '0.1.9'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()

is_micro = sys.platform in ['esp8266', 'esp32', 'WiPy']
# turn this on to debug command byte assignments
data_debug = False


def parse_args(args_str):
    if len(args_str) == 0:
        return dict()

    args = dict()
    for query_segment in args_str.split(b'&'):
        if query_segment.find(b'=') != -1:
            key, value = query_segment.split(b'=', 1)
            args[key.decode('utf-8')] = value.decode('utf-8')
        else:
            args[query_segment.decode('utf-8')] = True
    return args


def args_to_bytes(args):
    if len(args) == 0:
        return b''

    values = list()
    for key, value in args.items():
        values.append(b'%s=%s' % (key, value))
    return b'&'.join(values)
    # return b'&'.join([b'{0}={1}'.format(key, value) for (key, value) in args.items()])


class BufferPacket(object):
    def __init__(self, packet, args):
        self.packet = packet
        self.args = args
        print('packet - packet=%s args=%s' % (packet, args))


class Buffer(object):
    """
    Copied from RadioNetwork.Handlers.PacketParser
    :type Packets: list(str)
    :type packetBuffer: str
    :type split_chars: str
    :type end_chars: str
    """
    def __init__(self, split_chars, end_chars):
        """
        :rtype: Buffer
        """
        self.Packets = list()
        self.packetBuffer = b''
        if type(split_chars) is str:
            split_chars = split_chars.encode('ascii')
        self.split_chars = split_chars
        if type(end_chars) is str:
            end_chars = end_chars.encode('ascii')
        self.end_chars = end_chars

    def parse(self, packetdata):
        # type: (str) -> None
        # TODO: add cleanup routine, clear buffer after x seconds
        # TODO: do something about large packetdata sizes?
        # TODO: e.g. only take 100 char buffers at a time, prune at 100 chars when adding rest to rest buffer
        # TODO: maybe use utf-8 instead of ascii? and it should be a constant so it cant differ in any one location
        if type(packetdata) is str:
            packetdata = packetdata.encode('ascii')

        if packetdata == b'':
            return

        self.packetBuffer += packetdata
        rest = b''
        # logging.notice('for segment in split on %s len=%d' %
        #  (self.splitChars, len(self.packetBuffer.split(self.splitChars))))
        for segment in self.packetBuffer.split(self.split_chars):
            # logging.notice('segment[%s].find %s = %s' %
            #  (repr(segment), repr(self.endChars), segment.find(self.endChars) != -1))
            if segment == b'':
                # the segment empty or only POLYNOMIAL, ignore it
                pass
            elif segment.find(self.end_chars) != -1:
                packet, args = segment.split(self.end_chars, 1)  # discard everything after
                # logging.notice('appending packet')
                self.Packets.append(BufferPacket(packet, args=args))
            else:
                rest += self.split_chars + segment
            gc.collect()

        if len(rest) > 100:
            # logging.notice('pruning packetBuffer rest')
            rest = rest[0:20]
        self.packetBuffer = rest
        gc.collect()

    def pop(self):
        # type: () -> BufferPacket
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
        return u"RegisteredMethod(class_name='%s' method_name='%s' method_reference=%s data_value='%s' return_type=%s)"\
               % (self.class_name, self.method_name, self.method_reference, self.data_value, self.return_type)


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
        self.prefix_cache = dict()

        if self.__class__.__name__ in Registry.r:
            for key in Registry.r[self.__class__.__name__]:
                value = Registry.r[self.__class__.__name__][key]
                method_reference = getattr(self, value.method_name)
                # logging.notice('method ref: %s %s %d' %(method_reference, self, len(self.commands)))
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
        prometheus_attributes = self.recursive_attributes()

        self.prefix_cache = dict()
        for prometheus_attribute in prometheus_attributes:  # type: PrometheusAttribute
            # logging.notice('prometheus_attribute=%s' % str(prometheus_attribute))
            prefix = prometheus_attribute.prefix
            # logging.notice('debug, prefix=%s' % repr(prefix))
            if prometheus_attribute.prefix is not None:
                self.prefix_cache[prometheus_attribute.instance.__class__.__name__] = prefix
            else:
                for key in self.prefix_cache.keys():
                    if prometheus_attribute.instance.__class__.__name__.find(key) != -1:
                        prefix = self.prefix_cache[key]
                        # logging.notice('found cached prefix: %s' % prefix)
                        break
            attribute_commands = prometheus_attribute.instance.data_commands(data_value_prefix=prefix)
            for akey in attribute_commands.keys():
                # logging.notice('debug, akey=%s' % akey)
                self.cached_remap[akey] = attribute_commands[akey]

        return self.cached_remap

    def recursive_cleanup(self):
        for key in self.attributes.keys():
            self.attributes[key].instance.recursive_cleanup()
            # value = self.attributes[key]  # :type PrometheusAttribute
            # instances.append(value)
            # instances.extend(value.instance.recursive_attributes())
        self.commands = dict()
        self.attributes = dict()
        self.prefix_cache = dict()

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
                    logging.warn('Warning: overwriting reference for data_value %s' % command_key)
                value.command_key = command_key
                commands[command_key] = value
                value.logical_path = ''
                if value.instance:
                    logical_path = value.instance.logical_path()
                    value.logical_path = logical_path
                if data_debug:
                    logging.notice('%s\t-> %s\t%s\t%s' % (command_key, value.method_name, value.logical_path,
                                                          value.method_reference))

        return commands

    def update_urls(self, ignorecache=False):
        if not ignorecache and len(self.cached_urls) != 0:
            return

        for key in self.cached_remap.keys():
            value = self.cached_remap[key]
            url = '/'.join(value.logical_path.split('.')).replace('root/', 'api/').encode('ascii')
            url = url + b'/' + value.method_name.encode('ascii')
            self.cached_urls[url] = value

    def custom_command(self, command, reply, source, context, **kwargs):
        # by default, do nothing
        # usage: reply(return_value, source, **kwargs)
        return False


class PrometheusAttribute(object):
    def __init__(self, instance, prefix):
        """
        :param instance: Prometheus
        :param prefix: str
        """
        self.instance = instance
        self.prefix = prefix

    def __str__(self):
        return 'PrometheusAttribute - Instance: %s Prefix: %s' % (self.instance, self.prefix)


class Led(Prometheus):
    def __init__(self, pin, inverted=False, state=None):
        """
        :type pin: machine.Pin
        :type inverted: bool
        :type state: bool
        """
        Prometheus.__init__(self)
        self.pin = pin
        self.inverted = inverted
        # set initial state if it differs from what we have
        if state is not None and self.pin.value() is not state:
            if self.inverted:
                self.pin.value(not state)
            else:
                self.pin.value(state)

    @Registry.register('Led', '1')
    def on(self, **kwargs):
        if self.inverted:
            self.pin.value(False)
        else:
            self.pin.value(True)

    @Registry.register('Led', '0')
    def off(self, **kwargs):
        if self.inverted:
            self.pin.value(True)
        else:
            self.pin.value(False)

    @Registry.register('Led', 'v', 'OUT')
    def value(self, **kwargs):
        # the equal/not equal operators have to be used to get truthyness ('1 is not True' will not work)
        if self.inverted:
            return self.pin.value() != True
        else:
            return self.pin.value() == True


class Digital(Prometheus):
    def __init__(self, pin, inverted=False):
        """
        :type pin: machine.Pin
        :type inverted: bool
        """
        Prometheus.__init__(self)
        self.pin = pin
        self.inverted = inverted

    @Registry.register('Digital', 'v', 'OUT')
    def value(self, **kwargs):
        if self.inverted:
            return self.pin.value() != True
        else:
            return self.pin.value() == True


class Adc(Prometheus):
    def __init__(self, pin):
        """
        TODO: Warning - pin in analog mode requires max 1.8v, use volt divider to ensure this
        # not always::type pin: int
        """
        Prometheus.__init__(self)
        self.pin = pin
        self.adc = machine.ADC(pin)

    @Registry.register('Adc', 'r', 'OUT')
    def read(self, **kwargs):
        return self.adc.read()

# TODO: when adding new device subclasses, concidering splitting them all into submodules
