STA_IF = 0
AP_IF = 0

# TODO: there are a lot of holes here, and i have not checked which parameters are required


class WLAN(object):
    EXT_ANT = 0
    INT_ANT = 0
    STA = 0
    WPA2 = 0

    def __init__(self, interface=None):
        pass

    def init(self, type, antenna=None):
        pass

    def active(self, state=None):
        return True

    def isconnected(self):
        return True

    def ifconfig(self, config=None):
        return (1,2,3,4)

    def connect(self, ssid, password=None, auth=None, timeout=None, bssid=None):
        pass


class Server(object):
    def __init__(self):
        pass

    def deinit(self):
        pass

    def init(self, login=None, timeout=None):
        pass
