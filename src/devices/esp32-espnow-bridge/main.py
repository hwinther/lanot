# import network
import prometheus.pnetwork
import espnow
import time
import urequests
import machine
import network
import ubinascii
from umqtt.simple import MQTTClient


NODE_RED_BASE_URL = "http://10.20.1.58:1880"
# NODE_RED_BASE_URL = 'http://10.20.2.185:80'
MQTT_BROKER = "10.20.1.8"
MQTT_PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
CLIENT_ID = ubinascii.hexlify(machine.unique_id())


def td():
    import prometheus.tftpd
    import prometheus.pnetwork

    prometheus.pnetwork.init_network()
    prometheus.tftpd.tftpd()


def mqtt_connect():
    print("Connecting to MQTT Broker %s" % MQTT_BROKER)
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD)
    client.connect()
    return client


def mqtt_send(
    client: MQTTClient, topic: bytes, message: bytes, qos: int = 0, retain: bool = False
):
    try:
        client.publish(topic, message, qos=qos, retain=retain)
    except OSError as error:
        print("Error sending message, retrying", error)
        try:
            client.reconnect()
            client.publish(topic, message, qos=qos, retain=retain)
        except OSError as error2:
            print("Error sending message (no more retries)", error2)
            return False

    print("Message sent successfully to topic %s", topic)
    return True


# Home Assistant: state goes to a dedicated state topic; discovery uses homeassistant/.../config
# State topic (HA subscribes here): espnow-bridge/<room>/<source>/state
# Discovery topic (one-time config): homeassistant/sensor/espnow_bridge_<room>_<source>/config
def mqtt_publish_ha_sensor(client: MQTTClient, room: str, source: str, state: str):
    state_topic = "espnow-bridge/%s/%s/state" % (room, source)
    payload = b'{"state": "%s"}' % state.encode()
    mqtt_send(client, state_topic.encode(), payload, qos=0, retain=True)

    # Optional: publish MQTT discovery so the entity appears in HA without manual config
    object_id = "espnow_bridge_%s_%s" % (room, source)
    config_topic = ("homeassistant/sensor/%s/config" % object_id).encode()
    config = (
        b'{"name":"%s %s","state_topic":"%s",'
        b'"value_template":"{{ value_json.state }}","unique_id":"%s"}'
    ) % (
        room.encode(),
        source.encode(),
        state_topic.encode(),
        object_id.encode(),
    )
    mqtt_send(client, config_topic, config, qos=0, retain=True)


def http_put_request(room: str, state: str, source: str):
    """Performs an HTTP PUT request with JSON data."""
    payload = {"state": state, "source": source}

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ESP32-MicroPython-Client",
    }

    url = "%s/%s/trigger" % (NODE_RED_BASE_URL, room)

    print(f"Sending PUT request to {url} with payload {payload}")
    try:
        response = urequests.put(url, json=payload, headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        response.close()
        print("Request finished and connection closed.")

    except Exception as ex:
        print(f"An error occurred: {ex}")


# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.WLAN.IF_STA)
# sta.active(True)
# WIFI_CHANNEL = 6
# sta.config(channel=WIFI_CHANNEL)
# sta.config(name='dgn.iot', password='password')
# sta.disconnect()   # Because ESP8266 auto-connects to last Access Point
prometheus.pnetwork.init_network()
print("STA channel:", sta.config("channel"))
integrated_led_pin = machine.Pin(2, machine.Pin.OUT)

e = espnow.ESPNow()
e.active(True)
mqtt_client = mqtt_connect()

print("Entering ESPNow recv loop")
while True:
    host, msg = e.recv()
    if msg:  # msg == None if timeout in recv()
        integrated_led_pin.value(True)
        print(time.time(), host, msg)
        if msg == b"end":
            break
        elif msg == b"ping":
            print("Pong")
        elif msg == b"init":
            print("Device booted up")
        elif msg.count(b"_") >= 2:
            # e.g. storage_on_infra
            parts = msg.split(b"_", 2)
            room = parts[0].decode("ascii")
            state = parts[1].decode("ascii")
            source = parts[2].decode("ascii")
            http_put_request(room, state, source)
            mqtt_publish_ha_sensor(mqtt_client, room, source, state)
        else:
            print("Unknown message format")
        integrated_led_pin.value(False)
