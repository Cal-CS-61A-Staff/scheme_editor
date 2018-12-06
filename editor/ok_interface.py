import os
import sys

newdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/ok"
sys.path.append(newdir)

# noinspection PyUnresolvedReferences
import client

