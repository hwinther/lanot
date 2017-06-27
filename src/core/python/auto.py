import os
import sys
import re
import inspect
import machine
import prometheus
import socket
import datetime
import time
from prometheus import Buffer

# TODO: move these template classes to another python file? perhaps one for each via python modules


class SerialTemplate(prometheus.RemoteTemplate):
    def __init__(self, channel, baudrate):
        prometheus.RemoteTemplate.__init__(self)
        self.uart = machine.UART(channel, baudrate=baudrate)
        self.buffer = Buffer(split_chars=b'\n', end_chars=b'\n')
        # POST_INIT

    def send(self, data):
        self.uart.write(data + self.buffer.endChars)

    def recv(self, buffersize=None):
        if buffersize:
            self.buffer.parse(self.uart.read(buffersize))
        else:
            self.buffer.parse(self.uart.read())
        return self.buffer.pop()

    # cut

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self):
        self.send(b'VALUE')

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE', 'OUT')
    def METHOD_NAME_OUT(self):
        self.send(b'VALUE')
        self.recv(4)
        # TODO: replace this with something better?
        time.sleep(0.5)
        return self.buffer.pop()


class UdpTemplate(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, local_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', local_port))
        self.socket.settimeout(0)
        self.remote_addr = (remote_host, remote_port)
        self.buffers = dict()
        # POST_INIT

    def send(self, data):
        self.socket.sendto(data + b'\n', self.remote_addr)

    def try_recv(self, buffersize):
        try:
            return self.socket.recvfrom(buffersize)  # data, addr
        except OSError:
            return None, None

    def recv(self, buffersize=10):
        data, addr = self.try_recv(buffersize)
        if data is None:
            return None
        if addr not in self.buffers:
            self.buffers[addr] = Buffer(split_chars=b'\n', end_chars=b'\n')
        self.buffers[addr].parse(data)
        return self.buffers[addr].pop()

    def recv_timeout(self, buffersize, timeout):
        timestamp = time.time()
        while (time.time() - timestamp) > 0.5:
            data = self.recv(buffersize)
            if data is not None:
                return data
        return None

    # cut

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self):
        self.send(b'VALUE')

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE', 'OUT')
    def METHOD_NAME_OUT(self):
        self.send(b'VALUE')
        return self.recv_timeout(4, 0.5)


