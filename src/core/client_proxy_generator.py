# coding=utf-8
import os
import sys
import re
import gc
import inspect
import machine
import socket
import datetime
import time
import json
import prometheus
import prometheus.crypto
import prometheus.misc
import prometheus.psocket
import prometheus.logging as logging

__version__ = '0.1.8d'
__author__ = 'Hans Christian Winther-Sorensen'

# TODO: move these template classes to another python file? perhaps one for each via python modules
# TODO: none of the inheritors of prometheus.misc.RemoteTemplate call super outside of init
# TODO: in general just rewrite this so that it can be reused

gc.collect()


class SerialTemplate(prometheus.misc.RemoteTemplate):
    def __init__(self, channel, baudrate):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.uart = machine.UART(channel, baudrate=baudrate)
        self.buffer = prometheus.Buffer(split_chars=b'\n', end_chars=b'\r')
        # POST_INIT

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)
        self.uart.write(data + self.buffer.end_chars + args + self.buffer.split_chars)

    def recv(self, buffersize=None):
        if buffersize:
            self.buffer.parse(self.uart.read(buffersize))
        else:
            self.buffer.parse(self.uart.read())
        bufferpacket = self.buffer.pop()
        if bufferpacket is None:
            return None
        return bufferpacket.packet

    def recv_timeout(self, buffersize, timeout):
        # TODO: actually implement this
        raise Exception('Not implemented due to lazyness')

    # cut

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self, **kwargs):
        self.send(b'VALUE', **kwargs)

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE', str)
    def METHOD_NAME_OUT(self, **kwargs):
        self.send(b'VALUE', **kwargs)
        packet = self.recv(10)
        if packet is not None:
            return packet
        # TODO: replace this with something better?
        time.sleep(0.5)
        return self.resolve_response(self.buffer.pop().packet)


class UdpTemplate(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host='', bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((bind_host, bind_port))
        logging.info('listening on %s:%d' % (bind_host, bind_port))
        self.socket.settimeout(0)
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.splitChars = b'\n'
        self.endChars = b'\r'
        # POST_INIT

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)
        self.socket.sendto(data + self.endChars + args + self.splitChars, self.remote_addr)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except prometheus.psocket.socket_error:
            # they said i could use OSError here, they lied (cpython/micropython issue, solve it later if necessary)
            return None, None

    def recv_once(self, buffersize=10):
        data, addr = self.try_recv(buffersize)
        if data is None:
            return None
        if addr not in self.buffers:
            self.buffers[addr] = prometheus.Buffer(split_chars=self.splitChars, end_chars=self.endChars)
        self.buffers[addr].parse(data)
        bufferpacket = self.buffers[addr].pop()
        if bufferpacket is None:
            return None
        return bufferpacket.packet

    def recv(self, buffersize=20):
        return self.recv_timeout(buffersize, 0.5)

    def recv_timeout(self, buffersize, timeout):
        """
        :param buffersize: int
        :param timeout: float
        :return: str
        """
        timestamp = time.time()
        while (time.time() - timestamp) < timeout:
            # logging.debug('try recv: %s' % time.time())
            data = self.recv_once(buffersize)
            if data is not None:
                return data
        return None

    # cut

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self, **kwargs):
        self.send(b'VALUE', **kwargs)

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE', str)
    def METHOD_NAME_OUT(self, **kwargs):
        self.send(b'VALUE', **kwargs)
        return self.resolve_response(self.recv_timeout(20, 0.5))


