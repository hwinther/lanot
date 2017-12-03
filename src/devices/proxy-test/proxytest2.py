import sys
import random
import time
import prometheus
import prometheus_servers
import prometheus_servers_ssl
# sys.path.append('P:\lanot\build\clients')
import deploy.clients.sensor01client as sensor01client
import deploy.clients.sensor02client as sensor02client
import deploy.clients.nodetestclient as nodetestclient
import deploy.clients.tankclient as tankclient


class ProxyTest2(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)

        self.sensor01 = sensor01client.Sensor01UdpClient('sensor01', bind_port=random.randrange(1024, 9000))
        self.register(prefix='s1', sensor01=self.sensor01)

        self.sensor02 = sensor02client.Sensor02UdpClient('sensor02', bind_port=random.randrange(1024, 9000))
        self.register(prefix='s2', sensor02=self.sensor02)

        # self.nodetest = nodetestclient.NodeTestRsaUdpClient('nodetest', bind_port=random.randrange(1024, 9000))
        # self.register(prefix='nt', nodetest=self.nodetest)

        # self.tankclient = tankclient.TankUdpClient('192.168.1.250', bind_port=random.randrange(1024, 9000))
        # self.register(prefix='tc', tankclient=self.tankclient)


if __name__ == '__main__':
    node = ProxyTest2()
    # print('off')
    # proxytest2.sensor01.integrated_led.off()
    # proxytest2.sensor02.integrated_led.off()
    # proxytest2.nodetest.integrated_led.off()
    # proxytest2.tankclient.lightControl.all_on()
    # time.sleep(2)
    # print('on')
    # proxytest2.sensor01.integrated_led.on()
    # proxytest2.sensor02.integrated_led.on()
    # proxytest2.nodetest.integrated_led.on()
    # proxytest2.tankclient.lightControl.all_off()

    multiserver = prometheus_servers.MultiServer()

    udpserver = prometheus_servers.UdpSocketServer(node)
    multiserver.add(udpserver, bind_host='', bind_port=9190)

    tcpserver = prometheus_servers.TcpSocketServer(node)
    multiserver.add(tcpserver, bind_host='', bind_port=9191)

    jsonrestserver = prometheus_servers.JsonRestServer(node,
                                                       loop_tick_delay=0.1)
    multiserver.add(jsonrestserver, bind_host='', bind_port=8080)

    jsonrestsslserver = prometheus_servers.JsonRestServer(node,
                                                          loop_tick_delay=0.1,  # for cpython, limits cpu cycles
                                                          socketwrapper=prometheus_servers_ssl.SslSocket)
    multiserver.add(jsonrestsslserver, bind_host='', bind_port=4443)

    multiserver.start()

    # time.struct_time(tm_year=2017, tm_mon=9, tm_mday=3, tm_hour=1, tm_min=22, tm_sec
    # =54, tm_wday=6, tm_yday=246, tm_isdst=1)
    # lt = time.localtime()
    #
    # yd = 2016 - lt[0] * 365 * 24 * 60 * 60
    # et = yd
    # md = lt[1] * 24 * 60 * 60
    # et = et + md
    # dd = lt[2] * 60 * 60
    # et = et + dd
    # hd = lt[3] * 60
    # et = et + hd
    # et = et + lt[4]
