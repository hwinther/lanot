import gc as _gc


def collect():
    _gc.collect()


def mem_free():
    from prometheus import is_micro as _is_micro
    if _is_micro:
        return _gc.mem_free()
    else:
        return None