class TcpTemplate(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        # POST_INIT

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.bind_host is not None:
            logging.notice('bound to %s:%d' % (self.bind_host, self.bind_port))
            self.socket.bind((self.bind_host, self.bind_port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(5)
        logging.info('Connecting to %s' % repr(self.remote_addr))
        self.socket.connect(self.remote_addr)

    def send_once(self, data, args):
        self.socket.send(data + self.end_chars + args + self.split_chars)

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)
        if self.socket is None:
            self.create_socket()
        try:
            self.send_once(data, args)
        except prometheus.psocket.socket_error:
            self.create_socket()
            self.send_once(data, args)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except prometheus.psocket.socket_error:
            # they said i could use OSError here, they lied (cpython/micropython issue, solve it later if necessary)
            return None, None

    def recv(self, buffersize=10):
        data, addr = self.try_recv(buffersize)
        if data is None:
            return None
        if addr not in self.buffers:
            self.buffers[addr] = prometheus.Buffer(split_chars=self.split_chars, end_chars=self.end_chars)
        self.buffers[addr].parse(data)
        bufferpacket = self.buffers[addr].pop()
        if bufferpacket is None:
            return None
        return bufferpacket.packet

    # cut

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self, **kwargs):
        self.send(b'VALUE', **kwargs)

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE', str)
    def METHOD_NAME_OUT(self, **kwargs):
        self.send(b'VALUE', **kwargs)
        return self.resolve_response(self.recv(50))


class JsonRestTemplate(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=8080, bind_host=None, bind_port=9195):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = None  # type: socket.socket
        self.bind_host = bind_host
        self.bind_port = bind_port
        self.remote_addr = (remote_host, remote_port)
        # POST_INIT

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.bind_host is not None:
            logging.notice('bound to %s:%d' % (self.bind_host, self.bind_port))
            self.socket.bind((self.bind_host, self.bind_port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(5)
        # logging.info('Connecting to %s' % repr(self.remote_addr))
        self.socket.connect(self.remote_addr)

    def send_once(self, data, args):
        # print('sending data=%s args=%s' % (data, args))
        if len(args) is not 0:
            args = b'?' + args
        request = b'GET /%s%s HTTP/1.1\r\nHost: %s\r\n' % (data, args, self.remote_addr[0].encode('utf-8'))
        # print('request: %s' % repr(request))
        self.socket.send(request)

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)

        self.create_socket()
        self.send_once(data, args)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except prometheus.psocket.socket_error:
            return None, None

    def recv(self, buffersize=200):
        data, addr = self.try_recv(buffersize)

        self.socket.close()
        if data is None:
            return None

        # print('data: %s' % (repr(data)))
        head, body = data.split(b'\r\n\r\n', 1)
        json_body = json.loads(body)
        # print('json_body = %s' % repr(json_body))
        value = json_body['value']
        # print('value = %s' % repr(value))

        if type(value) is str or (prometheus.is_py2 and type(value) is unicode):
            value = value.encode('utf-8')

        return value

    # cut

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'DVAL')
    def METHOD_NAME(self, **kwargs):
        self.send(b'VALUE', **kwargs)

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'DVAL', str)
    def METHOD_NAME_OUT(self, **kwargs):
        self.send(b'VALUE', **kwargs)
        return self.resolve_response(self.recv(200))


