import gc

gc.collect()


class WrappedServer(object):
    def __init__(self, server, kwargs):
        self.server = server
        self.kwargs = kwargs


class MultiServer(object):
    def __init__(self):
        self.wrapped_servers = list()

    def add(self, server, **kwargs):
        self.wrapped_servers.append(WrappedServer(server, kwargs))

    def start(self):
        for wrapped_server in self.wrapped_servers:
            wrapped_server.server.pre_loop(**wrapped_server.kwargs)
            wrapped_server.server.loopActive = True

        loop_active = True
        while loop_active:
            for wrapped_server in self.wrapped_servers:
                wrapped_server.server.loop_tick(**wrapped_server.kwargs)
                if not wrapped_server.server.loopActive:
                    loop_active = False
                    break

        for wrapped_server in self.wrapped_servers:
            wrapped_server.server.post_loop(**wrapped_server.kwargs)
