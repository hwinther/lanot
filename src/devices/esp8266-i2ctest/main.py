import machine
import ds1307
import CCS811
import time
import ssd1306
import neopixel
import onewire
import dht
import gc
import prometheus.tftpd

gc.collect()

# 60 oled
# 72 adc
# 90 o2
# 87, 104 = rtc


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


def screenloop(s, d, ds):
    while True:
        if s.data_ready():
            d.fill(0)
            d.text('eCO2 ppm', 0, 0)
            d.text('TVOC ppb', 0, 20)
            d.text(str(s.eCO2) + '   ', 0, 10)
            d.text(str(s.tVOC) + '    ', 0, 30)
            da = ds.datetime()
            d.text('%02d:%02d:%02d  ' % (da[4], da[5], da[6]), 0, 40)
            d.show()
        time.sleep(1)
        machine.idle()


def td():
    prometheus.tftpd.tftpd()


i2c = machine.I2C(scl=machine.Pin(0), sda=machine.Pin(4), freq=400000)
time.sleep(0.5)
print(i2c.scan())

# ds = ds1307.DS1307(i2c)
# d = ssd1306.SSD1306_I2C(128, 64, i2c, 0x3c)
# time.sleep(0.5)
# s = CCS811.CCS811(i2c=i2c, addr=90)

ow = onewire.OneWire(machine.Pin(5, machine.Pin.IN))  # D1
npx = neopixel.NeoPixel(machine.Pin(2), 256)  # D4
dh = dht.DHT11(machine.Pin(12, machine.Pin.OUT))  # D6

gc.collect()
# screenloop(s, d, ds)

# p = machine.Pin(16, machine.Pin.IN)
# while True:
#     if p.value():
#         i2c.writeto(8, 'NECx48B7C837x12')
#     time.sleep(0.1)