class RsaUdpTemplate(prometheus.misc.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, bind_host='', bind_port=9195, clientencrypt=False):
        prometheus.misc.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((bind_host, bind_port))
        logging.info('listening on %s:%d' % (bind_host, bind_port))
        self.socket.settimeout(0)
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        self.split_chars = b'\n'
        self.end_chars = b'\r'
        self.negotiated = False
        self.remote_key = (0, 0)
        self.clientencrypt = clientencrypt
        self.private_key = None
        self.public_key = None
        # POST_INIT

    def negotiate(self, revalidate=False):
        d = prometheus.crypto.get_local_key_registry()
        if self.remote_addr[0] in d.keys() and revalidate is False:
            # got key already
            logging.notice('found cached pubkey for %s' % self.remote_addr[0])
            self.remote_key = d[self.remote_addr[0]]
            self.negotiated = True
        else:
            # request key from remote end
            logging.notice('requesting pubkey')
            self.send_raw(b'pubkey')
            data = self.recv_timeout(250, 1)
            logging.notice('pubkey recv: %s' % repr(data))

            self.remote_key = data.split(b'\t')
            self.remote_key = (int(self.remote_key[0]), int(self.remote_key[1]))
            update = True
            if self.remote_addr[0] in d.keys():
                # verify that its the same one we got before
                if d[self.remote_addr[0]][0] != self.remote_key[0] or d[self.remote_addr[0]][1] != self.remote_key[1]:
                    logging.warn('! alert - public key does not match')
                    logging.warn('%s and %s' % (d[self.remote_addr[0]][0], self.remote_key[0]))
                    logging.warn('%s and %s' % (d[self.remote_addr[0]][1], self.remote_key[1]))
                else:
                    logging.success('valid pubkey for %s' % self.remote_addr[0])
                    update = False
            if update:
                d[self.remote_addr[0]] = self.remote_key
                prometheus.crypto.set_local_key_registry(d)

        if self.clientencrypt:
            if self.private_key is None:
                logging.info('generating new keys')
                self.public_key, self.private_key = prometheus.crypto.get_or_create_local_keys()

            # send version command to get pubkey request in return?
            logging.notice('sending version')
            self.send_raw(b'version')
            reply = self.recv()
            logging.debug('repr(reply)=%s' % repr(reply))

            msg = b'%d\t\t\t%d' % (self.public_key[0], self.public_key[1])
            logging.notice('returning public key')
            self.send_raw(msg)

        self.negotiated = True

    def send_raw(self, data, args=b''):
        self.socket.sendto(data + self.end_chars + args + self.split_chars, self.remote_addr)

    def send_crypted(self, data, args):
        logging.notice('send_crypted: cleartext is %d bytes' % len(data))
        if self.clientencrypt:
            data = prometheus.crypto.encrypt_packet(data, self.remote_key, self.private_key)
            args = prometheus.crypto.encrypt_packet(args, self.remote_key, self.private_key)
        else:
            data = prometheus.crypto.encrypt_packet(data, self.remote_key)
            args = prometheus.crypto.encrypt_packet(args, self.remote_key)
        self.send_raw(data, args)

    def send(self, data, **kwargs):
        if len(kwargs) is 0:
            args = b''
        else:
            args = prometheus.args_to_bytes(kwargs)
        if self.negotiated is False:
            self.negotiate(revalidate=False)
        self.send_crypted(data, args)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except prometheus.psocket.socket_error:
            # they said i could use OSError here, they lied (cpython/micropython issue, solve it later if necessary)
            return None, None

    def recv_once(self, buffersize=250):
        data, addr = self.try_recv(buffersize)  # type: bytes, int
        if data is None:
            return None
        if addr not in self.buffers:
            self.buffers[addr] = prometheus.Buffer(split_chars=self.split_chars, end_chars=self.end_chars)
        self.buffers[addr].parse(data)
        return self.buffers[addr].pop().packet

    def recv(self, buffersize=250):
        data = self.recv_timeout(buffersize, 0.5)
        if self.negotiated:
            if self.clientencrypt:
                data = prometheus.crypto.decrypt_packet(data, self.remote_key, self.private_key)
            else:
                data = prometheus.crypto.decrypt_packet(data, self.remote_key)
        return data

    def recv_timeout(self, buffersize, timeout):
        """
        :param buffersize: int
        :param timeout: float
        :return: str
        """
        timestamp = time.time()
        while (time.time() - timestamp) < timeout:
            # logging.debug('try recv: %s' % time.time())
            data = self.recv_once(buffersize)
            if data is not None:
                return data
        return None

    # cut

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self, **kwargs):
        self.send(b'VALUE', **kwargs)

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE', str)
    def METHOD_NAME_OUT(self, **kwargs):
        self.send(b'VALUE', **kwargs)
        return self.resolve_response(self.recv_timeout(10, 0.5))


