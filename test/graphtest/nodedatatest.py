# coding=utf-8
import random
import time
import deploy.clients.sensor01client as sensor01client
import deploy.clients.sensor02client as sensor02client
import deploy.clients.nodetestclient as nodetestclient
import prometheus.nodedata


def log_dht(value, name):
    nodedatas = list()
    if value is None:
        return nodedatas
    values = value.split('c')

    if len(values) != 2:
        return nodedatas

    nodedatas.append(prometheus.nodedata.NodeData(name, b'dht_temp', b'%s' % values[0]))
    nodedatas.append(prometheus.nodedata.NodeData(name, b'dht_hum', b'%s' % values[1]))
    return nodedatas


def log_dht_retry(method, name):
    count = 0
    result = list()
    while True:
        if count == 5:
            break
        value = method()
        print('%s.dht11 value=%s' % (name.encode('utf-8'), value))
        result = log_dht(value, name)
        # print('result count: %d' % len(result))
        if len(result) == 2:
            break
        count += 1
        time.sleep(0.5)
    return result


def main():
    port1 = random.randrange(1024, 9000)
    port2 = random.randrange(1024, 9000)
    sensor01 = sensor01client.Sensor01UdpClient('sensor01', bind_port=port1)
    sensor02 = sensor02client.Sensor02UdpClient('sensor02', bind_port=port2)

    while True:
        # nodetest = nodetestclient.NodeTestTcpClient('10.20.2.117')
        nodedatas = list()

        result = log_dht_retry(sensor01.dht11.value, 'sensor01')
        nodedatas.extend(result)

        result = log_dht_retry(sensor02.dht11.value, 'sensor02')
        nodedatas.extend(result)

        prometheus.nodedata.client('10.20.1.19', 9085, *nodedatas)

        time.sleep(60*5)


if __name__ == '__main__':
    main()
