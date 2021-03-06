# coding=utf-8
import gc


def collect():
    gc.collect()


def mem_free():
    from prometheus import is_micro as _is_micro
    if _is_micro:
        return gc.mem_free()
    else:
        return None
