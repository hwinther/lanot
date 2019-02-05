import nodetest
import machine
import prometheus.server.multiserver
import prometheus.server.socketserver.jsonrest
import prometheus.server.localevents
import prometheus.logging as logging
import gc

gc.collect()
node = nodetest.NodeTest()
gc.collect()

multiserver = prometheus.server.multiserver.MultiServer()
gc.collect()
logging.debug('mem_free: %s' % gc.mem_free())

jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, settimeout=0.1)
multiserver.add(jsonrestserver)
gc.collect()
logging.debug('mem_free after adding json: %d' % gc.mem_free())

localevents = prometheus.server.localevents.LocalEvents(node)
multiserver.add(localevents)

logging.boot(jsonrestserver)
gc.collect()
logging.debug('mem_free before start: %d' % gc.mem_free())

try:
    multiserver.start()
except Exception as exception:
    print(exception)
    gc.collect()

try:
    logging.error('crashed? rst')
except Exception:
    gc.collect()

machine.reset()
