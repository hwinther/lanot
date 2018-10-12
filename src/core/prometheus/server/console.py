# coding=utf-8
import prometheus
import prometheus.server
import prometheus.logging as logging
import prometheus.pollcompat
import sys
import gc

gc.collect()


# TODO: implement support for windows with msvcrt - https://stackoverflow.com/questions/3471461/raw-input-and-timeout

class Console(prometheus.server.Server):
    def __init__(self, instance):
        prometheus.server.Server.__init__(self, instance)

        self.poll_compat = prometheus.pollcompat.PollCompat()

    def pre_loop(self, **kwargs):
        prometheus.server.Server.pre_loop(self, **kwargs)

        self.poll_compat.register(sys.stdin, prometheus.pollcompat.PollCompat.POLLIN)
        logging.success('console active')

    def loop_tick(self, **kwargs):
        prometheus.server.Server.loop_tick(self, **kwargs)

        for pair in self.poll_compat.poll(0):
            if prometheus.pollcompat.PollCompat.POLLIN & pair[1]:
                command = sys.stdin.readline()
                if command[-1] == '\n':
                    command = command[:-1]
                self.handle_data(command, None)

    def reply(self, return_value, source=None, context=None, **kwargs):
        prometheus.server.Server.reply(self, return_value, **kwargs)

        logging.info(return_value)
