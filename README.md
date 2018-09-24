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