class CodeValue(object):
    def __init__(self, name, value, out=False, data_value=None):
        # type: (str, str, bool) -> None
        self.name = name
        if len(value) > 2 and value[0:2] == '0d':
            value = chr(int(value[2:]))
        self.value = value
        self.out = out
        if data_value is None:
            data_value = value
        self.data_value = data_value

    def method_template(self, template_class, generated_class_name):
        if self.value == 'undefined' or self.name == 'microcontroller' or self.name == 'classname':
            return None
        replace_name = 'METHOD_NAME'
        # TODO: handle more than just not None
        if self.out is not None:
            replace_name = 'METHOD_NAME_OUT'
        lines, count = inspect.getsourcelines(getattr(template_class, replace_name))
        template = list()
        for line in lines:
            # logging.debug('line',line,line.find(replace_name))
            if line.find(replace_name) != -1:
                template.append(line.replace(replace_name, self.name).replace('CLASS_NAME', generated_class_name))
            elif line.find('VALUE') != -1 or line.find('DVAL') != -1:
                template.append(line.replace('VALUE', str(self.value)).replace('DVAL', self.data_value)
                                .replace('CLASS_NAME', generated_class_name))
            elif line.strip()[0] == '#':
                continue  # ignore these comments so it doesnt get spammy
            else:
                template.append(line)
        return ''.join(template)

    def __str__(self):
        return 'CodeValue name=%s value=%s' % (self.name, self.value)


class CodeBlock(object):
    def __init__(self, name, value):
        self.name = name.replace('\r', '')
        self.value = value

    def __str__(self):
        return 'CodeBlock name=%s value=%s' % (self.name, repr(self.value))


class CodeFile(object):
    FILE_UNKNOWN = -1
    FILE_BASIC = 0
    FILE_CPP = 1

    supported_extensions = ['.bas']

    def __init__(self, file_path):
        self.file_path = file_path
        self.type = CodeFile.FILE_UNKNOWN
        name_path, self.file_ext = os.path.splitext(file_path)
        self.path, self.filename = os.path.split(name_path)
        if self.file_ext == '.bas':
            self.type = CodeFile.FILE_BASIC
        self.parse_ex = re.compile(r"(')\1\1\1(.*?)\1{4}", re.DOTALL)
        self.codevalues = list()
        self.codeblocks = list()
        self.name = 'unknown'
        self.class_name = 'unknown'

    def parse(self):
        data = open(self.file_path, 'r').read()
        if data.find("''''name") == -1:
            return

        for groups in self.parse_ex.findall(data):
            capture = groups[1]
            # logging.debug('group: %s' % capture)
            if capture.find('\n') == -1 and capture.find('=') != -1:
                name, value = capture.split('=', 1)
                out = None
                if name.find('out|') != -1:
                    name = name.replace('out|', '')
                    out = True
                codevalue = CodeValue(name, value, out)
                # logging.debug(codevalue)
                # logging.debug(codevalue.method_template())
                self.codevalues.append(codevalue)
                if name == 'classname':
                    self.class_name = value
            elif capture.find('\n') != -1:
                name, value = capture.split('\n', 1)
                codeblock = CodeBlock(name, value)
                # logging.debug(codeblock)
                self.codeblocks.append(codeblock)
                if name.replace('\r', '') == 'name':
                    matches = re.findall(r'"([^"]*)"', value)
                    if len(matches) == 1:
                        self.name = matches[0]

        return True

    def generate_template(self, template_class_name):
        template_class = getattr(sys.modules[__name__], template_class_name)
        lines, count = inspect.getsourcelines(template_class)
        template = list()
        for line in lines:
            # logging.debug('line',line,line.find('NAME'))
            if line.find('cut') != -1:
                break
            elif line.find(template_class_name) != -1:
                template.append(line.replace(template_class_name, self.class_name))
            elif len(line.strip()) != 0 and line.strip()[0] == '#':
                continue  # ignore these comments so it doesnt get spammy
            else:
                template.append(line)
        codemethods = list()
        for codevalue in self.codevalues:
            codemethod = codevalue.method_template(template_class, self.class_name)
            if codemethod is not None:
                codemethods.append(codemethod)
        return ''.join(template) + '\n'.join(codemethods) + '\n\n'
        # + self.class_name[0].lower() + self.class_name[1:] + ' = ' + self.class_name + '()\n'

    def __str__(self):
        return 'CodeFile: %s' % self.filename


