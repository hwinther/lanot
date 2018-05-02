import test01
import servers.socketserver.udp
import servers.multiserver
import prometheus_tftpd
import prometheus_logging as logging
import prometheus_gc as gc
import machine
import time
import socket
import rover01client


gc.collect()


def td():
    prometheus_tftpd.tftpd()


node = test01.Test01()
multiserver = servers.multiserver.MultiServer()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())

udpserver = servers.socketserver.udp.UdpSocketServer(node)
# multiserver.add(udpserver)
# gc.collect()
#
# tcpserver = prometheus_servers.TcpSocketServer(node)
# multiserver.add(tcpserver)
# gc.collect()
#
# jsonrestserver = prometheus_servers.JsonRestServer(node, loop_tick_delay=0.1)
# multiserver.add(jsonrestserver, bind_port=8080)
# gc.collect()

# jsonrestsslserver = prometheus_servers.JsonRestServer(node,
#                                                       loop_tick_delay=0.1,  # for cpython, limits cpu cycles
#                                                       socketwrapper=prometheus_servers_ssl.SslSocket)
# multiserver.add(jsonrestsslserver, bind_port=4443)
# gc.collect()

logging.boot(udpserver)
# multiserver.start()

x_calibration_forward = 1800
x_calibration_backward = 1940
y_calibration_left = 2100
y_calibration_right = 1940
switch_calibration = 50


def joystickread():
    x = node.joystickx.read()
    y = node.joysticky.read()
    # sw = node.joystickswitch.value()
    sw = node.switch.value()
    # print('x=%d y=%d sw=%d' % (x, y, sw))

    if x < x_calibration_forward:
        xdir = 'forward'
    elif x > x_calibration_backward:
        xdir = 'backward'
    else:
        xdir = ''

    if y > y_calibration_left:
        ydir = 'left'
    elif y < y_calibration_right:
        ydir = 'right'
    else:
        ydir = ''

    if xdir != '' or ydir != '':
        print('%s %s - x=%d y=%d sw=%d' % (xdir, ydir, x, y, sw))
    return sw


def jl():
    sc = 0
    old_xdir = ''
    old_ydir = ''
    touch = machine.TouchPad(machine.Pin(4))
    rc = 0
    timer = time.ticks_ms()
    driving = False
    host = 'rover01.iot.oh.wsh.no'
    ip = socket.getaddrinfo(host, 9195)[-1][-1][0]
    udp = rover01client.Rover01UdpClient(ip, remote_port=9195, bind_port=9191)

    while True:
        x = node.joystickx.read()
        y = node.joysticky.read()
        # sw = node.joystickswitch.value()
        sw = node.switch.value()
        # print('x=%d y=%d sw=%d' % (x, y, sw))
        r = touch.read()

        if x < x_calibration_forward:
            xdir = 'forward'
        elif x > x_calibration_backward:
            xdir = 'backward'
        else:
            xdir = ''

        if y > y_calibration_left:
            ydir = 'left'
        elif y < y_calibration_right:
            ydir = 'right'
        else:
            ydir = ''

        # if xdir != '' or ydir != '':
        if old_xdir != xdir or old_ydir != ydir:
            print('%s %s (%d, %d)' % (xdir, ydir, x, y))
            old_xdir = xdir
            old_ydir = ydir

        # sw = joystickread()
        if sw == 0:
            # button down
            sc += 1
        elif sc != 0:
            # button up
            print('button up - sc=%d' % sc)
            sc = 0

        if sc > switch_calibration:
            # button held
            # print('click - sc=%d' % sc)
            pass

        if r == 0:
            if rc == 0:
                # touch active
                print('touch active')
            rc += 1
        elif rc != 0:
            # touch inactive
            print('touch inactive - rc=%d' % rc)
            rc = 0

        current_time = time.ticks_ms()
        if current_time - timer >= 500:
            timer = current_time
            if xdir == 'forward' and ydir == 'left':
                driving = True
                print('sending strafe forward left')
                udp.strafe_left_forward_fast()
            elif xdir == 'forward' and ydir == 'right':
                driving = True
                print('sending strafe forward right')
                udp.strafe_right_forward_fast()
            elif xdir == 'backward' and ydir == 'left':
                driving = True
                print('sending strafe backward left')
                udp.strafe_left_backward_fast()
            elif xdir == 'backward' and ydir == 'right':
                driving = True
                print('sending strafe backward right')
                udp.strafe_right_backward_fast()
            elif xdir == 'forward':
                driving = True
                print('sending forward')
                udp.fast_forward()
            elif xdir == 'backward':
                driving = True
                print('sending backward')
                udp.fast_backward()
            elif ydir == 'left':
                driving = True
                print('sending left')
                udp.turn_left_fast()
            elif ydir == 'right':
                driving = True
                print('sending right')
                udp.turn_right_fast()
            elif xdir == '' or ydir == '':
                if driving:
                    driving = False
                    # udp.full_stop()


jl()
