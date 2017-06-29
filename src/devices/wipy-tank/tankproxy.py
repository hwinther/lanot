import sys
import random
import time
import prometheus
import prometheus_servers
sys.path.append('P:\lanot\build\clients')
from tankclient import TankUdpClient


class TankProxy(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
        self.tankclient = TankUdpClient('192.168.1.250', bind_port=random.randrange(1024, 9000))
        self.register(prefix='t', tankclient=self.tankclient)

if __name__ == '__main__':
    tankproxy = TankProxy()
    tankproxy.tankclient.lightControl.all_on()
    time.sleep(2)
    tankproxy.tankclient.lightControl.all_off()
    jsonrest = prometheus_servers.JsonRestServer(tankproxy)
    jsonrest.start()
