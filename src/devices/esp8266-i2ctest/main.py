import machine
import ds1307
import CCS811
import time
import ssd1306
# import neopixel
import onewire
import prometheus.pds18x20
import nanoi2c
import misc
# import dht
import gc
import prometheus.tftpd

gc.collect()


def td():
    prometheus.tftpd.tftpd()
    gc.collect()


def gcc():
    gc.collect()
    print(gc.mem_free())
    gc.collect()


i2 = machine.I2C(scl=machine.Pin(0), sda=machine.Pin(4), freq=400000)
time.sleep(0.5)
# scan = list()
scan = i2.scan()
print(scan)
# 60 = oled
# 72 = adc
# 90 = o2
# 87, 104 = rtc
# 8 = nano

nano = None
if 8 in scan:
    print('Detected Nano')
    nano = nanoi2c.NanoI2C(i2)

d = None
if 60 in scan:
    print('Detected SSD1306 display')
    d = ssd1306.SSD1306_I2C(128, 64, i2, 0x3c)
    d.text('init', 0, 0)
    d.show()

ds = None
if 87 in scan and 104 in scan:
    print('Detected DS1307')
    ds = ds1307.DS1307(i2)

s = None
if 90 in scan:
    print('Detected CCS811')
    time.sleep(0.5)
    s = CCS811.CCS811(i2c=i2, addr=90)

# ow = None
ow = onewire.OneWire(machine.Pin(5, machine.Pin.IN))  # D1
ow_scan = ow.scan()
ds18 = None
if len(ow_scan) != 0:
    # print(ow_scan)
    ds18 = prometheus.pds18x20.Ds18x20(ow=ow)

# npx = neopixel.NeoPixel(machine.Pin(2), 256)  # D4
dh = None
# dh = dht.DHT11(machine.Pin(12, machine.Pin.OUT))  # D6

gc.collect()
print(gc.mem_free())
misc.screenloop(s, d, ds, dh, ds18)

# p = machine.Pin(16, machine.Pin.IN)
# while True:
#     if p.value():
#         i2c.writeto(8, 'NECx48B7C837x12')
#     time.sleep(0.1)