class PrometheusTemplate(object):
    def __init__(self, instance, name, parent, prefix=None):
        """
        :param instance: prometheus.Prometheus
        :param name: str
        :param parent: PrometheusTemplate
        :param prefix: str
        """
        self.instance = instance  # type: prometheus.Prometheus
        self.name = name  # type: str
        self.children = list()  # type: list[prometheus.Prometheus]
        self.parent = parent  # type: PrometheusTemplate
        self.prefix = prefix

    def generate(self, template_class, parent_class_name, generated_class_name, data_value_prefix=None,
                 http_template=False):
        """
        :param template_class: Type<prometheus.InputOutputProxy>
        :param parent_class_name: str
        :param generated_class_name: str
        :param data_value_prefix: str
        :return: str
        """
        # generate method templates and arrange command values
        # rem param remap_counter: prometheus.RemapCounter
        if self.parent is not None:
            # noinspection PyAugmentAssignment
            generated_class_name = parent_class_name + generated_class_name
        template_commands = dict()

        if http_template:
            self.instance.recursive_remap()
            self.instance.update_urls()
            command_keys = list(self.instance.cached_urls.keys())
            commands = self.instance.cached_urls
        else:
            command_keys = list(self.instance.commands.keys())
            commands = self.instance.commands
        command_keys.sort()

        for key in command_keys:
            value = commands[key]  # self.instance.commands[key]
            if not isinstance(value, prometheus.RegisteredMethod):
                continue

            # data value to send
            command_key = value.data_value
            if self.prefix:
                command_key = self.prefix + command_key
            # elif remap_counter:
            #     command_key = chr(remap_counter.next()) + command_key
            elif data_value_prefix:
                command_key = data_value_prefix + command_key
            if command_key in template_commands.keys():
                logging.warn('Warning: overwriting reference for data_value %s' % command_key)

            data_value = None
            if http_template:
                # URI
                data_value = command_key
                command_key = key

            context_key = value.method_name
            code_value = CodeValue(name=context_key, value=command_key, out=value.return_type,
                                   data_value=data_value)
            template_commands[command_key] = code_value.method_template(template_class, generated_class_name)

        method_templates = list()
        for key in template_commands:
            method_templates.append(template_commands[key])

        # TODO: something for variables?
        attribute_keys = list(self.instance.attributes.keys())
        attribute_keys.sort()

        init_variables = None
        for key in attribute_keys:
            # value = self.instance.attributes[key]
            if init_variables is None:
                init_variables = list()
            attribute_class_name = generate_class_name(key)
            # if self.parent is not None:
            attribute_class_name = parent_class_name + attribute_class_name
            init_variables.append((key, attribute_class_name))

        # generate class template with methods
        template_class_name = template_class.__name__
        lines, count = inspect.getsourcelines(template_class)
        template = list()
        for line in lines:
            # logging.debug('line',line,line.find('NAME'))
            if line.find('cut') != -1:
                break
            elif line.find(template_class_name) != -1:
                template.append(line.replace(template_class_name, generated_class_name))
            elif len(line.strip()) != 0 and line.strip()[0] == '#':
                if init_variables is not None and line.find('# POST_INIT') != -1:
                    # lets add the post init stuff then
                    post_init = list()
                    for init_variable in init_variables:
                        variable_name, class_name = init_variable
                        post_init.append('        self.%s = %s(self.send, self.recv)' % (variable_name, class_name))
                        post_init.append('        self.register(%s=self.%s)' % (variable_name, variable_name))
                    template.append(line.replace('# POST_INIT', '\n' + '\n'.join(post_init)))
                continue  # ignore these comments so it doesnt get spammy
            else:
                template.append(line)
        return ''.join(template) + '\n'.join(method_templates)


class RemapCounter(object):
    def __init__(self, value):
        # :type value: int
        self.counter = value

    def next(self):
        self.counter += 1
        return self.counter - 1


def parse_folder(path):
    code_files = list()
    for filename in os.listdir(path):
        if not os.path.splitext(filename)[1] in CodeFile.supported_extensions:
            continue

        code_file = CodeFile('%s%s%s' % (path, os.path.sep, filename))
        if code_file.parse():
            logging.info('adding %s' % code_file)
            code_files.append(code_file)
    return code_files


