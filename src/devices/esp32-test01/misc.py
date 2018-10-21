# coding=utf-8
import prometheus.logging as logging
import uos
import gc
import utime

gc.collect()


# x_calibration_forward = 1800
# x_calibration_backward = 1940
# y_calibration_left = 2100
# y_calibration_right = 1940
switch_calibration = 50


class Calibrate(object):
    def __init__(self, instance):
        self.node = instance
        self.highest_joystickx_value = 0
        self.lowest_joystickx_value = 3000
        self.highest_joysticky_value = 0
        self.lowest_joysticky_value = 3000
        self.calibrated = False
        self.last_change = utime.time()
        self.load_calibration()

    def save_calibration(self):
        open('calibration.cfg', 'w').write(b'%d\t%d\t%d\t%d' % (self.lowest_joystickx_value,
                                                                self.highest_joystickx_value,
                                                                self.lowest_joysticky_value,
                                                                self.highest_joysticky_value))
        logging.notice('calibration saved')

    def load_calibration(self):
        if 'calibration.cfg' not in uos.listdir('.'):
            return
        data = open('calibration.cfg', 'r').read()
        values = data.split('\t')
        if len(values) is not 4:
            return
        self.lowest_joystickx_value = int(values[0])
        self.highest_joystickx_value = int(values[1])
        self.lowest_joysticky_value = int(values[2])
        self.highest_joysticky_value = int(values[3])
        logging.notice('calibration loaded')

    def calibrate(self, xvalue, yvalue):
        if xvalue > self.highest_joystickx_value:
            self.highest_joystickx_value = xvalue
            self.last_change = utime.time()
        elif xvalue < self.lowest_joystickx_value:
            self.lowest_joystickx_value = xvalue
            self.last_change = utime.time()

        if yvalue > self.highest_joysticky_value:
            self.highest_joysticky_value = yvalue
            self.last_change = utime.time()
        elif yvalue < self.lowest_joysticky_value:
            self.lowest_joysticky_value = yvalue
            self.last_change = utime.time()

        if not self.calibrated and utime.time() - self.last_change > 30:
            self.calibrated = True
            self.save_calibration()

        return xvalue, yvalue


class StateMachine(object):
    S_IDLE = 0
    S_MENU_MAIN = 1
    S_MENU_CONFIGURATION = 2
    S_MENU_CONFIGURATION_ROVER = 21
    S_MENU_CONFIGURATION_TANK = 22
    S_MENU_CALIBRATION = 3
    S_MENU_CONNECT = 4
    S_DRIVE = 5

    def __init__(self):
        self.state = StateMachine.S_IDLE

    def _set_state(self, state_to):
        self.state = state_to

    @staticmethod
    def get_state_name(state):
        # TODO: make this generic, get the states via constructor or alternatively inheritance
        if state == StateMachine.S_IDLE:
            return 'idle'
        elif state == StateMachine.S_MENU_MAIN:
            return 'menu main'
        elif state == StateMachine.S_MENU_CONFIGURATION:
            return 'menu configuration'
        elif state == StateMachine.S_MENU_CONFIGURATION_ROVER:
            return 'menu configuration rover'
        elif state == StateMachine.S_MENU_CONFIGURATION_TANK:
            return 'menu configuration tank'
        elif state == StateMachine.S_MENU_CALIBRATION:
            return 'menu calibration'
        elif state == StateMachine.S_MENU_CONNECT:
            return 'menu connect'
        elif state == StateMachine.S_DRIVE:
            return 'drive'

    def transition(self, state_to):
        logging.notice('transition from state %s and to %s' % (self.get_state_name(self.state),
                                                               self.get_state_name(state_to)))
        self._set_state(state_to)


class Menu(object):
    def __init__(self, state_to, name, options, row_height=5):
        self.state_to = state_to
        self.name = name
        self.options = options

    @staticmethod
    def get_menu(menu_root, state):
        # print('comparing %d to %d' % (menu_root.state_to, state))
        if menu_root.state_to == state:
            return menu_root
        for menu_option in menu_root.options:
            menu = Menu.get_menu(menu_option, state)
            if menu is not None:
                return menu
        return None

    def __str__(self):
        return 'Menu: %s' % self.name
