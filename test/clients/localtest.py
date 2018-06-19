from deploy.clients import localtestclient
from deploy.clients import nodetestclient
from deploy.clients import sensor01client
from deploy.clients import sensor02client
from deploy.clients import test02client
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


udp = localtestclient.LocalTestUdpClient('localhost', bind_port=9190)
# tcp = localtestclient.LocalTestTcpClient('localhost', bind_port=9190)
nu = nodetestclient.NodeTestUdpClient('nodetest', bind_port=9191)
s1u = sensor01client.Sensor01UdpClient('sensor01', bind_port=9192)
s2u = sensor02client.Sensor02UdpClient('sensor02', bind_port=9193)
t2u = test02client.Test02UdpClient('test02', bind_port=9194)

print('udp: %s' % udp.version())
print('nu: %s' % nu.version())
# print('tcp: %s' % tcp.version())

st = StressTester(udp.blue_led.value)
su = StressTester(nu.integrated_led.value)
s1u = StressTester(s1u.integrated_led.value)
s2u = StressTester(s2u.integrated_led.value)
t2u = StressTester(t2u.integrated_led.value)

# print(st.run_once())
# st.run_multiple(4)

print('\n==LocalTest==')
st.run_multiple(10)

print('\n==NodeTest==')
su.run_multiple(10)

print('\n==Sensor01==')
s1u.run_multiple(10)

print('\n==Sensor02==')
s2u.run_multiple(10)

print('\n==Test02==')
t2u.run_multiple(10)
