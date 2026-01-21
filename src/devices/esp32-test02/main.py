import test02
import machine
import network
import time
import esp32
import espnow
import prometheus.pgc as gc
# import prometheus.server.multiserver
# import prometheus.server.socketserver.udp
# import prometheus.server.socketserver.tcp
# import prometheus.server.socketserver.jsonrest
import prometheus.logging as logging

gc.collect()


def td():
    import prometheus.tftpd
    import prometheus.pnetwork
    prometheus.pnetwork.init_network()
    prometheus.tftpd.tftpd()


def wifi_reset():   # Reset wifi to AP_IF off, STA_IF on and disconnected
  sta = network.WLAN(network.WLAN.IF_STA); sta.active(False)
  ap = network.WLAN(network.WLAN.IF_AP); ap.active(False)
  sta.active(True)
  while not sta.active():
      time.sleep(0.1)
  sta.disconnect()   # For ESP8266
  while sta.isconnected():
      time.sleep(0.1)
  return sta, ap


class DelayedSender:
    def __init__(self, delay_time: int):
        self.delay_time = delay_time
        self.last_send = -100

    def send(self, peer_addr: bytes, data: bytes):
        if time.time() - self.last_send > 60:
            self.last_send = time.time()
            print('Passed %d time, sending %s' % (self.delay_time, data))
            send_esp_now(peer_addr, data)


reset_cause = machine.reset_cause()
wake_reason = machine.wake_reason()
print('reset cause: %s wake_reason: %s' % (reset_cause, wake_reason))
#if machine.reset_cause() == machine.DEEPSLEEP_RESET:
#    print('woke from a deep sleep')


node = test02.Test02()
gc.collect()
logging.debug(gc.mem_free())
# multiserver = prometheus.server.multiserver.MultiServer()
#
# udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
# multiserver.add(udpserver)
# gc.collect()
#
# # tcpserver = prometheus.server.socketserver.tcp.TcpSocketServer(node)
# # multiserver.add(tcpserver)
# # gc.collect()
#
# jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, loop_tick_delay=0.1)
# multiserver.add(jsonrestserver, bind_port=8080)
# gc.collect()
#
# logging.boot(udpserver)
# # udpserver.start()
# multiserver.start()


# self.door_sensor = prometheus.Digital(machine.Pin(32, machine.Pin.IN, machine.Pin.PULL_DOWN))
# self.register(prefix='d', door_sensor=self.door_sensor)

# self.infrared_sensor = prometheus.Digital(machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_DOWN))
# self.register(prefix='s', infrared_sensor=self.infrared_sensor)

# self.light_switch = prometheus.Digital(machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_DOWN))
# self.register(prefix='l', light_switch=self.light_switch)

# import esp32
# self.wake_pins = [self.door_sensor.pin, self.infrared_sensor.pin, self.light_switch.pin]
# print('set wake_on_gpio pins')
# esp32.wake_on_gpio(self.wake_pins, esp32.WAKEUP_ANY_HIGH)
# gc.collect()


# while True:
#     print("wr %d" % (machine.wake_reason()))
#     print("d %d i %d l %d" % (int(node.door_sensor.value()),
#                               int(node.infrared_sensor.value()),
#                               int(node.light_switch.value())))
#     print('ls 10k')
#     # machine.deepsleep(10*1000)
#     machine.lightsleep(10*1000)

print('disabling wifi and enabling ESPNow')
sta, ap = wifi_reset()            # Reset wifi to AP off, STA on and disconnected
WIFI_CHANNEL = 6
sta.config(channel=WIFI_CHANNEL)
peer = b'0\xaa\xaa\xaa\xaa\xaa'   # MAC address of peer
e = espnow.ESPNow()
e.active(True)
e.add_peer(peer)                  # Register peer on STA_IF


def send_esp_now(peer_addr: bytes, data: bytes):
    sta.active(True)
    sta.config(channel=WIFI_CHANNEL)
    print('Sending data to peer...')
    if not e.send(peer_addr, data):
        print('Send failed!')
    else:
        print('Send success!')


def wake_from_light_sleep(pin):
    """Interrupt handler called on any pin change."""
    # we don't do anything here – the main loop will handle it.
    print('Wake handler on pin', pin)
    pass


# node.door_sensor.pin.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
node.door_sensor.pin.irq(trigger=machine.Pin.IRQ_RISING,
                         handler=wake_from_light_sleep)

wake_pins = [node.door_sensor.pin, node.infrared_sensor.pin, node.light_switch.pin]
wake_pins_ids = [0, 1, 2]
print('set wake_on_gpio pins')
esp32.wake_on_ext1(wake_pins, esp32.WAKEUP_ANY_HIGH)
gc.collect()

ping_sender = DelayedSender(delay_time=60)
door_open_sender = DelayedSender(delay_time=10)

while True:
    ping_sender.send(peer, b'ping')

    machine.lightsleep(60 * 1000)

    new_wake_pins = []
    new_wake_pins_ids = []

    if node.door_sensor.pin.value() == 1:
        door_open_sender.send(peer, b'alert')
        time.sleep_ms(100)

        # Immediately go back to light‑sleep
        continue
    else:
        new_wake_pins.append(node.door_sensor.pin)
        new_wake_pins_ids.append(0)

    if node.infrared_sensor.pin.value() == 1:
        pass
    else:
        new_wake_pins.append(node.infrared_sensor.pin)
        new_wake_pins_ids.append(1)

    if node.light_switch.pin.value() == 1:
        pass
    else:
        new_wake_pins.append(node.light_switch.pin)
        new_wake_pins_ids.append(2)

    if wake_pins_ids != new_wake_pins_ids:
        wake_pins = new_wake_pins
        wake_pins_ids = new_wake_pins_ids
        print('set wake_on_gpio pins', wake_pins)
        esp32.wake_on_ext1(wake_pins, esp32.WAKEUP_ANY_HIGH)

    # If we get here the sensor is LOW – nothing else to do.
    print("Sensor low – going back to sleep")
    time.sleep_ms(100)
