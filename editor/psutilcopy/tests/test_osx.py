#!/usr/bin/env python

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""OSX specific tests."""

import os
import re
import time

import psutilcopy
from psutilcopy import OSX
from psutilcopy.tests import create_zombie_proc
from psutilcopy.tests import get_test_subprocess
from psutilcopy.tests import HAS_BATTERY
from psutilcopy.tests import MEMORY_TOLERANCE
from psutilcopy.tests import reap_children
from psutilcopy.tests import retry_before_failing
from psutilcopy.tests import run_test_module_by_name
from psutilcopy.tests import sh
from psutilcopy.tests import unittest


PAGESIZE = os.sysconf("SC_PAGE_SIZE") if OSX else None


def sysctl(cmdline):
    """Expects a sysctl command with an argument and parse the result
    returning only the value of interest.
    """
    out = sh(cmdline)
    result = out.split()[1]
    try:
        return int(result)
    except ValueError:
        return result


def vm_stat(field):
    """Wrapper around 'vm_stat' cmdline utility."""
    out = sh('vm_stat')
    for line in out.split('\n'):
        if field in line:
            break
    else:
        raise ValueError("line not found")
    return int(re.search(r'\d+', line).group(0)) * PAGESIZE


# http://code.activestate.com/recipes/578019/
def human2bytes(s):
    SYMBOLS = {
        'customary': ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
    }
    init = s
    num = ""
    while s and s[0:1].isdigit() or s[0:1] == '.':
        num += s[0]
        s = s[1:]
    num = float(num)
    letter = s.strip()
    for name, sset in SYMBOLS.items():
        if letter in sset:
            break
    else:
        if letter == 'k':
            sset = SYMBOLS['customary']
            letter = letter.upper()
        else:
            raise ValueError("can't interpret %r" % init)
    prefix = {sset[0]: 1}
    for i, s in enumerate(sset[1:]):
        prefix[s] = 1 << (i + 1) * 10
    return int(num * prefix[letter])


@unittest.skipIf(not OSX, "OSX only")
class TestProcess(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pid = get_test_subprocess().pid

    @classmethod
    def tearDownClass(cls):
        reap_children()

    def test_process_create_time(self):
        output = sh("ps -o lstart -p %s" % self.pid)
        start_ps = output.replace('STARTED', '').strip()
        hhmmss = start_ps.split(' ')[-2]
        year = start_ps.split(' ')[-1]
        start_psutil = psutilcopy.Process(self.pid).create_time()
        self.assertEqual(
            hhmmss,
            time.strftime("%H:%M:%S", time.localtime(start_psutil)))
        self.assertEqual(
            year,
            time.strftime("%Y", time.localtime(start_psutil)))


@unittest.skipIf(not OSX, "OSX only")
class TestZombieProcessAPIs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        zpid = create_zombie_proc()
        cls.p = psutilcopy.Process(zpid)

    @classmethod
    def tearDownClass(cls):
        reap_children(recursive=True)

    def test_pidtask_info(self):
        self.assertEqual(self.p.status(), psutilcopy.STATUS_ZOMBIE)
        self.p.ppid()
        self.p.uids()
        self.p.gids()
        self.p.terminal()
        self.p.create_time()

    def test_exe(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.exe)

    def test_cmdline(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.cmdline)

    def test_environ(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.environ)

    def test_cwd(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.cwd)

    def test_memory_full_info(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.memory_full_info)

    def test_cpu_times(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.cpu_times)

    def test_num_ctx_switches(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.num_ctx_switches)

    def test_num_threads(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.num_threads)

    def test_open_files(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.open_files)

    def test_connections(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.connections)

    def test_num_fds(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.num_fds)

    def test_threads(self):
        self.assertRaises((psutilcopy.ZombieProcess, psutilcopy.AccessDenied),
                          self.p.threads)

    def test_memory_maps(self):
        self.assertRaises(psutilcopy.ZombieProcess, self.p.memory_maps)


@unittest.skipIf(not OSX, "OSX only")
class TestSystemAPIs(unittest.TestCase):

    # --- disk

    def test_disks(self):
        # test psutil.disk_usage() and psutil.disk_partitions()
        # against "df -a"
        def df(path):
            out = sh('df -k "%s"' % path).strip()
            lines = out.split('\n')
            lines.pop(0)
            line = lines.pop(0)
            dev, total, used, free = line.split()[:4]
            if dev == 'none':
                dev = ''
            total = int(total) * 1024
            used = int(used) * 1024
            free = int(free) * 1024
            return dev, total, used, free

        for part in psutilcopy.disk_partitions(all=False):
            usage = psutilcopy.disk_usage(part.mountpoint)
            dev, total, used, free = df(part.mountpoint)
            self.assertEqual(part.device, dev)
            self.assertEqual(usage.total, total)
            # 10 MB tollerance
            if abs(usage.free - free) > 10 * 1024 * 1024:
                self.fail("psutil=%s, df=%s" % usage.free, free)
            if abs(usage.used - used) > 10 * 1024 * 1024:
                self.fail("psutil=%s, df=%s" % usage.used, used)

    # --- cpu

    def test_cpu_count_logical(self):
        num = sysctl("sysctl hw.logicalcpu")
        self.assertEqual(num, psutilcopy.cpu_count(logical=True))

    def test_cpu_count_physical(self):
        num = sysctl("sysctl hw.physicalcpu")
        self.assertEqual(num, psutilcopy.cpu_count(logical=False))

    def test_cpu_freq(self):
        freq = psutilcopy.cpu_freq()
        self.assertEqual(
            freq.current * 1000 * 1000, sysctl("sysctl hw.cpufrequency"))
        self.assertEqual(
            freq.min * 1000 * 1000, sysctl("sysctl hw.cpufrequency_min"))
        self.assertEqual(
            freq.max * 1000 * 1000, sysctl("sysctl hw.cpufrequency_max"))

    # --- virtual mem

    def test_vmem_total(self):
        sysctl_hwphymem = sysctl('sysctl hw.memsize')
        self.assertEqual(sysctl_hwphymem, psutilcopy.virtual_memory().total)

    @retry_before_failing()
    def test_vmem_free(self):
        vmstat_val = vm_stat("free")
        psutil_val = psutilcopy.virtual_memory().free
        self.assertAlmostEqual(psutil_val, vmstat_val, delta=MEMORY_TOLERANCE)

    @retry_before_failing()
    def test_vmem_available(self):
        vmstat_val = vm_stat("inactive") + vm_stat("free")
        psutil_val = psutilcopy.virtual_memory().available
        self.assertAlmostEqual(psutil_val, vmstat_val, delta=MEMORY_TOLERANCE)

    @retry_before_failing()
    def test_vmem_active(self):
        vmstat_val = vm_stat("active")
        psutil_val = psutilcopy.virtual_memory().active
        self.assertAlmostEqual(psutil_val, vmstat_val, delta=MEMORY_TOLERANCE)

    @retry_before_failing()
    def test_vmem_inactive(self):
        vmstat_val = vm_stat("inactive")
        psutil_val = psutilcopy.virtual_memory().inactive
        self.assertAlmostEqual(psutil_val, vmstat_val, delta=MEMORY_TOLERANCE)

    @retry_before_failing()
    def test_vmem_wired(self):
        vmstat_val = vm_stat("wired")
        psutil_val = psutilcopy.virtual_memory().wired
        self.assertAlmostEqual(psutil_val, vmstat_val, delta=MEMORY_TOLERANCE)

    # --- swap mem

    @retry_before_failing()
    def test_swapmem_sin(self):
        vmstat_val = vm_stat("Pageins")
        psutil_val = psutilcopy.swap_memory().sin
        self.assertEqual(psutil_val, vmstat_val)

    @retry_before_failing()
    def test_swapmem_sout(self):
        vmstat_val = vm_stat("Pageout")
        psutil_val = psutilcopy.swap_memory().sout
        self.assertEqual(psutil_val, vmstat_val)

    # Not very reliable.
    # def test_swapmem_total(self):
    #     out = sh('sysctl vm.swapusage')
    #     out = out.replace('vm.swapusage: ', '')
    #     total, used, free = re.findall('\d+.\d+\w', out)
    #     psutil_smem = psutil.swap_memory()
    #     self.assertEqual(psutil_smem.total, human2bytes(total))
    #     self.assertEqual(psutil_smem.used, human2bytes(used))
    #     self.assertEqual(psutil_smem.free, human2bytes(free))

    # --- network

    def test_net_if_stats(self):
        for name, stats in psutilcopy.net_if_stats().items():
            try:
                out = sh("ifconfig %s" % name)
            except RuntimeError:
                pass
            else:
                self.assertEqual(stats.isup, 'RUNNING' in out, msg=out)
                self.assertEqual(stats.mtu,
                                 int(re.findall(r'mtu (\d+)', out)[0]))

    # --- sensors_battery

    @unittest.skipIf(not HAS_BATTERY, "no battery")
    def test_sensors_battery(self):
        out = sh("pmset -g batt")
        percent = re.search("(\d+)%", out).group(1)
        drawing_from = re.search("Now drawing from '([^']+)'", out).group(1)
        power_plugged = drawing_from == "AC Power"
        psutil_result = psutilcopy.sensors_battery()
        self.assertEqual(psutil_result.power_plugged, power_plugged)
        self.assertEqual(psutil_result.percent, int(percent))


if __name__ == '__main__':
    run_test_module_by_name(__file__)
