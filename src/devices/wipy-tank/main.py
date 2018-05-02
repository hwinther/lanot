import time
import machine  # this happens in boot and isnt required here, but for the IDE (and as a failsafe)
import os
import untplib
import gc
from tank import Tank
from servers.socketserver.udp import UdpSocketServer

gc.collect()


def uname():
    un = os.uname()
    print('%s %s %s %s %s MicroPython' % (un[0], un[1], un[2], un[3], un[4]))


def update_clock():
    c = untplib.NTPClient()
    resp = c.request('0.no.pool.ntp.org', version=3, port=123)
    print("Offset is ", resp.offset)

    rtc = machine.RTC()
    print("Adjusting clock by ", resp.offset, "seconds")
    rtc.init(time.localtime(time.time() + resp.offset))


# init done
tank = Tank()
# give serial time to sync?
time.sleep_ms(200)
tank.blink_lights(1000)

last_time = time.time()
events = list()


def sensor_react():
    reading = tank.sensor_reading()
    print(str(reading))
    if reading is not None:
        if reading[0] <= 40:
            tank.led_red.on()
        else:
            tank.led_red.off()
        if reading[1] <= 40:
            tank.led_blue.on()
        else:
            tank.led_blue.off()


def second_tick(source_timer):
    global last_time, events
    t = time.time()
    if t - last_time >= 1:
        # led_red.toggle()
        # add distance checking event to queue
        events.append(sensor_react)
        # limit queue to 10 items
        events = events[-10:]
        last_time = t


def start_event_timer():
    timer = machine.Timer(0)
    timer.init(machine.Timer.PERIODIC)
    timer_channel = timer.channel(machine.Timer.B, freq=5)
    timer_channel_irq = timer_channel.irq(handler=second_tick, trigger=machine.Timer.TIMEOUT)

    while True:
        for e in events:
            print('handling event')
            e()
            events.remove(e)


# start_event_timer()
# tank.start_socket_server()
gc.collect()
s = UdpSocketServer(tank)
gc.collect()
s.start()
