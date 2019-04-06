import sys
import threading
import time


class OperationCanceledException(Exception): pass
class TimeLimitException(Exception): pass


def limiter(lim, func, *args):
    is_event = isinstance(lim, threading.Event)
    lim_is_set = lim.is_set if is_event else None  # For performance
    gettime = time.time  # For performance
    end = (gettime() + lim) if not is_event else None
    def tracer(*args):
        if lim_is_set() if is_event else gettime() > end:
            raise OperationCanceledException() if is_event else TimeLimitException()
        return tracer

    sys_tracer = sys.gettrace()
    try:
        sys.settrace(tracer)
        func(*args)
    finally:
        sys.settrace(sys_tracer)