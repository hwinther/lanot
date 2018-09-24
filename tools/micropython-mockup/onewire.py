class OneWire(object):
    def __init__(self, pin):
        self.pin = pin

    def scan(self):
        return list()


class OneWireError(object):
    pass
