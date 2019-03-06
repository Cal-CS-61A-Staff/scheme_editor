import os

import sys
sys.path.insert(0, "editor")

import psutilcopy as psutil

process = psutil.Process(os.getpid())
print(process.memory_info().rss)  # in bytes
