import sys
import time


class TimeLimitException(Exception): pass


def limiter(lim, func, *args):
    start = time.time()

    def tracer(*args):
        if time.time() > start + lim:
            raise TimeLimitException()
        return tracer

    sys_tracer = sys.gettrace()
    try:
        sys.settrace(tracer)
        func(*args)
    finally:
        sys.settrace(sys_tracer)