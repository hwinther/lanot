# lanot

###### Local Area Network Of Things

## Overview

lanot is a collection of applications and application framework/framework support.

### prometheus

[src/core/prometheus](src/core/prometheus) micropython device framework

Supports cpython testing via [micropython-mockup](tools/micropython-mockup)

Currently fully supporting the esp8266 (12E) and esp32 platforms, more might be added later.

HTML5 client can be found under [test/html5ui](test/html5ui)

Proxy clients for devices are under [test/html5ui](test/html5ui)

[Python client proxy generator](test/html5ui)

## Example devices can be found under [src/devices](src/devices)

* chain-test
  * test device that chains the client proxy C(B(A))) (no pun intended)
* cpython-local-test
  * cpython compatible test device
* esp32-greenhouse01/02
  * esp32 device that measures humidity via 6 hygrometers (soil water via adc0-5) and a dht11
  * displays values on a i2c ssd1306 oled screen (64x128)
* esp-rover01
  * rover (robot) wrapper for arduino h-bridge device
* esp32-test01-03
  * development test devices, changes over time
* esp8266-nodetest
  * development test device, should implement everything supported on the rev02b pcb
  * onewire (dht11), ds18b20, neopixel, i2c (ssd1306, ccs822, ds1307, nano ir & gpio extender)
* esp8266-sensor01/02
  * dht & ds18b20 temperature and humidity sensors
 
## Current hardware support
  ##### Note: pin typically means an instance of Machine.Pin

##### `prometheus.Prometheus.Led(pin, inverted=False, state=None)` - light emitting diode

###### Generic node example:
    self.integrated_led = prometheus.Led(machine.Pin(2, machine.Pin.OUT), inverted=True)
    self.register(prefix='i', integrated_led=self.integrated_led)

##### `prometheus.Prometheus.Digital(pin, inverted=False)` - digital output, similar to Led

###### Generic node example:
    self.digital_relay = prometheus.Digital(machine.Pin(2, machine.Pin.OUT))
    self.register(prefix='r', integrated_led=self.digital_relay)

##### `prometheus.Prometheus.Adc(pin)` - Analog to digital converter, wrapper for the single ADC on esp8266, and the 6 that are typically exposed on esp32

###### esp8266 node example:
    self.adc1 = prometheus.Adc(0)
    self.register(prefix='a', adc1=self.adc1)

###### esp32 node example:
    self.hygrometer01 = prometheus.Adc(machine.Pin(36, machine.Pin.IN))
    self.register(prefix='h1', hygrometer01=self.hygrometer01)
    self.hygrometer01.adc.width(machine.ADC.WIDTH_12BIT)
    self.hygrometer01.adc.atten(machine.ADC.ATTN_11DB)

##### `prometheus.dht11.Dht11(pin)`, `prometheus.dht22.Dht22(pin)` - DHT11/22 temperature and humidity sensor

###### Generic node example:
    self.dht11 = prometheus.dht11.Dht11(machine.Pin(12, machine.Pin.OUT))
    self.register(prefix='d', dht11=self.dht11)

##### `prometheus.pds18x20.Ds18x20(pin=None, ow=None)` - ds18x20 onewire temperature sensor

###### Generic node example:
    self.dsb = prometheus.pds18x20.Ds18x20(ow=self.onewire)
    self.register(prefix='s', dsb=self.dsb)


## Devices that will be supported soon:
* ssd1306 oled display of various sizes (64x128 is common)
* ccs822 air quality sensor (co2 & ppm)
* ds1307+ real time clock
* max7219 (led matrix, e.g. 8x32)
* neopixel (rgb led matrix, chain, or similar)
* nanoi2c (subproject)
* ads1115 (4 channel adc)
