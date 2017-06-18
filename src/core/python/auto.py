import os
import sys
import re
import inspect
import machine
import prometheus
import socket
import datetime


class SerialTemplate(prometheus.RemoteTemplate):
    def __init__(self, channel, baudrate):
        prometheus.RemoteTemplate.__init__(self)
        self.uart = machine.UART(channel, baudrate=baudrate)
        # POST_INIT

    def send(self, data):
        self.uart.write(data + b'\n')

    def recv(self, buffersize=None):
        if buffersize:
            return self.uart.read(buffersize)
        else:
            return self.uart.read()

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


class UdpTemplate(prometheus.RemoteTemplate):
    def __init__(self, remote_host, remote_port=9195, local_port=9195):
        prometheus.RemoteTemplate.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', local_port))
        self.remote_addr = (remote_host, remote_port)
        # POST_INIT

    def send(self, data):
        self.socket.sendto(data, self.remote_addr)

    def recv(self, buffersize=10):
        # TODO: addr is not checked, this could be sent by anyone and renders multiple connections moot
        self.socket.setblocking(False)
        data, addr = self.socket.recvfrom(buffersize)
        self.socket.setblocking(True)
        return data

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
    def __init__(self, name, value, out=None):
        self.name = name
        if value[0] == 'b':
            value = chr(int(value[1:]))
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


def folder_test():
    path = os.path.join('..', '..', 'devices')
    all_code = list()
    for folder in os.listdir(path):
        folder_path = os.path.join(path, folder)
        folder_code = parse_folder(folder_path)
        print('files detected under %s: %d' % (folder_path, len(folder_code)))
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


def map_template_commands(commands, template_commands, template_class_commands, template_class, generated_class_name, remap=True, remap_counter=None,
                          context='self'):
    """
    :type commands: dict
    :type template_commands: dict
    :type template_class_commands: dict
    :type template_class: Type
    :type generated_class_name: str
    :type remap: bool
    :type remap_counter: prometheus.RemapCounter
    :type context: str
    """
    if remap_counter is None:
        remap_counter = prometheus.RemapCounter(65)

    command_keys = list(commands.keys())
    command_keys.sort()

    for key in command_keys:
        value = commands[key]
        if isinstance(value, prometheus.RegisteredMethod):
            if not remap:
                command_key = value.data_value
            else:
                # re-map the bytes
                command_key = chr(remap_counter.next())
            if command_key in template_commands.keys():
                print('Warning: overwriting reference for data_value %s' % command_key)
            # context_key = '%s__%s' % (context, value.method_name)
            # code_value = CodeValue(name=context_key, value=command_key, out=value.return_type)
            # template_commands[command_key] = code_value.method_template(template_class, generated_class_name)
            if context == 'self':
                context_key = value.method_name
                code_value = CodeValue(name=context_key, value=command_key, out=value.return_type)
                template_commands[command_key] = code_value.method_template(template_class, generated_class_name)
            else:
                context_key = value.method_name
                context_class_name = generate_class_name(context)
                code_value = CodeValue(name=context_key, value=command_key, out=value.return_type)
                context_index = (context, context_class_name)
                if not context_index in template_class_commands.keys():
                    template_class_commands[context_index] = dict()
                template_class_commands[context_index][command_key] = code_value.method_template(template_class, context_class_name)
            print('Added reference for %s.%s (%s) data_value %s (%d)' % (context, value.method_name, value.method_reference,
                                                                         command_key, ord(command_key)))
        elif isinstance(value, dict):
            print('its a dict, going derper: %s' % value)
            map_template_commands(value, template_commands, template_class_commands, template_class, generated_class_name, remap, remap_counter, context=key)


def generate_template(template_class_name, generated_class_name, method_templates, template_class=None, init_variables=None):
    # to permit overrides on non-dynamic (InputOutputProxy)
    if template_class is None:
        template_class = getattr(sys.modules[__name__], template_class_name)
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
    return ''.join(template) + '\n' + '\n'.join(method_templates) + '\n\n'


