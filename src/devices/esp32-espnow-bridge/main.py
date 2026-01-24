# import network
import prometheus.pnetwork
import espnow
import time
import urequests
import machine


# NODE_RED_BASE_URL = 'http://10.20.1.58:1880'
NODE_RED_BASE_URL = 'http://10.20.2.185:80'


def td():
    import prometheus.tftpd
    import prometheus.pnetwork
    prometheus.pnetwork.init_network()
    prometheus.tftpd.tftpd()


def http_put_request(room: str, state: str, source: str):
    """Performs an HTTP PUT request with JSON data."""
    payload = {
        "state": state,
        "source": source
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'ESP32-MicroPython-Client'
    }

    url = '%s/%s/trigger' % (NODE_RED_BASE_URL, room)

    print(f"Sending PUT request to {url}...")
    try:
        response = urequests.put(url, json=payload, headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        response.close()
        print("Request finished and connection closed.")

    except Exception as ex:
        print(f"An error occurred: {ex}")


# A WLAN interface must be active to send()/recv()
# sta = network.WLAN(network.WLAN.IF_STA)
# sta.active(True)
# sta.config(name='dgn.iot', password='password')
# sta.disconnect()   # Because ESP8266 auto-connects to last Access Point
prometheus.pnetwork.init_network()
integrated_led_pin = machine.Pin(2, machine.Pin.OUT)

e = espnow.ESPNow()
e.active(True)

print('Entering ESPNow recv loop')
while True:
    host, msg = e.recv()
    if msg:             # msg == None if timeout in recv()
        integrated_led_pin.value(True)
        print(time.time(), host, msg)
        if msg == b'end':
            break
        elif msg == b'ping':
            print('Pong')
        elif msg == b'init':
            print('Device booted up')
        elif msg.count(b'_') >= 2:
            # e.g. storage_on_infra
            parts = msg.split(b'_', 2)
            room = parts[0].decode('ascii')
            state = parts[1].decode('ascii')
            source = parts[2].decode('ascii')
            http_put_request('storage', 'on', source)
        else:
            print("Unknown message format")
        integrated_led_pin.value(False)
