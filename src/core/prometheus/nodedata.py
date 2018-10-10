# coding=utf-8
"""
server - recv packet (buffer), parse and validate node to a-z, write to node/sensor/%yy.%mm.%dd/data.json:
record:
[
  {
      'timestamp': 'iso-timestamp',
      data: [
          {'sensor': value},
          (..)
      ]
  }
]
client - send list of packets
packet: node\tsensor\tvalue\r\n
function to parse data file into individual readings again?
"""
import socket
import time
import gc
import os
import prometheus
import prometheus.psocket
import prometheus.logging


__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class NodeData:
    """
NodeData storage and formatting class
    """
    def __init__(self, node, sensor, value, timestamp=None):
        # type: (bytes, bytes, bytes, int) -> NodeData
        """
Data formatting class, raw data to/from json
        :param node: node/device name
        :param sensor: sensor name
        :param value: sensor value
        :param timestamp: should be left empty unless loading from file
        """
        self.node = node
        self.sensor = sensor
        self.value = value
        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp

    def to_json(self):
        """
Convert to JSON format
        :return: JSON as string
        """
        import json
        return json.dumps({'node': self.node, 'sensor': self.sensor, 'value': self.value, 'timestamp': self.timestamp})

    @staticmethod
    def from_json(data):
        """
Construct NodeData instance from JSON format
        :param data: JSON object
        :return: NodeData instance
        """
        return NodeData(data['node'], data['sensor'], data['value'], data['timestamp'])

    def to_packet(self):
        """
Convert to packet (raw) format
        :return: bytes
        """
        return b'%s\t%s\t%s' % (self.node, self.sensor, self.value)

    @staticmethod
    def from_packet(data):
        """
Construct NodeData instance from packet (raw) format
        :param data: bytes
        :return: NodeData instance
        """
        parts = data.split(b'\t')
        print(parts, len(parts))
        if len(parts) != 3:
            return None
        node_data = NodeData(parts[0], parts[1], parts[2])
        import datetime
        node_data.timestamp = datetime.datetime.now().isoformat()
        return node_data


class Server:
    """
NodeData UDP server
    """
    def start(self, bind_host='', bind_port=9085):
        """
NodeData UDP receiver
        :param bind_host: IP to bind to, defaults to any
        :param bind_port: Port to bind to, defaults to 9085
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((bind_host, bind_port))
        prometheus.logging.info('Listening on %s:%d' % (bind_host, bind_port))
        sock.settimeout(0.1)
        buffers = dict()
        split_chars = '\n'
        end_chars = '\r'
        debug = True

        while True:
            data, addr = None, None
            try:
                data, addr = sock.recvfrom(500)
            except prometheus.psocket.socket_error as exception:
                if prometheus.is_micro:
                    if exception.args[0] != 11 and exception.args[0] != 110 and exception.args[0] != 23:
                        prometheus.logging.error(exception)
                        raise
                else:
                    if exception.errno != 11 and exception.errno != 110 and exception.errno != 10035 and \
                            not isinstance(exception, socket.timeout):
                        prometheus.logging.error(exception)
                        raise

            if data is None:
                continue

            prometheus.logging.notice('recv %s from %s' % (repr(data), repr(addr)))

            if addr not in buffers.keys():
                if debug:
                    prometheus.logging.debug('Creating new buffer context')
                buffers[addr] = prometheus.Buffer(split_chars=split_chars, end_chars=end_chars)

            buffers[addr].parse(data)

            while True:
                command = buffers[addr].pop()
                if command is None:
                    break

                prometheus.logging.debug('handle_packet')
                self.handle_packet(addr, command)

    @staticmethod
    def handle_packet(addr, command):
        """
Append packet to file
        :param addr: (host, port) tuple
        :param command: command data
        :return: None
        """
        packet = NodeData.from_packet(command.packet)
        if packet is None:
            return
        prometheus.logging.info('addr=%s cmd=%s' % (addr, command))
        import datetime
        date_time = datetime.datetime.now()
        filename = '%s.json' % date_time.strftime('%Y.%m.%d')
        folder = packet.node
        if not os.path.exists('data'):
            os.mkdir('data')
        folder = os.path.join('data', folder)
        if not os.path.exists(folder):
            os.mkdir(folder)
        filepath = os.path.join(folder, filename)
        prometheus.logging.info('writing to %s' % filepath)
        with open(filepath, 'a') as file_descriptor:
            file_descriptor.write(packet.to_json() + b'\r\n')


def client(host, port, *nodedatas):
    """
NodeData sending client
    :param host: Host to connect to
    :param port: Port to connect to
    :param nodedatas: List of NodeData instances
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for nodedata in nodedatas:
        assert isinstance(nodedata, NodeData)
        prometheus.logging.info('Sending %s=%s' % (nodedata.sensor, nodedata.value))
        sock.sendto(nodedata.to_packet() + b'\r\n', (host, port))
        gc.collect()
    gc.collect()


def run_server():
    """
Start UDP server instance
    """
    server = Server()
    server.start()


if __name__ == '__main__':
    run_server()
