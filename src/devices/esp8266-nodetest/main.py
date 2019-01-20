import nodetest
import machine
import prometheus.server.socketserver.jsonrest
import prometheus.logging as logging
import gc

gc.collect()
node = nodetest.NodeTest()
gc.collect()
jsonrestserver = prometheus.server.socketserver.jsonrest.JsonRestServer(node, settimeout=0.1)
gc.collect()
logging.debug('mem_free after adding json: %d' % gc.mem_free())
logging.boot(jsonrestserver)
gc.collect()
logging.debug('mem_free before start: %d' % gc.mem_free())

try:
    jsonrestserver.start()
except Exception as exception:
    print(exception)
    gc.collect()

try:
    logging.error('crashed? rst')
except Exception:
    gc.collect()

machine.reset()
