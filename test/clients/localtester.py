from deploy.clients import localtestclient
from localtest import LocalTest
# from deploy.clients import nodetestclient
# from deploy.clients import sensor01client
# from deploy.clients import sensor02client
# from deploy.clients import test02client
# from deploy.clients import proxytest2client
import prometheus.logging as logging
import time


class StressTester(object):
    def __init__(self, method, *args):
        self.method = method
        self.args = args

    def run_once(self):
        start = time.time()
        result = self.method(*self.args)
        elapsed = time.time() - start
        return result, elapsed

    def run_multiple(self, times=10):
        start = time.time()
        elapsed_times = list()
        for n in range(0, times):
            result, elapsed = self.run_once()
            print('%d] %04f - %s' % (n, elapsed, repr(result)))
            elapsed_times.append(elapsed)
        average = sum(elapsed_times) / float(len(elapsed_times))
        print('Average: %04f Total: %04f' % (average, time.time() - start))


class Tester(object):
    def __init__(self):
        self.test_state = None

    def runtests(self):
        pass


class LocalTester(Tester):
    def __init__(self, testnode, name):
        Tester.__init__(self)
        self.node = testnode
        self.name = name

    def function_test(self, func, description, kwargs=None, expected_return=None):
        if kwargs is None:
            kwargs = dict()
        # TODO: add try
        return_value = func(**kwargs)
        success = return_value == expected_return
        # print('type1=%s type2=%s' % (type(return_value), type(expected_return)))
        if not isinstance(return_value, type(expected_return)):
            success = False
        if success:
            logging.success('%s ->  %s               Success: %s' % (self.name, func.__name__, description))
            if self.test_state is None:
                self.test_state = True
        else:
            logging.error('%s   ->  %s               Failed: %s' % (self.name, func.__name__, description))
            logging.error(func.__doc__)
            logging.error('Return value was: %s' % repr(return_value))
            self.test_state = False

    def runtests(self):
        Tester.runtests(self)

        self.function_test(self.node.test1, 'return True', None, True)
        # self.function_test(node.test1, 'Local return True reversed', None, False)
        self.function_test(self.node.test2, 'return False', None, False)
        self.function_test(self.node.test3, 'return None (e)', None, None)
        self.function_test(self.node.test4, 'return None (i)', None, None)

        self.function_test(self.node.test5, 'return 0', None, 0)
        self.function_test(self.node.test6, "return 'test'", None, 'test')
        self.function_test(self.node.test7, "return b'test'", None, b'test')


node = LocalTest()

lt = LocalTester(node, 'Local')
lt.runtests()

udp = localtestclient.LocalTestUdpClient('10.20.1.18', bind_port=9190)
lt = LocalTester(udp, 'UDP')
lt.runtests()

tcp = localtestclient.LocalTestTcpClient('10.20.1.18')
lt = LocalTester(tcp, 'TCP')
lt.runtests()

# udp = localtestclient.LocalTestUdpClient('localhost', bind_port=9190)
# tcp = localtestclient.LocalTestTcpClient('localhost', bind_port=9190)
# nu = nodetestclient.NodeTestUdpClient('nodetest', bind_port=9191)
# s1u = sensor01client.Sensor01UdpClient('sensor01', bind_port=9192)
# s2u = sensor02client.Sensor02UdpClient('sensor02', bind_port=9193)
# t2u = test02client.Test02UdpClient('test02', bind_port=9194)
# ptu = proxytest2client.ProxyTest2UdpClient('serenity.oh.wsh.no', bind_port=9196)
# ptul = localtestclient.LocalTestUdpClient('serenity.oh.wsh.no', bind_port=9197)

"""
print('udp: %s' % udp.version())
print('nu: %s' % nu.version())
# print('tcp: %s' % tcp.version())

st = StressTester(udp.blue_led.value)
su = StressTester(nu.integrated_led.value)
s1u = StressTester(s1u.integrated_led.value)
s2u = StressTester(s2u.integrated_led.value)
t2u = StressTester(t2u.integrated_led.value)
pst = StressTester(ptu.version)
pstl = StressTester(ptul.blue_led.value)

# print(st.run_once())
# st.run_multiple(4)

num = 10

print('\n==LocalTest==')
st.run_multiple(num)

print('\n==NodeTest==')
su.run_multiple(num)
""
print('\n==Sensor01==')
s1u.run_multiple(num)

print('\n==Sensor02==')
s2u.run_multiple(num)

print('\n==Test02==')
t2u.run_multiple(num)
""
# print('\n==Proxytest==')
# pst.run_multiple(num)

print('\n==Serenity localtest==')
pstl.run_multiple(num)
"""