import gc
import os

import sys

from scheme_exceptions import OutOfMemoryError

sys.path.insert(0, "editor")

# import libraries.psutilcopy as psutil
import psutil

THRESHOLD = 100 * 10**6


min_memory = 0


def get_memory():
    global min_memory
    process = psutil.Process(os.getpid())
    out = process.memory_info().rss
    min_memory = min(min_memory, out)
    return out


def reset():
    global min_memory
    min_memory = get_memory()


def assert_low_memory(collected=False):
    if get_memory() > min_memory + THRESHOLD:
        if not collected:
            gc.collect()
            assert_low_memory(True)
        else:
            raise OutOfMemoryError("Out of memory, terminating program!")