class TcpTemplate(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, local_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', local_port))
        self.remote_addr = (remote_host, remote_port)
        self.socket.connect(self.remote_addr)
        # POST_INIT

    def send(self, data):
        self.socket.sendall(data)

    def recv(self, buffersize=10):
        return self.socket.recv(buffersize)

    # cut

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE')
    def METHOD_NAME(self):
        self.send(b'VALUE')

    # noinspection PyPep8Naming
    @prometheus.Registry.register('CLASS_NAME', 'VALUE', 'OUT')
    def METHOD_NAME_OUT(self):
        self.send(b'VALUE')
        # TODO: pause maybe
        return self.recv(4)


class CodeValue:
    def __init__(self, name, value, out=False):
        # type: (str, str, bool) -> None
        self.name = name
        if len(value) > 2 and value[0:2] == '0d':
            value = chr(int(value[2:]))
        self.value = value
        self.out = out

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
            # print('line',line,line.find(replace_name))
            if line.find(replace_name) != -1:
                template.append(line.replace(replace_name, self.name).replace('CLASS_NAME', generated_class_name))
            elif line.find('VALUE') != -1:
                template.append(line.replace('VALUE', str(self.value)).replace('CLASS_NAME', generated_class_name))
            elif line.strip()[0] == '#':
                continue  # ignore these comments so it doesnt get spammy
            else:
                template.append(line)
        return ''.join(template)

    def __str__(self):
        return 'CodeValue name=%s value=%s' % (self.name, self.value)


class CodeBlock:
    def __init__(self, name, value):
        self.name = name.replace('\r', '')
        self.value = value

    def __str__(self):
        return 'CodeBlock name=%s value=%s' % (self.name, repr(self.value))


class CodeFile:
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
            # print('group: %s' % capture)
            if capture.find('\n') == -1 and capture.find('=') != -1:
                name, value = capture.split('=', 1)
                out = None
                if name.find('out|') != -1:
                    name = name.replace('out|', '')
                    out = True
                codevalue = CodeValue(name, value, out)
                # print(codevalue)
                # print(codevalue.method_template())
                self.codevalues.append(codevalue)
                if name == 'classname':
                    self.class_name = value
            elif capture.find('\n') != -1:
                name, value = capture.split('\n', 1)
                codeblock = CodeBlock(name, value)
                # print(codeblock)
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
            # print('line',line,line.find('NAME'))
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
        self.children = list()  # type: list<prometheus.Prometheus>
        self.parent = parent  # type: PrometheusTemplate
        self.prefix = prefix

    def generate(self, template_class, parent_class_name, generated_class_name, data_value_prefix=None):
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
            generated_class_name = parent_class_name + generated_class_name
        template_commands = dict()

        command_keys = list(self.instance.commands.keys())
        command_keys.sort()

        for key in command_keys:
            value = self.instance.commands[key]
            if isinstance(value, prometheus.RegisteredMethod):
                command_key = value.data_value
                if self.prefix:
                    command_key = self.prefix + command_key
                # elif remap_counter:
                #     command_key = chr(remap_counter.next()) + command_key
                elif data_value_prefix:
                    command_key = data_value_prefix + command_key
                if command_key in template_commands.keys():
                    print('Warning: overwriting reference for data_value %s' % command_key)

                context_key = value.method_name
                code_value = CodeValue(name=context_key, value=command_key, out=value.return_type)
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
            # print('line',line,line.find('NAME'))
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


def parse_folder(path):
    code_files = list()
    for filename in os.listdir(path):
        if not os.path.splitext(filename)[1] in CodeFile.supported_extensions:
            continue

        code_file = CodeFile('%s%s%s' % (path, os.path.sep, filename))
        if code_file.parse():
            print('adding %s' % code_file)
            code_files.append(code_file)
    return code_files


def folder_import():
    path = os.path.join('..', '..', 'devices')
    all_code = list()
    for folder in os.listdir(path):
        folder_path = os.path.join(path, folder)
        folder_code = parse_folder(folder_path)
        # print('files detected under %s: %d' % (folder_path, len(folder_code)))
        all_code.extend(folder_code)

    item = all_code[0]
    template = item.generate_template('SerialTemplate')
    output_folder = os.path.join('..', '..', '..', 'build', 'clients')
    outfile = os.path.join(output_folder, item.class_name + '.py')
    # print(template)
    print('writing to %s' % outfile)
    open(outfile, 'w').write('# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
                             'import prometheus\nimport machine\n\n\n' + template)
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
        generate_template_classes(template_classes, prometheus_attribute.instance, key, prometheus_template, prefix=prometheus_attribute.prefix)


def generate_python_template(source_class, template_class, generated_class_name, subclasses=True):
    """
    :type source_class: Type<prometheus.Prometheus>
    :type template_class: Type<prometheus.RemoteTemplate>
    :type generated_class_name: str
    :type subclasses: bool
    """

    instance = source_class()
    template_class_name = template_class.__name__
    # template_class = getattr(sys.modules[__name__], template_class_name)

    template_classes = list()
    # this will only work for a Prometheus inheritor, but it should be kept separate from it in order to separate code templating/build from dist
    generate_template_classes(template_classes, instance, 'self')

    # remap_counter = prometheus.RemapCounter(65)
    supportclass_templates = list()
    mainclass_template = ''

    for prometheus_template in template_classes:
        if not isinstance(prometheus_template, PrometheusTemplate):
            raise Exception('Object is not of type PrometheusTemplate')

        # print(prometheus_template.name, prometheus_template.instance)
        if prometheus_template.name == 'self':
            mainclass_template = prometheus_template.generate(template_class, generated_class_name, generated_class_name)
        else:
            # data_value_prefix = chr(remap_counter.next())
            # print('prefix=%s for %s' % (data_value_prefix, prometheus_template.name))
            supportclass_template = prometheus_template.generate(prometheus.InputOutputProxy, generated_class_name,
                                                                 generate_class_name(prometheus_template.name),
                                                                 data_value_prefix=None)
            supportclass_template = supportclass_template.replace('(Prometheus):', '(prometheus.Prometheus):')
            supportclass_template = supportclass_template.replace('Prometheus.__init__(self)', 'prometheus.Prometheus.__init__(self)')
            supportclass_template = supportclass_template.replace('@Registry.register', '@prometheus.Registry.register')
            supportclass_templates.append(supportclass_template)

    full_template = '\n\n'.join(supportclass_templates) + '\n\n' + mainclass_template
    return full_template


def build_client(instance, output_filename, client_template_instances):
    """
    :param instance: Type[prometheus.Prometheus]
    :param output_filename: str
    :param client_template_instances: list(Type[prometheus.Prometheus])
    :return: None
    """
    # TODO: dynamically determine imports necesary for this specific module?
    imports = 'import prometheus\nimport socket\nimport machine\n\n\n'
    code = list()
    subclasses = True  # only for the first instance
    classes = list()
    for client_template_instance in client_template_instances:
        generated_class_name = instance.__name__ + client_template_instance.__name__.replace('Template', '') + 'Client'
        # print('Generating class: %s' % generated_class_name)
        classes.append(generated_class_name)
        code.append(generate_python_template(source_class=instance, template_class=client_template_instance,
                    generated_class_name=generated_class_name, subclasses=subclasses))
        subclasses = False
    output_path = os.path.join('..', '..', '..', 'build', 'clients', output_filename)
    print('Writing to %s, classes: %s' % (output_path, ', '.join(classes)))
    open(output_path, 'w').write(
        '# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+
        imports + '\n'.join(code))

folder_import()

from tank import Tank
build_client(Tank, 'tankclient.py', [TcpTemplate, UdpTemplate])
from nodetest import NodeTest
build_client(NodeTest, 'nodeclient.py', [UdpTemplate])
from proxytest import ProxyTest
build_client(ProxyTest, 'proxyclient.py', [UdpTemplate])
from chaintest import A, B, C
build_client(A, 'chainclientA.py', [UdpTemplate])
build_client(B, 'chainclientB.py', [UdpTemplate])
build_client(C, 'chainclientC.py', [UdpTemplate])