def generate_python_template(source_class, template_class, generated_class_name, subclasses=True):
    # :type source_class: prometheus.Prometheus
    # :type template_class: prometheus.RemoteTemplate
    # TODO: get this dynamically somehow
    # from nodetest import NodeTest as source_class

    instance = source_class()
    print(instance.commands)
    template_commands = dict()
    template_class_commands = dict()
    template_class_name = template_class.__name__  # 'UdpTemplate'
    template_class = getattr(sys.modules[__name__], template_class_name)
    # generated_class_name = 'NodeClient'
    # filename = 'nodeclient.py'
    map_template_commands(instance.commands, template_commands, template_class_commands, template_class, generated_class_name)

    lst = list()
    for key in template_commands:
        # print(template_commands[key])
        lst.append(template_commands[key])

    class_list = list()
    if subclasses:
        for key in template_class_commands:
            # template_class = ''.join(inspect.getsourcelines(prometheus.InputOutputProxy)[0]) + '\n'
            # print(key, template_class_commands[key])
            variable_name, class_name = key
            lst2 = list()
            for method_key in template_class_commands[key]:
                lst2.append(template_class_commands[key][method_key])
            template_class = generate_template('InputOutputProxy', class_name, lst2, prometheus.InputOutputProxy)
            template_class = template_class.replace('(Prometheus):', '(prometheus.Prometheus):')
            template_class = template_class.replace('Prometheus.__init__(self)', 'prometheus.Prometheus.__init__(self)')
            # print(template_class)
            class_list.append(template_class)

    template = ''.join(class_list) + generate_template(template_class_name, generated_class_name, lst, init_variables=list(template_class_commands.keys()))
    # print(template)
    template = template.replace('\n\n\n\n\n', '\n\n')
    return template
    # open(filename, 'w').write('import prometheus\nimport socket\nimport machine\n\n\n' + template)


# folder_test()

# TODO: make the following code dynamic?
imports = 'import prometheus\nimport socket\nimport machine\n\n\n'
"""
from main import Tank

open(os.path.join('..', '..', '..', 'build', 'clients', 'tankclient.py'), 'w').write('# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + imports +
                                                                                     generate_python_template(source_class=Tank, template_class=TcpTemplate,
                                                                                                              generated_class_name='TankTestTcp') + '\n' +
                                                                                     generate_python_template(source_class=Tank, template_class=UdpTemplate,
                                                                                                              generated_class_name='TankTestUdp',
                                                                                                              subclasses=False)
                                                                                     )

from nodetest import NodeTest

open(os.path.join('..', '..', '..', 'build', 'clients', 'nodeclient.py'), 'w').write('# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + imports +
                                                                                     generate_python_template(source_class=NodeTest, template_class=TcpTemplate,
                                                                                                              generated_class_name='NodeTestTcp') + '\n' +
                                                                                     generate_python_template(source_class=NodeTest, template_class=UdpTemplate,
                                                                                                              generated_class_name='NodeTestUdp',
                                                                                                              subclasses=False)
                                                                                     )

from proxytest import ProxyTest

open(os.path.join('..', '..', '..', 'build', 'clients', 'proxyclient.py'), 'w').write('# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d '
                                                                                                                                               '%H:%M:%S') +
                                                                                      imports +
                                                                                      generate_python_template(source_class=ProxyTest,
                                                                                                               template_class=TcpTemplate,
                                                                                                               generated_class_name='ProxyTestTcp') + '\n' +
                                                                                      generate_python_template(source_class=ProxyTest,
                                                                                                               template_class=UdpTemplate,
                                                                                                               generated_class_name='ProxyTestUdp',
                                                                                                               subclasses=False)
                                                                                      )
"""

from chaintest import A, B, C
"""
open(os.path.join('..', '..', '..', 'build', 'clients', 'chainclientA.py'), 'w').write('# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d '
                                                                                                                                               '%H:%M:%S') +
                                                                                      imports +
                                                                                      generate_python_template(source_class=A,
                                                                                                               template_class=UdpTemplate,
                                                                                                               generated_class_name='AUdp',
                                                                                                               subclasses=True)
                                                                                      )
"""
open(os.path.join('..', '..', '..', 'build', 'clients', 'chainclientB.py'), 'w').write('# generated at %s\n' % datetime.datetime.now().strftime('%Y-%m-%d '
                                                                                                                                               '%H:%M:%S') +
                                                                                      imports +
                                                                                      generate_python_template(source_class=B,
                                                                                                               template_class=UdpTemplate,
                                                                                                               generated_class_name='BUdp',
                                                                                                               subclasses=True)
                                                                                      )
