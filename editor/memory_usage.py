import os

import sys
sys.path.insert(0, "editor")

import psutilcopy as psutil


def assert_low_memory():
    process = psutil.Process(os.getpid())
    print(process.memory_info().rss)  # in bytes
