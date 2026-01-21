import test02
import machine
import network
import time
import esp32
import espnow
import prometheus.pgc as gc
import prometheus.logging as logging

gc.collect()


def td():
    import prometheus.tftpd
    import prometheus.pnetwork
    prometheus.pnetwork.init_network()
    prometheus.tftpd.tftpd()


def wifi_reset():
    sta = network.WLAN(network.WLAN.IF_STA)
    sta.active(False)
    ap = network.WLAN(network.WLAN.IF_AP)
    ap.active(False)
    sta.active(True)
    while not sta.active():
        time.sleep(0.1)
    sta.disconnect()   # For ESP8266
    while sta.isconnected():
        time.sleep(0.1)
    return sta, ap


class DelayedSender:
    delay_time: int = None
    last_send: int = None

    def __init__(self, delay_time: int):
        self.delay_time = delay_time
        self.last_send = -100

    def send(self, peer_addr: bytes, data: bytes):
        t = int(time.time())
        if t - self.last_send > self.delay_time:
            self.last_send = t
            print('Passed %d time, sending %s' % (self.delay_time, data))
            send_esp_now(peer_addr, data)
            return True
        return False


reset_cause = machine.reset_cause()
wake_reason = machine.wake_reason()
print('reset cause: %s wake_reason: %s' % (reset_cause, wake_reason))

node = test02.Test02()
gc.collect()
logging.debug(gc.mem_free())

print('disabling wifi and enabling ESPNow')
sta, ap = wifi_reset()
WIFI_CHANNEL = 6
sta.config(channel=WIFI_CHANNEL)
peer = b'0\xae\xa4\x1c\xb5\x8c'
e = espnow.ESPNow()
e.active(True)
e.add_peer(peer)


def send_esp_now(peer_addr: bytes, data: bytes):
    sta.active(True)
    sta.config(channel=WIFI_CHANNEL)
    print('Sending data to peer...')
    if not e.send(peer_addr, data):
        print('Send failed!')
    else:
        print('Send success!')


class PinState:
    name: str = None
    state: bool = None

    def __init__(self, name, initial_state=None):
        self.name = name
        self.initial_state = False if initial_state is None else initial_state
        self.state = False if initial_state is None else initial_state

    def set(self):
        self.state = not self.initial_state

    def reset(self):
        self.state = self.initial_state


pin_state_door = PinState('door', initial_state=True)
pin_state_infrared = PinState('infrared')
pin_state_light = PinState('light')

pin_states = {
    id(node.door_sensor.pin): pin_state_door,
    id(node.infrared_sensor.pin): pin_state_infrared,
    id(node.light_switch.pin): pin_state_light,
}


def wake_from_light_sleep(pin):
    """Interrupt handler called on any pin change."""
    # print('Wake handler on pin', pin, id(pin), pin_states[id(pin)].name)
    pin_states[id(pin)].set()


node.door_sensor.pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=wake_from_light_sleep)
node.infrared_sensor.pin.irq(trigger=machine.Pin.IRQ_RISING, handler=wake_from_light_sleep)
node.light_switch.pin.irq(trigger=machine.Pin.IRQ_RISING, handler=wake_from_light_sleep)

wake_on_ext0_pin = node.door_sensor.pin
print('set wake_on_ext0 pin')
esp32.wake_on_ext0(wake_on_ext0_pin, esp32.WAKEUP_ALL_LOW)
wake_on_ext1_pins = [node.infrared_sensor.pin, node.light_switch.pin]
print('set wake_on_ext1 pins')
esp32.wake_on_ext1(wake_on_ext1_pins, esp32.WAKEUP_ANY_HIGH)
gc.collect()

ping_sender = DelayedSender(delay_time=60)
door_open_sender = DelayedSender(delay_time=10)
infrared_activity_sender = DelayedSender(delay_time=10)
switch_activated_sender = DelayedSender(delay_time=3)

previous_door_state = node.door_sensor.pin.value()

while True:
    if ping_sender.send(peer, b'ping'):
        print('States: d %d ir %d sw %d' % (node.door_sensor.pin.value(),
                                            node.infrared_sensor.pin.value(),
                                            node.light_switch.pin.value()))

    sensor_activity = False

    door_state = node.door_sensor.pin.value()
    print('ds %d pds %d' % (door_state, previous_door_state))
    if door_state != previous_door_state:
        sensor_activity = True
        previous_door_state = door_state
        if door_state:
            door_open_sender.send(peer, b'door_closed')
        else:
            door_open_sender.send(peer, b'door_open')
        # holdover for now:
        if not pin_state_door.state:
            print('reset 1')
            pin_state_door.reset()
        else:
            print('reset 2')

    if pin_state_infrared.state:
        sensor_activity = True
        infrared_activity_sender.send(peer, b'infra')
        pin_state_infrared.reset()

    if pin_state_light.state:
        sensor_activity = True
        switch_activated_sender.send(peer, b'switch')
        pin_state_light.reset()

    if not sensor_activity:
        # If we get here the sensor is LOW – nothing else to do.
        print('Sleep - States: d %d ir %d sw %d' % (node.door_sensor.pin.value(),
                                                    node.infrared_sensor.pin.value(),
                                                    node.light_switch.pin.value()))
        time.sleep_ms(100)

        machine.lightsleep(60 * 1000)
        # time.sleep_ms(10000)  # Temporary to separate lightsleep issues from state logic
