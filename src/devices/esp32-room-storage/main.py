import machine
import network
import time
import esp32
import espnow
import prometheus.pgc as gc
import prometheus.logging as logging


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
            if DEBUG:
                print('Passed %d time, sending %s' % (self.delay_time, data))
            send_esp_now(peer_addr, data)
            return True
        return False


gc.collect()
DEBUG = True

integrated_led_pin = machine.Pin(2, machine.Pin.OUT)
infrared_sensor_pin = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_DOWN)
gc.collect()
logging.debug(gc.mem_free())

if DEBUG:
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
    integrated_led_pin.value(True)
    if DEBUG:
        print('Sending %s to peer %s' % (repr(data), repr(peer_addr)))
    if not e.send(peer_addr, data):
        if DEBUG:
            print('Send failed!')
    else:
        if DEBUG:
            print('Send success!')
    integrated_led_pin.value(False)


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
    id(infrared_sensor_pin): pin_state_infrared,
}


def wake_from_light_sleep(pin):
    """Interrupt handler called on any pin change."""
    # print('Wake handler on pin', pin, id(pin), pin_states[id(pin)].name)
    pin_states[id(pin)].set()


infrared_sensor_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=wake_from_light_sleep)

wake_on_ext1_pins = [infrared_sensor_pin]
if DEBUG:
    print('set wake_on_ext1 pins')
esp32.wake_on_ext1(wake_on_ext1_pins, esp32.WAKEUP_ANY_HIGH)
gc.collect()

ping_sender = DelayedSender(delay_time=60)
infrared_activity_sender = DelayedSender(delay_time=10)
send_esp_now(peer, b'init')

while True:
    if ping_sender.send(peer, b'ping'):
        if DEBUG:
            print('States: ir %d' % (infrared_sensor_pin.value()))

    sensor_activity = False

    if pin_state_infrared.state:
        sensor_activity = True
        infrared_activity_sender.send(peer, b'storage_on_infra')
        pin_state_infrared.reset()

    if not sensor_activity:
        # If we get here the sensor is LOW – nothing else to do.
        if DEBUG:
            print('Sleep - States: ir %d' % (infrared_sensor_pin.value()))

        # time.sleep_ms(1000)
        # machine.lightsleep(60 * 1000)

        time.sleep_ms(10000)  # Temporary to separate lightsleep issues from state logic