def folder_import():
    path = os.path.join('..', 'devices')
    all_code = list()
    for folder in os.listdir(path):
        folder_path = os.path.join(path, folder)
        folder_code = parse_folder(folder_path)
        # logging.debug('files detected under %s: %d' % (folder_path, len(folder_code)))
        all_code.extend(folder_code)

    item = all_code[0]
    template = item.generate_template('SerialTemplate')
    output_folder = os.path.join('..', '..', 'deploy', 'clients')
    outfile = os.path.join(output_folder, item.class_name + '.py')
    # logging.debug(template)
    logging.info('writing to %s' % outfile)
    import_socket, import_machine = '', ''
    if template.find('socket.') != -1:
        import_socket = 'import socket\n'
    if template.find('machine.') != -1:
        import_machine = 'import machine\n'
    header = '# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +\
        '''import prometheus\n%s%simport time\nimport gc\nimport prometheus.crypto
import prometheus.misc\nimport prometheus.psocket\nimport prometheus.logging as logging
\ngc.collect()\n\n\n''' % (import_socket, import_machine)
    open(outfile, 'w').write(header + template)
    # '\n\n' + ''.join(inspect.getsourcelines(prometheus.Prometheus)[0])
    # ''.join(inspect.getsourcelines(prometheus.Registry)[0]) + '\n\n'
    # SerialTemplate.NAME()


def generate_class_name(name):
    class_name = ''
    for word in name.split('_'):
        class_name += word[0].upper() + word[1:]
    return class_name


def generate_template_classes(template_classes, instance, name, parent=None, prefix=None):
    """
    :type template_classes: list
    :type instance: Prometheus
    :type name: str
    :type parent: PrometheusTemplate
    :type prefix: str
    """

    prometheus_template = PrometheusTemplate(instance, name, parent, prefix)
    template_classes.append(prometheus_template)

    if parent:
        # list of directly underlying entities
        parent.children.append(prometheus_template)

    # should only contain inheritors of prometheus
    for key in instance.attributes.keys():
        prometheus_attribute = instance.attributes[key]  # type: prometheus.PrometheusAttribute
        generate_template_classes(template_classes, prometheus_attribute.instance, key, prometheus_template,
                                  prefix=prometheus_attribute.prefix)


def generate_python_template(source_class, template_class, generated_class_name, subclasses=True):
    """
    :type source_class: Type<prometheus.Prometheus>
    :type template_class: Type<prometheus.misc.RemoteTemplate>
    :type generated_class_name: str
    :type subclasses: bool
    """

    instance = source_class()
    template_class_name = template_class.__name__
    # template_class = getattr(sys.modules[__name__], template_class_name)

    template_classes = list()
    # this will only work for a Prometheus inheritor, but it should be kept separate
    #  from it in order to separate code templating/build from dist
    generate_template_classes(template_classes, instance, 'self')

    # remap_counter = prometheus.RemapCounter(65)
    supportclass_templates = list()
    mainclass_template = ''
    http_template = template_class_name == 'JsonRestTemplate'

    for prometheus_template in template_classes:
        if not isinstance(prometheus_template, PrometheusTemplate):
            raise Exception('Object is not of type PrometheusTemplate')

        # logging.debug(prometheus_template.name, prometheus_template.instance)
        if prometheus_template.name == 'self':
            mainclass_template = prometheus_template.generate(template_class,
                                                              generated_class_name,
                                                              generated_class_name,
                                                              http_template=http_template)
        else:
            # data_value_prefix = chr(remap_counter.next())
            # logging.debug('prefix=%s for %s' % (data_value_prefix, prometheus_template.name))
            supportclass_template = prometheus_template.generate(prometheus.misc.InputOutputProxy,
                                                                 generated_class_name,
                                                                 generate_class_name(prometheus_template.name),
                                                                 data_value_prefix=None,
                                                                 http_template=http_template)
            supportclass_template = supportclass_template.replace('(Prometheus):', '(prometheus.Prometheus):')
            supportclass_template = supportclass_template.replace('Prometheus.__init__(self)',
                                                                  'prometheus.Prometheus.__init__(self)')
            supportclass_template = supportclass_template.replace('@Registry.register', '@prometheus.Registry.register')
            supportclass_templates.append(supportclass_template)

    full_template = '\n\n'.join(supportclass_templates) + '\n\n' + mainclass_template
    return full_template


def build_client(cls, output_filename, client_template_instances):
    """
    :param cls: type[prometheus.Prometheus]
    :param output_filename: str
    :param client_template_instances: list(Type[prometheus.Prometheus])
    :return: None
    """
    # TODO: dynamically determine imports necesary for this specific module?

    imports = 'import prometheus\n%s%simport time\nimport gc\n' +\
              'import prometheus.crypto\nimport prometheus.misc\nimport prometheus.psocket\n' \
              'import prometheus.logging as logging\n' +\
              '\ngc.collect()\n\n\n'
    code = list()
    subclasses = True  # only for the first instance
    classes = list()
    for client_template_instance in client_template_instances:
        generated_class_name = cls.__name__ + client_template_instance.__name__.replace('Template', '') + 'Client'
        # logging.debug('Generating class: %s' % generated_class_name)
        classes.append(generated_class_name)
        code.append('# region ' + generated_class_name + '\n' +
                    generate_python_template(source_class=cls, template_class=client_template_instance,
                                             generated_class_name=generated_class_name, subclasses=subclasses) +
                    '\n# endregion\n\n')
        subclasses = False
    output_path = os.path.join('..', '..', 'deploy', 'clients', output_filename)
    logging.info('Writing to %s, classes: %s' % (output_path, ', '.join(classes)))
    all_code = '\n'.join(code)[:-1]
    import_socket, import_machine = '', ''
    if all_code.find('socket.') != -1:
        import_socket = 'import socket\n'
    if all_code.find('machine.') != -1:
        import_machine = 'import machine\n'
    imports %= import_socket, import_machine
    open(output_path, 'w').write(
        '# coding=utf-8\n# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
        imports + all_code)


if __name__ == '__main__':
    # to "make" lightcontrol and other things from basic sources
    # folder_import()

    from tank import Tank
    build_client(Tank, 'tankclient.py', [UdpTemplate, TcpTemplate])
    
    from tankproxy import TankProxy
    build_client(TankProxy, 'tankproxyclient.py', [UdpTemplate, TcpTemplate])
    
    # from proxytest import ProxyTest
    # build_client(ProxyTest, 'proxyclient.py', [UdpTemplate, TcpTemplate])
    
    from chaintest import A, B, C
    build_client(A, 'chainclientA.py', [UdpTemplate, TcpTemplate])
    build_client(B, 'chainclientB.py', [UdpTemplate, TcpTemplate])
    build_client(C, 'chainclientC.py', [UdpTemplate, TcpTemplate])

    from sensor01 import Sensor01
    build_client(Sensor01, 'sensor01client.py', [UdpTemplate])
    
    from sensor02 import Sensor02
    build_client(Sensor02, 'sensor02client.py', [UdpTemplate])

    from nodetest import NodeTest
    build_client(NodeTest, 'nodetestclient.py', [UdpTemplate, TcpTemplate])

    from localtest import LocalTest
    build_client(LocalTest, 'localtestclient.py', [UdpTemplate, TcpTemplate, JsonRestTemplate])

    from test01 import Test01
    build_client(Test01, 'test01client.py', [UdpTemplate, TcpTemplate])
    
    from test02 import Test02
    build_client(Test02, 'test02client.py', [UdpTemplate, TcpTemplate])

    from proxytest2 import ProxyTest2
    build_client(ProxyTest2, 'proxytest2client.py', [UdpTemplate, TcpTemplate])
    # , RsaUdpTemplate

    # u = RsaUdpTemplate('192.168.1.102', bind_port=9191, clientencrypt=False)
    # u.send(b'version')
    # v = u.recv(250)
    # logging.info('version: %s' % v)

    from rover01 import Rover01
    build_client(Rover01, 'rover01client.py', [UdpTemplate, TcpTemplate])
