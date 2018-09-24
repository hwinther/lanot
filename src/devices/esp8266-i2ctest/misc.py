import machine
import time
import max7219
import gc

gc.collect()


def cycle(np, n):
    # cycle
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 0)
        np[i % n] = (255, 255, 255)
        np.write()
        # time.sleep_ms(25)


def bounce(np, n):
    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)


def fade(np, n):
    # fade in/out
    for i in range(0, 4 * 256, 8):
        for j in range(n):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()


def clear(np, n):
    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()


def demo(np):
    n = np.n
    cycle(np, n)
    bounce(np, n)
    clear(np, n)


def screenloop(s, d, ds, dh, ds18):
    while True:
        d.fill(0)

        if s is not None and s.data_ready():
            d.text('eCO2 ppm', 0, 0)
            d.text('TVOC ppb', 0, 20)
            d.text(str(s.eCO2) + '   ', 0, 10)
            d.text(str(s.tVOC) + '    ', 0, 30)

        if ds is not None:
            da = ds.datetime()
            d.text('%02d:%02d:%02d  ' % (da[4], da[5], da[6]), 0, 40)

        if dh is not None:
            dh.measure()
            d.text('%dC %d%%' % (dh.temperature(), dh.humidity()), 0, 50)

        if ds18 is not None:
            d.text('%s' % ds18.value(), 60, 50)

        d.show()
        time.sleep(1)
        machine.idle()


def maxtest():
    spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0)
    display = max7219.Matrix8x8(spi, machine.Pin(15), 4)
    display.brightness(0)
    display.fill(0)
    display.text('1234', 0, 0, 1)
    display.show()
