import test01
import prometheus_servers
import prometheus_tftpd
import prometheus_logging as logging
import gc
import machine


gc.collect()


def td():
    prometheus_tftpd.tftpd()


node = test01.Test01()
# multiserver = prometheus_servers.MultiServer()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())

udpserver = prometheus_servers.UdpSocketServer(node)
# multiserver.add(udpserver, bind_host='', bind_port=9190)
# gc.collect()
#
# tcpserver = prometheus_servers.TcpSocketServer(node)
# multiserver.add(tcpserver, bind_host='', bind_port=9191)
# gc.collect()
#
# jsonrestserver = prometheus_servers.JsonRestServer(node,
#                                                    loop_tick_delay=0.1)
# multiserver.add(jsonrestserver, bind_host='', bind_port=8080)
# gc.collect()
#
# jsonrestsslserver = prometheus_servers.JsonRestServer(node,
#                                                       loop_tick_delay=0.1,  # for cpython, limits cpu cycles
#                                                       socketwrapper=prometheus_servers_ssl.SslSocket)
# multiserver.add(jsonrestsslserver, bind_host='', bind_port=4443)
# gc.collect()

logging.boot(udpserver)
# multiserver.start()

x_calibration_forward = 1800
x_calibration_backward = 1910
y_calibration_left = 2070
y_calibration_right = 1960
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

        if xdir != '' or ydir != '':
            if old_xdir != xdir or old_ydir != ydir:
                print('%s %s' % (xdir, ydir))
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
