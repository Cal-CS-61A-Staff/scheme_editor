#!/usr/bin/env python

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Sun OS specific tests."""

import os

import psutilcopy
from psutilcopy import SUNOS
from psutilcopy.tests import run_test_module_by_name
from psutilcopy.tests import sh
from psutilcopy.tests import unittest


@unittest.skipIf(not SUNOS, "SUNOS only")
class SunOSSpecificTestCase(unittest.TestCase):

    def test_swap_memory(self):
        out = sh('env PATH=/usr/sbin:/sbin:%s swap -l' % os.environ['PATH'])
        lines = out.strip().split('\n')[1:]
        if not lines:
            raise ValueError('no swap device(s) configured')
        total = free = 0
        for line in lines:
            line = line.split()
            t, f = line[-2:]
            total += int(int(t) * 512)
            free += int(int(f) * 512)
        used = total - free

        psutil_swap = psutilcopy.swap_memory()
        self.assertEqual(psutil_swap.total, total)
        self.assertEqual(psutil_swap.used, used)
        self.assertEqual(psutil_swap.free, free)

    def test_cpu_count(self):
        out = sh("/usr/sbin/psrinfo")
        self.assertEqual(psutilcopy.cpu_count(), len(out.split('\n')))


if __name__ == '__main__':
    run_test_module_by_name(__file__)
