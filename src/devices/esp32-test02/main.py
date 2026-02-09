# import test02
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

# node = test02.Test02()
door_sensor_pin = machine.Pin(32, machine.Pin.IN, machine.Pin.PULL_DOWN)
infrared_sensor_pin = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_DOWN)
light_switch_pin = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_DOWN)

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
    id(door_sensor_pin): pin_state_door,
    id(infrared_sensor_pin): pin_state_infrared,
    id(light_switch_pin): pin_state_light,
}


def wake_from_light_sleep(pin):
    """Interrupt handler called on any pin change."""
    # print('Wake handler on pin', pin, id(pin), pin_states[id(pin)].name)
    pin_states[id(pin)].set()


infrared_sensor_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=wake_from_light_sleep)
light_switch_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=wake_from_light_sleep)

wake_on_ext1_pins = [infrared_sensor_pin, light_switch_pin]
print('set wake_on_ext1 pins')
esp32.wake_on_ext1(wake_on_ext1_pins, esp32.WAKEUP_ANY_HIGH)
gc.collect()

ping_sender = DelayedSender(delay_time=60)
infrared_activity_sender = DelayedSender(delay_time=10)
switch_activated_sender = DelayedSender(delay_time=3)


class DoorSensor:
    pin: machine.Pin = None
    light_sleep_ext0_enabled: bool = None
    state: bool = None
    previous_state: bool = None
    changed: bool = None
    door_open_sender: DelayedSender = None

    def __init__(self, pin, light_sleep_ext0_enabled=False):
        self.pin = pin
        self.light_sleep_ext0_enabled = light_sleep_ext0_enabled

        # TODO: when light_sleep_ext0_enabled is not enabled, use timer instead?
        self.state = pin.value()
        self.door_open_sender = DelayedSender(delay_time=10)

        if light_sleep_ext0_enabled:
            self.update_ext0()

    def callback(self, pin):
        self.previous_state = self.state
        self.state = pin.value()
        if self.previous_state != self.state:
            print('set changed in cb')
            self.changed = True
        else:
            print('cb with no change')

    def update_ext0(self):
        print('set wake_on_ext0 pin for door pin state %s to %s' % (self.state,
                                                                    'WAKEUP_ALL_LOW' if self.state
                                                                    else 'WAKEUP_ANY_HIGH'))

        if self.state:
            esp32.wake_on_ext0(self.pin, esp32.WAKEUP_ALL_LOW)
        else:
            esp32.wake_on_ext0(self.pin, esp32.WAKEUP_ANY_HIGH)

        print('set irq for door pin to trigger on %s' % ('IRQ_FALLING' if self.state else 'IRQ_RISING'))
        self.pin.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING,
                     handler=self.callback)

    def handle(self):
        if not self.changed:
            return False

        self.changed = False
        print('ds %d pds %d' % (self.state, self.previous_state))

        if self.state:
            # door closed (switch closed)
            self.door_open_sender.send(peer, b'office_closed_door')
        else:
            # door open (switch open)
            self.door_open_sender.send(peer, b'office_open_door')

        if self.light_sleep_ext0_enabled:
            self.update_ext0()

        return True


esp32.wake_on_ext0(door_sensor_pin, esp32.WAKEUP_ALL_LOW)
door_sensor = DoorSensor(door_sensor_pin, True)
send_esp_now(peer, b'init')

while True:
    if ping_sender.send(peer, b'ping'):
        print('States: d %d ir %d sw %d' % (door_sensor_pin.value(),
                                            infrared_sensor_pin.value(),
                                            light_switch_pin.value()))

    sensor_activity = False

    if door_sensor.handle():
        sensor_activity = True

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
        print('Sleep - States: d %d ir %d sw %d' % (door_sensor_pin.value(),
                                                    infrared_sensor_pin.value(),
                                                    light_switch_pin.value()))
        time.sleep_ms(100)
        machine.lightsleep(60 * 1000)

        # time.sleep_ms(10000)  # Temporary to separate lightsleep issues from state logic
