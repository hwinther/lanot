STA_IF = 0
AP_IF = 0


class WLAN(object):
    def __init__(self, interface=None):
        pass

    def active(self, state=None):
        return True

    def isconnected(self):
        return True

    def ifconfig(self):
        return (1,2,3,4)

    def connect(self, ssid, pw):
        pass
