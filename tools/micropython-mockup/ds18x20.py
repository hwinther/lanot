class DS18X20(object):
    def __init__(self, ow):
        self.ow = ow

    def scan(self):
        return list('')

    def convert_temp(self):
        pass

    def read_temp(self, addr):
        return 25.1234
