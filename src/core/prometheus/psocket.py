# coding=utf-8
import gc
import socket
import prometheus

gc.collect()

if prometheus.is_micro:
    socket_error = Exception
else:
    socket_error = socket.error
# 11 EAGAIN (try again later)
# 110 Connection timed out
# 23 cant read data?
# 10035 WSAEWOULDBLOCK (A non-blocking socket operation could not be completed immediately)
