import test01
import prometheus.server.socketserver.udp
import prometheus.server.multiserver
import prometheus.tftpd
import prometheus.logging as logging
import prometheus.pgc as gc
import machine
import utime
import socket
import rover01client
import tankclient
from misc import StateMachine, Menu, Calibrate, switch_calibration

gc.collect()

node = test01.Test01()
multiserver = prometheus.server.multiserver.MultiServer()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())

udpserver = prometheus.server.socketserver.udp.UdpSocketServer(node)
logging.boot(udpserver)


def td():
    prometheus.tftpd.tftpd()


def get_choices():
    lst = list()
    if node.switch1.value():
        lst.append(1)
    if node.switch2.value():
        lst.append(2)
    if node.switch3.value():
        lst.append(3)
    return lst


class MenuSystem(object):
    def __init__(self, instance):
        self.node = instance
        self.menu_tree = Menu(StateMachine.S_MENU_MAIN, 'Main menu', [
            Menu(StateMachine.S_MENU_CONFIGURATION, 'Configuration', [
                Menu(StateMachine.S_MENU_CONFIGURATION_ROVER, 'Rover', [
                    Menu(StateMachine.S_MENU_CONNECT, 'Connect', [
                        Menu(StateMachine.S_MENU_CONFIGURATION_ROVER, 'Back', [])
                    ]),
                    Menu(StateMachine.S_MENU_MAIN, 'Back', [])
                ]),
                Menu(StateMachine.S_MENU_CONFIGURATION_TANK, 'Tank', [
                    Menu(StateMachine.S_MENU_CONNECT, 'Connect', [
                        Menu(StateMachine.S_MENU_CONFIGURATION_TANK, 'Back', [])
                    ]),
                    Menu(StateMachine.S_MENU_MAIN, 'Back', [])
                ]),
                Menu(StateMachine.S_MENU_MAIN, 'Back', [])
            ]),
            Menu(StateMachine.S_MENU_CALIBRATION, 'Calibration', [
                # Menu(StateMachine.S_MENU_CONNECT, 'Connect', []),
                Menu(StateMachine.S_MENU_MAIN, 'Back', [])
            ]),
            Menu(StateMachine.S_MENU_CONNECT, 'Connect', [
                # Menu(StateMachine.S_DRIVE, 'Drive', []),
                Menu(StateMachine.S_MENU_MAIN, 'Back', [])
            ]),
            Menu(StateMachine.S_DRIVE, 'Drive', [
                Menu(StateMachine.S_MENU_MAIN, 'Back', [])
            ])])
        self.state_machine = StateMachine()
        self.current_menu = self.menu_tree
        self.selected_menu_item = 0
        self.previous_buttons_down = list()
        self.previously_selected_menu_item = -1
        self.timer = utime.time()
        self.frame = 0
        self.force_refresh = True
        self.previous_joystickx_value = 0
        self.previous_joysticky_value = 0
        self.calibration = Calibrate(self.node)
        self.udp = None
        # for driving state:
        self.joystick_button_held = 0
        self.touch = machine.TouchPad(machine.Pin(4))
        self.driving = False
        self.touch_active = 0
        self.state_drive_timer = utime.ticks_ms()

    def update_menu(self):
        node.ssd.fill(False)
        node.ssd.text('RC 0.1 %d %d' % (utime.time(), self.frame), 0, 0)
        node.ssd.text('-- %s --' % self.current_menu.name, 0, 8)
        height = 16
        index = 0
        for option in self.current_menu.options:
            node.ssd.text(('*' if self.selected_menu_item == index else ' ') + ' ' + option.name, 0, height)
            height += 8
            index += 1

    def run(self):
        while True:
            gc.collect()
            machine.idle()
            self.frame += 1

            node.integrated_led.off()
            buttons_down = get_choices()
            if 1 in buttons_down and 1 not in self.previous_buttons_down:
                # pressed up
                print('choice from %d and to %d' % (self.selected_menu_item, self.selected_menu_item - 1))
                self.selected_menu_item -= 1
            elif 2 in buttons_down and 2 not in self.previous_buttons_down:
                # pressed down
                print('choice from %d and to %d' % (self.selected_menu_item, self.selected_menu_item + 1))
                self.selected_menu_item += 1
            elif 3 in buttons_down and 3 not in self.previous_buttons_down:
                # pressed select
                print('selected %d' % self.selected_menu_item)
                if self.selected_menu_item > len(self.current_menu.options):
                    print('ignoring out of bounds')
                    continue

                selected_menu = self.current_menu.options[self.selected_menu_item]
                self.state_machine.transition(selected_menu.state_to)
                # in order to get the closest option to root
                self.current_menu = Menu.get_menu(self.menu_tree, self.state_machine.state)
                self.force_refresh = True
                self.selected_menu_item = 0

            selected_changed = self.selected_menu_item != self.previously_selected_menu_item
            max_item = len(self.current_menu.options) - 1
            # clamping
            if self.selected_menu_item < 0:
                self.selected_menu_item = max_item
            elif self.selected_menu_item > max_item:
                self.selected_menu_item = 0
            # switch choice state and update screen
            self.previously_selected_menu_item = self.selected_menu_item
            self.previous_buttons_down = buttons_down

            if self.state_machine.state == StateMachine.S_IDLE:
                # for now, just switch to main menu
                self.state_machine.transition(StateMachine.S_MENU_MAIN)
                self.current_menu = Menu.get_menu(self.menu_tree, self.state_machine.state)
                # to trigger menu update
                self.force_refresh = True
            elif self.state_machine.state == StateMachine.S_MENU_MAIN:
                # update when choice has been changed or a second (or more) has passed
                if not self.force_refresh and not selected_changed or self.timer - utime.time() == 0:
                    continue

                self.update_menu()
                node.ssd.show()
                self.frame = 0
                self.force_refresh = False
            elif self.state_machine.state == StateMachine.S_MENU_CONFIGURATION:
                # update when choice has been changed or a second (or more) has passed
                if not self.force_refresh and not selected_changed or self.timer - utime.time() == 0:
                    continue

                self.update_menu()
                node.ssd.show()
                self.frame = 0
                self.force_refresh = False
            elif self.state_machine.state == StateMachine.S_MENU_CONFIGURATION_ROVER:
                ip = '10.20.2.144'
                self.udp = rover01client.Rover01UdpClient(ip, bind_port=5000 + (int(utime.time()) & 0xff))
                self.state_machine.transition(StateMachine.S_MENU_CONFIGURATION)
            elif self.state_machine.state == StateMachine.S_MENU_CONFIGURATION_TANK:
                host = 'tank.iot.oh.wsh.no'
                ip = socket.getaddrinfo(host, 9195)
                if ip is []:
                    print('could not resolve rover01')
                    return
                ip = ip[-1][-1][0]
                self.udp = tankclient.TankUdpClient(ip, bind_port=6000 + (int(utime.time()) & 0xff))
                self.state_machine.transition(StateMachine.S_MENU_CONFIGURATION)
            elif self.state_machine.state == StateMachine.S_MENU_CALIBRATION:
                joystickx_value = node.joystickx.read()
                joysticky_value = node.joysticky.read()
                # update when choice has been changed or a second (or more) has passed
                if joysticky_value is self.previous_joystickx_value and \
                        joysticky_value is self.previous_joysticky_value and \
                        not self.force_refresh and \
                        not selected_changed or self.timer - utime.time() == 0:
                    continue

                self.update_menu()
                xvalue, yvalue = self.calibration.calibrate(joystickx_value, joysticky_value)

                if self.calibration.calibrated:
                    # blink led
                    self.node.integrated_led.pin.value(self.node.integrated_led.value() ^ 1)

                self.node.ssd.text('~~~~~~~~ Done!' if self.calibration.calibrated else '~~~~~~~~', 0, 32)
                self.node.ssd.text('x: %d y: %d' % (xvalue, yvalue), 0, 36)
                self.node.ssd.text('h x:%d y:%d' % (self.calibration.highest_joystickx_value,
                                                    self.calibration.highest_joysticky_value), 0, 44)
                self.node.ssd.text('l x:%d y:%d' % (self.calibration.lowest_joystickx_value,
                                                    self.calibration.lowest_joysticky_value), 0, 52)

                self.previous_joystickx_value = joystickx_value
                self.previous_joysticky_value = joysticky_value
                node.ssd.show()
                self.frame = 0
                self.force_refresh = False
            elif self.state_machine.state == StateMachine.S_MENU_CONNECT:
                # update when choice has been changed or a second (or more) has passed
                if not self.force_refresh and not selected_changed or self.timer - utime.time() == 0:
                    continue

                self.update_menu()
                version = self.udp.version()
                node.ssd.text('%s' % version, 0, 24)
                node.ssd.show()
                self.frame = 0
                self.force_refresh = False
            elif self.state_machine.state == StateMachine.S_DRIVE:
                self.state_drive()

    def state_drive(self):
        x = node.joystickx.read()
        y = node.joysticky.read()
        # sw = node.joystickswitch.value()
        sw = node.switch1.value()
        # print('x=%d y=%d sw=%d' % (x, y, sw))
        r = self.touch.read()

        if x < self.calibration.lowest_joystickx_value:  # x_calibration_forward:
            xdir = 'forward'
        elif x > self.calibration.highest_joystickx_value:  # x_calibration_backward:
            xdir = 'backward'
        else:
            xdir = ''

        if y > self.calibration.highest_joysticky_value:  # y_calibration_left:
            ydir = 'left'
        elif y < self.calibration.lowest_joysticky_value:  # y_calibration_right:
            ydir = 'right'
        else:
            ydir = ''

        # if xdir != '' or ydir != '':
        if self.previous_joystickx_value != xdir or self.previous_joysticky_value != ydir:
            print('%s %s (%d, %d)' % (xdir, ydir, x, y))
            self.previous_joystickx_value = xdir
            self.previous_joysticky_value = ydir

        # sw = joystickread()
        if sw == 0:
            # button down
            self.joystick_button_held += 1
        elif self.joystick_button_held != 0:
            # button up
            print('button up - sc=%d' % self.joystick_button_held)
            self.joystick_button_held = 0

        if self.joystick_button_held > switch_calibration:
            # button held
            # print('click - sc=%d' % sc)
            pass

        if r == 0:
            if self.touch_active == 0:
                # touch active
                print('touch active')
            self.touch_active += 1
        elif self.touch_active != 0:
            # touch inactive
            print('touch inactive - rc=%d' % self.touch_active)
            self.touch_active = 0

        current_time = utime.ticks_ms()
        if current_time - self.state_drive_timer >= 200:
            self.state_drive_timer = current_time
            if xdir == 'forward' and ydir == 'left':
                self.driving = True
                print('sending strafe forward left')
                self.udp.strafe_left_forward_fast()
            elif xdir == 'forward' and ydir == 'right':
                self.driving = True
                print('sending strafe forward right')
                self.udp.strafe_right_forward_fast()
            elif xdir == 'backward' and ydir == 'left':
                self.driving = True
                print('sending strafe backward left')
                self.udp.strafe_left_backward_fast()
            elif xdir == 'backward' and ydir == 'right':
                self.driving = True
                print('sending strafe backward right')
                self.udp.strafe_right_backward_fast()
            elif xdir == 'forward':
                self.driving = True
                print('sending forward')
                self.udp.fast_forward()
            elif xdir == 'backward':
                self.driving = True
                print('sending backward')
                self.udp.fast_backward()
            elif ydir == 'left':
                self.driving = True
                print('sending left')
                self.udp.turn_left_fast()
            elif ydir == 'right':
                self.driving = True
                print('sending right')
                self.udp.turn_right_fast()
            elif xdir == '' or ydir == '':
                if self.driving:
                    self.driving = False
                    # udp.full_stop()


menu_system = MenuSystem(node)
menu_system.run()
