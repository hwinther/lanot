import sys
import random
import time
import prometheus
import prometheus.server.socketserver.jsonrest
sys.path.append('P:\\lanot\\deploy\\clients')
from tankclient import TankUdpClient


class TankProxy(prometheus.Prometheus):
    def __init__(self):
        prometheus.Prometheus.__init__(self)
        self.tankclient = TankUdpClient('10.20.2.250', bind_port=random.randrange(1024, 9000))
        self.register(prefix='t', tankclient=self.tankclient)


if __name__ == '__main__':
    tankproxy = TankProxy()
    tankproxy.tankclient.lightControl.all_on()
    time.sleep(2)
    tankproxy.tankclient.lightControl.all_off()
    jsonrest = prometheus.server.socketserver.jsonrest.JsonRestServer(tankproxy)
    jsonrest.start()
