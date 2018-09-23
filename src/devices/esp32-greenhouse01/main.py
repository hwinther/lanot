import greenhouse01
import urequests
import machine
import prometheus.server.multiserver
import prometheus.server.socketserver.udp
import prometheus.server.socketserver.tcp
import prometheus.server.socketserver.jsonrest
import prometheus.tftpd
import prometheus.pnetwork
import prometheus.logging as logging
import prometheus.pgc as gc
import time

gc.collect()


def td():
    prometheus.tftpd.tftpd()


class LocalEvents(prometheus.server.Server):
    def __init__(self, instance):
        """
        :type instance: greenhouse01.GreenHouse01
        """
        prometheus.server.Server.__init__(self, instance)
        self.timer = 0

    def pre_loop(self, **kwargs):
        self.timer = time.time() - 300
        self.instance.ssd.fill(False)
        self.instance.ssd.text('v: %s' % self.version(), 0, 0)
        self.instance.ssd.show()

    def loop_tick(self, **kwargs):
        diff = time.time() - self.timer
        if diff >= 300:
            self.timer = time.time()
            # print('1 sec event, diff=%d' % diff)
            assert isinstance(self.instance, greenhouse01.Greenhouse01)

            # update the screen with current values
            h1 = self.instance.hygrometer01.read()
            h2 = self.instance.hygrometer02.read()
            h3 = self.instance.hygrometer03.read()
            h4 = self.instance.hygrometer04.read()
            h5 = self.instance.hygrometer05.read()
            h6 = self.instance.hygrometer06.read()

            self.instance.ssd.fill(False)
            self.instance.ssd.text('v: %s' % self.version(), 0, 0)
            self.instance.ssd.text('t: %d o: %s' % (time.time(), prometheus.pnetwork.sta_if.isconnected()), 0, 10)
            if prometheus.pnetwork.sta_if.isconnected():
                self.instance.ssd.text('i:%s' % prometheus.pnetwork.sta_if.ifconfig()[0], 0, 20)
            self.instance.ssd.text('h1:%d h2:%d' % (h1, h2), 0, 30)
            self.instance.ssd.text('h3:%d h4:%d' % (h3, h4), 0, 40)
            self.instance.ssd.text('h5:%d h6:%d' % (h5, h6), 0, 50)

            dht_value = self.instance.dht11.value()
            temperature = '0'
            humidity = '0'
            if dht_value.find('c') != -1:
                temperature, humidity = dht_value.split('c')
            self.instance.ssd.text('tem:%s hum:%s' % (temperature, humidity), 0, 60)

            self.instance.ssd.show()

            # update thingspeak graph data
            # GET https://api.thingspeak.com/update?api_key=YC62U1B1P23RVPQS&field1=0
            # fields = temperature, humidity, hygro1, hygro2, hygro3, hygro4, hygro5, hygro6
            response = urequests.get('https://api.thingspeak.com/update?api_key=YC62U1B1P23RVPQS&field1=%s&field2=%s&'
                                     'field3=%s&field4=%s&field5=%s&field6=%s&field7=%s&field8=%s' % (temperature,
                                                                                                      humidity, h1,
                                                                                                      h2, h3, h4,
                                                                                                      h5, h6))
            del response


node = greenhouse01.Greenhouse01()
gc.collect()
multiserver = prometheus.server.multiserver.MultiServer()

udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
multiserver.add(udpserver)
gc.collect()

tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
multiserver.add(tcpserver)
gc.collect()

jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
multiserver.add(jsonrestserver, bind_port=8080)
gc.collect()

# jsonrestsslserver = prometheus_servers.JsonRestServer(node,
#                                                       loop_tick_delay=0.1,  # for cpython, limits cpu cycles
#                                                       socketwrapper=prometheus_servers_ssl.SslSocket)
# multiserver.add(jsonrestsslserver, bind_host='', bind_port=4443)
# gc.collect()

localevents = LocalEvents(node)
multiserver.add(localevents)

logging.boot(udpserver)
try:
    multiserver.start()
except:
    gc.collect()

try:
    logging.error('crashed? rst')
except:
    gc.collect()

machine.reset()
