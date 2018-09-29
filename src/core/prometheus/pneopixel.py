# coding=utf-8
import prometheus
import machine
import neopixel
import prometheus.logging as logging
import gc

__version__ = '0.1.0'
__author__ = 'Hans Christian Winther-Sorensen'

gc.collect()


class NeoPixel(prometheus.Prometheus):
    np = None  # type: neopixel.NeoPixel

    def __init__(self, pin, number):
        """
        esp8266 pcb rev01b: pin 2 (GPIO 4)
        :type pin: machine.Pin
        :type number: int
        """
        prometheus.Prometheus.__init__(self)
        self.np = neopixel.NeoPixel(pin, number)
        self.n = number

    @prometheus.Registry.register('NeoPixel', 'sp')
    def set_pixel(self, pixel, r, g, b, **kwargs):
        # combination of the two methods below
        if not isinstance(pixel, int):
            pixel = int(pixel)
        if not isinstance(r, int):
            r = int(r)
        if not isinstance(g, int):
            g = int(g)
        if not isinstance(b, int):
            b = int(b)
        logging.info('setting and writing np[%d] = %s' % (pixel, (r, g, b)))
        self.np[pixel] = (r, g, b)
        self.np.write()

    @prometheus.Registry.register('NeoPixel', 's')
    def set(self, pixel, r, g, b, **kwargs):
        if not isinstance(pixel, int):
            pixel = int(pixel)
        if not isinstance(r, int):
            r = int(r)
        if not isinstance(g, int):
            g = int(g)
        if not isinstance(b, int):
            b = int(b)
        logging.info('setting np[%d] = %s' % (pixel, (r, g, b)))
        self.np[pixel] = (r, g, b)

    @prometheus.Registry.register('NeoPixel', 'wr')
    def write(self, **kwargs):
        logging.info('writing np')
        self.np.write()

    # def custom_command(self, command, reply, source, **kwargs):
    #     if not len(command) > 3 or not command[0:3] == 'np ':
    #         return prometheus.Prometheus.custom_command(self, command, reply, source, **kwargs)
    #
    #     params = command[3:].split(' ')
    #     if not len(params) == 4 or not params[0].isdigit():
    #         return prometheus.Prometheus.custom_command(self, command, reply, source, **kwargs)
    #
    #     led = int(params[0])
    #     if led > self.n or led < 0:
    #         return prometheus.Prometheus.custom_command(self, command, reply, source, **kwargs)
    #
    #     values = list()
    #     for value in params[1:4]:
    #         if not value.isdigit():
    #             return prometheus.Prometheus.custom_command(self, command, reply, source, **kwargs)
    #
    #         value = int(value)
    #         if value > 255 or value < 0:
    #             return prometheus.Prometheus.custom_command(self, command, reply, source, **kwargs)
    #
    #         values.append(value)
    #
    #     self.set_pixel(led, values[0], values[1], values[2])
    #     gc.collect()
    #
    #     return True
