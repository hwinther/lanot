# import network
import prometheus.pnetwork
import espnow
import time


def td():
    import prometheus.tftpd
    import prometheus.pnetwork
    prometheus.pnetwork.init_network()
    prometheus.tftpd.tftpd()


# A WLAN interface must be active to send()/recv()
# sta = network.WLAN(network.WLAN.IF_STA)
# sta.active(True)
# sta.config(name='dgn.iot', password='umbFUTyJSvqhxNrQ')
# sta.disconnect()   # Because ESP8266 auto-connects to last Access Point
prometheus.pnetwork.init_network()

e = espnow.ESPNow()
e.active(True)

print('Entering ESPNow recv loop')
while True:
    host, msg = e.recv()
    if msg:             # msg == None if timeout in recv()
        print(time.time(), host, msg)
        if msg == b'end':
            break
