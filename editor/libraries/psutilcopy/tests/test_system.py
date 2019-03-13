#!/usr/bin/env python

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Tests for system APIS."""

import contextlib
import datetime
import errno
import os
import pprint
import shutil
import signal
import socket
import sys
import tempfile
import time

import psutilcopy
from psutilcopy import AIX
from psutilcopy import BSD
from psutilcopy import FREEBSD
from psutilcopy import LINUX
from psutilcopy import NETBSD
from psutilcopy import OPENBSD
from psutilcopy import OSX
from psutilcopy import POSIX
from psutilcopy import SUNOS
from psutilcopy import WINDOWS
from psutilcopy._compat import long
from psutilcopy.tests import APPVEYOR
from psutilcopy.tests import ASCII_FS
from psutilcopy.tests import check_net_address
from psutilcopy.tests import DEVNULL
from psutilcopy.tests import enum
from psutilcopy.tests import get_test_subprocess
from psutilcopy.tests import HAS_BATTERY
from psutilcopy.tests import HAS_CPU_FREQ
from psutilcopy.tests import HAS_SENSORS_BATTERY
from psutilcopy.tests import HAS_SENSORS_FANS
from psutilcopy.tests import HAS_SENSORS_TEMPERATURES
from psutilcopy.tests import mock
from psutilcopy.tests import reap_children
from psutilcopy.tests import retry_before_failing
from psutilcopy.tests import run_test_module_by_name
from psutilcopy.tests import safe_rmpath
from psutilcopy.tests import TESTFN
from psutilcopy.tests import TESTFN_UNICODE
from psutilcopy.tests import TRAVIS
from psutilcopy.tests import unittest


# ===================================================================
# --- System-related API tests
# ===================================================================


class TestSystemAPIs(unittest.TestCase):
    """Tests for system-related APIs."""

    def setUp(self):
        safe_rmpath(TESTFN)

    def tearDown(self):
        reap_children()

    def test_process_iter(self):
        self.assertIn(os.getpid(), [x.pid for x in psutilcopy.process_iter()])
        sproc = get_test_subprocess()
        self.assertIn(sproc.pid, [x.pid for x in psutilcopy.process_iter()])
        p = psutilcopy.Process(sproc.pid)
        p.kill()
        p.wait()
        self.assertNotIn(sproc.pid, [x.pid for x in psutilcopy.process_iter()])

        with mock.patch('psutil.Process',
                        side_effect=psutilcopy.NoSuchProcess(os.getpid())):
            self.assertEqual(list(psutilcopy.process_iter()), [])
        with mock.patch('psutil.Process',
                        side_effect=psutilcopy.AccessDenied(os.getpid())):
            with self.assertRaises(psutilcopy.AccessDenied):
                list(psutilcopy.process_iter())

    def test_prcess_iter_w_params(self):
        for p in psutilcopy.process_iter(attrs=['pid']):
            self.assertEqual(list(p.info.keys()), ['pid'])
        with self.assertRaises(ValueError):
            list(psutilcopy.process_iter(attrs=['foo']))
        with mock.patch("psutil._psplatform.Process.cpu_times",
                        side_effect=psutilcopy.AccessDenied(0, "")) as m:
            for p in psutilcopy.process_iter(attrs=["pid", "cpu_times"]):
                self.assertIsNone(p.info['cpu_times'])
                self.assertGreaterEqual(p.info['pid'], 0)
            assert m.called
        with mock.patch("psutil._psplatform.Process.cpu_times",
                        side_effect=psutilcopy.AccessDenied(0, "")) as m:
            flag = object()
            for p in psutilcopy.process_iter(
                    attrs=["pid", "cpu_times"], ad_value=flag):
                self.assertIs(p.info['cpu_times'], flag)
                self.assertGreaterEqual(p.info['pid'], 0)
            assert m.called

    def test_wait_procs(self):
        def callback(p):
            pids.append(p.pid)

        pids = []
        sproc1 = get_test_subprocess()
        sproc2 = get_test_subprocess()
        sproc3 = get_test_subprocess()
        procs = [psutilcopy.Process(x.pid) for x in (sproc1, sproc2, sproc3)]
        self.assertRaises(ValueError, psutilcopy.wait_procs, procs, timeout=-1)
        self.assertRaises(TypeError, psutilcopy.wait_procs, procs, callback=1)
        t = time.time()
        gone, alive = psutilcopy.wait_procs(procs, timeout=0.01, callback=callback)

        self.assertLess(time.time() - t, 0.5)
        self.assertEqual(gone, [])
        self.assertEqual(len(alive), 3)
        self.assertEqual(pids, [])
        for p in alive:
            self.assertFalse(hasattr(p, 'returncode'))

        @retry_before_failing(30)
        def test(procs, callback):
            gone, alive = psutilcopy.wait_procs(procs, timeout=0.03,
                                                callback=callback)
            self.assertEqual(len(gone), 1)
            self.assertEqual(len(alive), 2)
            return gone, alive

        sproc3.terminate()
        gone, alive = test(procs, callback)
        self.assertIn(sproc3.pid, [x.pid for x in gone])
        if POSIX:
            self.assertEqual(gone.pop().returncode, -signal.SIGTERM)
        else:
            self.assertEqual(gone.pop().returncode, 1)
        self.assertEqual(pids, [sproc3.pid])
        for p in alive:
            self.assertFalse(hasattr(p, 'returncode'))

        @retry_before_failing(30)
        def test(procs, callback):
            gone, alive = psutilcopy.wait_procs(procs, timeout=0.03,
                                                callback=callback)
            self.assertEqual(len(gone), 3)
            self.assertEqual(len(alive), 0)
            return gone, alive

        sproc1.terminate()
        sproc2.terminate()
        gone, alive = test(procs, callback)
        self.assertEqual(set(pids), set([sproc1.pid, sproc2.pid, sproc3.pid]))
        for p in gone:
            self.assertTrue(hasattr(p, 'returncode'))

    def test_wait_procs_no_timeout(self):
        sproc1 = get_test_subprocess()
        sproc2 = get_test_subprocess()
        sproc3 = get_test_subprocess()
        procs = [psutilcopy.Process(x.pid) for x in (sproc1, sproc2, sproc3)]
        for p in procs:
            p.terminate()
        gone, alive = psutilcopy.wait_procs(procs)

    def test_boot_time(self):
        bt = psutilcopy.boot_time()
        self.assertIsInstance(bt, float)
        self.assertGreater(bt, 0)
        self.assertLess(bt, time.time())

    @unittest.skipIf(not POSIX, 'POSIX only')
    def test_PAGESIZE(self):
        # pagesize is used internally to perform different calculations
        # and it's determined by using SC_PAGE_SIZE; make sure
        # getpagesize() returns the same value.
        import resource
        self.assertEqual(os.sysconf("SC_PAGE_SIZE"), resource.getpagesize())

    def test_virtual_memory(self):
        mem = psutilcopy.virtual_memory()
        assert mem.total > 0, mem
        assert mem.available > 0, mem
        assert 0 <= mem.percent <= 100, mem
        assert mem.used > 0, mem
        assert mem.free >= 0, mem
        for name in mem._fields:
            value = getattr(mem, name)
            if name != 'percent':
                self.assertIsInstance(value, (int, long))
            if name != 'total':
                if not value >= 0:
                    self.fail("%r < 0 (%s)" % (name, value))
                if value > mem.total:
                    self.fail("%r > total (total=%s, %s=%s)"
                              % (name, mem.total, name, value))

    def test_swap_memory(self):
        mem = psutilcopy.swap_memory()
        self.assertEqual(
            mem._fields, ('total', 'used', 'free', 'percent', 'sin', 'sout'))

        assert mem.total >= 0, mem
        assert mem.used >= 0, mem
        if mem.total > 0:
            # likely a system with no swap partition
            assert mem.free > 0, mem
        else:
            assert mem.free == 0, mem
        assert 0 <= mem.percent <= 100, mem
        assert mem.sin >= 0, mem
        assert mem.sout >= 0, mem

    def test_pid_exists(self):
        sproc = get_test_subprocess()
        self.assertTrue(psutilcopy.pid_exists(sproc.pid))
        p = psutilcopy.Process(sproc.pid)
        p.kill()
        p.wait()
        self.assertFalse(psutilcopy.pid_exists(sproc.pid))
        self.assertFalse(psutilcopy.pid_exists(-1))
        self.assertEqual(psutilcopy.pid_exists(0), 0 in psutilcopy.pids())

    def test_pid_exists_2(self):
        reap_children()
        pids = psutilcopy.pids()
        for pid in pids:
            try:
                assert psutilcopy.pid_exists(pid)
            except AssertionError:
                # in case the process disappeared in meantime fail only
                # if it is no longer in psutil.pids()
                time.sleep(.1)
                if pid in psutilcopy.pids():
                    self.fail(pid)
        pids = range(max(pids) + 5000, max(pids) + 6000)
        for pid in pids:
            self.assertFalse(psutilcopy.pid_exists(pid), msg=pid)

    def test_pids(self):
        plist = [x.pid for x in psutilcopy.process_iter()]
        pidlist = psutilcopy.pids()
        self.assertEqual(plist.sort(), pidlist.sort())
        # make sure every pid is unique
        self.assertEqual(len(pidlist), len(set(pidlist)))

    def test_test(self):
        # test for psutil.test() function
        stdout = sys.stdout
        sys.stdout = DEVNULL
        try:
            psutilcopy.test()
        finally:
            sys.stdout = stdout

    def test_cpu_count(self):
        logical = psutilcopy.cpu_count()
        self.assertEqual(logical, len(psutilcopy.cpu_times(percpu=True)))
        self.assertGreaterEqual(logical, 1)
        #
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo") as fd:
                cpuinfo_data = fd.read()
            if "physical id" not in cpuinfo_data:
                raise unittest.SkipTest("cpuinfo doesn't include physical id")
        physical = psutilcopy.cpu_count(logical=False)
        if WINDOWS and sys.getwindowsversion()[:2] <= (6, 1):  # <= Vista
            self.assertIsNone(physical)
        else:
            self.assertGreaterEqual(physical, 1)
            self.assertGreaterEqual(logical, physical)

    def test_cpu_count_none(self):
        # https://github.com/giampaolo/psutil/issues/1085
        for val in (-1, 0, None):
            with mock.patch('psutil._psplatform.cpu_count_logical',
                            return_value=val) as m:
                self.assertIsNone(psutilcopy.cpu_count())
                assert m.called
            with mock.patch('psutil._psplatform.cpu_count_physical',
                            return_value=val) as m:
                self.assertIsNone(psutilcopy.cpu_count(logical=False))
                assert m.called

    def test_cpu_times(self):
        # Check type, value >= 0, str().
        total = 0
        times = psutilcopy.cpu_times()
        sum(times)
        for cp_time in times:
            self.assertIsInstance(cp_time, float)
            self.assertGreaterEqual(cp_time, 0.0)
            total += cp_time
        self.assertEqual(total, sum(times))
        str(times)
        # CPU times are always supposed to increase over time
        # or at least remain the same and that's because time
        # cannot go backwards.
        # Surprisingly sometimes this might not be the case (at
        # least on Windows and Linux), see:
        # https://github.com/giampaolo/psutil/issues/392
        # https://github.com/giampaolo/psutil/issues/645
        # if not WINDOWS:
        #     last = psutil.cpu_times()
        #     for x in range(100):
        #         new = psutil.cpu_times()
        #         for field in new._fields:
        #             new_t = getattr(new, field)
        #             last_t = getattr(last, field)
        #             self.assertGreaterEqual(new_t, last_t,
        #                                     msg="%s %s" % (new_t, last_t))
        #         last = new

    def test_cpu_times_time_increases(self):
        # Make sure time increases between calls.
        t1 = sum(psutilcopy.cpu_times())
        time.sleep(0.1)
        t2 = sum(psutilcopy.cpu_times())
        difference = t2 - t1
        if not difference >= 0.05:
            self.fail("difference %s" % difference)

    def test_per_cpu_times(self):
        # Check type, value >= 0, str().
        for times in psutilcopy.cpu_times(percpu=True):
            total = 0
            sum(times)
            for cp_time in times:
                self.assertIsInstance(cp_time, float)
                self.assertGreaterEqual(cp_time, 0.0)
                total += cp_time
            self.assertEqual(total, sum(times))
            str(times)
        self.assertEqual(len(psutilcopy.cpu_times(percpu=True)[0]),
                         len(psutilcopy.cpu_times(percpu=False)))

        # Note: in theory CPU times are always supposed to increase over
        # time or remain the same but never go backwards. In practice
        # sometimes this is not the case.
        # This issue seemd to be afflict Windows:
        # https://github.com/giampaolo/psutil/issues/392
        # ...but it turns out also Linux (rarely) behaves the same.
        # last = psutil.cpu_times(percpu=True)
        # for x in range(100):
        #     new = psutil.cpu_times(percpu=True)
        #     for index in range(len(new)):
        #         newcpu = new[index]
        #         lastcpu = last[index]
        #         for field in newcpu._fields:
        #             new_t = getattr(newcpu, field)
        #             last_t = getattr(lastcpu, field)
        #             self.assertGreaterEqual(
        #                 new_t, last_t, msg="%s %s" % (lastcpu, newcpu))
        #     last = new

    def test_per_cpu_times_2(self):
        # Simulate some work load then make sure time have increased
        # between calls.
        tot1 = psutilcopy.cpu_times(percpu=True)
        stop_at = time.time() + 0.1
        while True:
            if time.time() >= stop_at:
                break
        tot2 = psutilcopy.cpu_times(percpu=True)
        for t1, t2 in zip(tot1, tot2):
            t1, t2 = sum(t1), sum(t2)
            difference = t2 - t1
            if difference >= 0.05:
                return
        self.fail()

    def test_cpu_times_comparison(self):
        # Make sure the sum of all per cpu times is almost equal to
        # base "one cpu" times.
        base = psutilcopy.cpu_times()
        per_cpu = psutilcopy.cpu_times(percpu=True)
        summed_values = base._make([sum(num) for num in zip(*per_cpu)])
        for field in base._fields:
            self.assertAlmostEqual(
                getattr(base, field), getattr(summed_values, field), delta=1)

    def _test_cpu_percent(self, percent, last_ret, new_ret):
        try:
            self.assertIsInstance(percent, float)
            self.assertGreaterEqual(percent, 0.0)
            self.assertIsNot(percent, -0.0)
            self.assertLessEqual(percent, 100.0 * psutilcopy.cpu_count())
        except AssertionError as err:
            raise AssertionError("\n%s\nlast=%s\nnew=%s" % (
                err, pprint.pformat(last_ret), pprint.pformat(new_ret)))

    def test_cpu_percent(self):
        last = psutilcopy.cpu_percent(interval=0.001)
        for x in range(100):
            new = psutilcopy.cpu_percent(interval=None)
            self._test_cpu_percent(new, last, new)
            last = new
        with self.assertRaises(ValueError):
            psutilcopy.cpu_percent(interval=-1)

    def test_per_cpu_percent(self):
        last = psutilcopy.cpu_percent(interval=0.001, percpu=True)
        self.assertEqual(len(last), psutilcopy.cpu_count())
        for x in range(100):
            new = psutilcopy.cpu_percent(interval=None, percpu=True)
            for percent in new:
                self._test_cpu_percent(percent, last, new)
            last = new
        with self.assertRaises(ValueError):
            psutilcopy.cpu_percent(interval=-1, percpu=True)

    def test_cpu_times_percent(self):
        last = psutilcopy.cpu_times_percent(interval=0.001)
        for x in range(100):
            new = psutilcopy.cpu_times_percent(interval=None)
            for percent in new:
                self._test_cpu_percent(percent, last, new)
            self._test_cpu_percent(sum(new), last, new)
            last = new

    def test_per_cpu_times_percent(self):
        last = psutilcopy.cpu_times_percent(interval=0.001, percpu=True)
        self.assertEqual(len(last), psutilcopy.cpu_count())
        for x in range(100):
            new = psutilcopy.cpu_times_percent(interval=None, percpu=True)
            for cpu in new:
                for percent in cpu:
                    self._test_cpu_percent(percent, last, new)
                self._test_cpu_percent(sum(cpu), last, new)
            last = new

    def test_per_cpu_times_percent_negative(self):
        # see: https://github.com/giampaolo/psutil/issues/645
        psutilcopy.cpu_times_percent(percpu=True)
        zero_times = [x._make([0 for x in range(len(x._fields))])
                      for x in psutilcopy.cpu_times(percpu=True)]
        with mock.patch('psutil.cpu_times', return_value=zero_times):
            for cpu in psutilcopy.cpu_times_percent(percpu=True):
                for percent in cpu:
                    self._test_cpu_percent(percent, None, None)

    def test_disk_usage(self):
        usage = psutilcopy.disk_usage(os.getcwd())
        self.assertEqual(usage._fields, ('total', 'used', 'free', 'percent'))

        assert usage.total > 0, usage
        assert usage.used > 0, usage
        assert usage.free > 0, usage
        assert usage.total > usage.used, usage
        assert usage.total > usage.free, usage
        assert 0 <= usage.percent <= 100, usage.percent
        if hasattr(shutil, 'disk_usage'):
            # py >= 3.3, see: http://bugs.python.org/issue12442
            shutil_usage = shutil.disk_usage(os.getcwd())
            tolerance = 5 * 1024 * 1024  # 5MB
            self.assertEqual(usage.total, shutil_usage.total)
            self.assertAlmostEqual(usage.free, shutil_usage.free,
                                   delta=tolerance)
            self.assertAlmostEqual(usage.used, shutil_usage.used,
                                   delta=tolerance)

        # if path does not exist OSError ENOENT is expected across
        # all platforms
        fname = tempfile.mktemp()
        with self.assertRaises(OSError) as exc:
            psutilcopy.disk_usage(fname)
        self.assertEqual(exc.exception.errno, errno.ENOENT)

    def test_disk_usage_unicode(self):
        # See: https://github.com/giampaolo/psutil/issues/416
        if ASCII_FS:
            with self.assertRaises(UnicodeEncodeError):
                psutilcopy.disk_usage(TESTFN_UNICODE)

    def test_disk_usage_bytes(self):
        psutilcopy.disk_usage(b'.')

    def test_disk_partitions(self):
        # all = False
        ls = psutilcopy.disk_partitions(all=False)
        # on travis we get:
        #     self.assertEqual(p.cpu_affinity(), [n])
        # AssertionError: Lists differ: [0, 1, 2, 3, 4, 5, 6, 7,... != [0]
        self.assertTrue(ls, msg=ls)
        for disk in ls:
            self.assertIsInstance(disk.device, str)
            self.assertIsInstance(disk.mountpoint, str)
            self.assertIsInstance(disk.fstype, str)
            self.assertIsInstance(disk.opts, str)
            if WINDOWS and 'cdrom' in disk.opts:
                continue
            if not POSIX:
                assert os.path.exists(disk.device), disk
            else:
                # we cannot make any assumption about this, see:
                # http://goo.gl/p9c43
                disk.device
            if SUNOS or TRAVIS:
                # on solaris apparently mount points can also be files
                assert os.path.exists(disk.mountpoint), disk
            else:
                assert os.path.isdir(disk.mountpoint), disk
            assert disk.fstype, disk

        # all = True
        ls = psutilcopy.disk_partitions(all=True)
        self.assertTrue(ls, msg=ls)
        for disk in psutilcopy.disk_partitions(all=True):
            if not WINDOWS:
                try:
                    os.stat(disk.mountpoint)
                except OSError as err:
                    if TRAVIS and OSX and err.errno == errno.EIO:
                        continue
                    # http://mail.python.org/pipermail/python-dev/
                    #     2012-June/120787.html
                    if err.errno not in (errno.EPERM, errno.EACCES):
                        raise
                else:
                    if SUNOS or TRAVIS:
                        # on solaris apparently mount points can also be files
                        assert os.path.exists(disk.mountpoint), disk
                    else:
                        assert os.path.isdir(disk.mountpoint), disk
            self.assertIsInstance(disk.fstype, str)
            self.assertIsInstance(disk.opts, str)

        def find_mount_point(path):
            path = os.path.abspath(path)
            while not os.path.ismount(path):
                path = os.path.dirname(path)
            return path.lower()

        mount = find_mount_point(__file__)
        mounts = [x.mountpoint.lower() for x in
                  psutilcopy.disk_partitions(all=True)]
        self.assertIn(mount, mounts)
        psutilcopy.disk_usage(mount)

    def test_net_io_counters(self):
        def check_ntuple(nt):
            self.assertEqual(nt[0], nt.bytes_sent)
            self.assertEqual(nt[1], nt.bytes_recv)
            self.assertEqual(nt[2], nt.packets_sent)
            self.assertEqual(nt[3], nt.packets_recv)
            self.assertEqual(nt[4], nt.errin)
            self.assertEqual(nt[5], nt.errout)
            self.assertEqual(nt[6], nt.dropin)
            self.assertEqual(nt[7], nt.dropout)
            assert nt.bytes_sent >= 0, nt
            assert nt.bytes_recv >= 0, nt
            assert nt.packets_sent >= 0, nt
            assert nt.packets_recv >= 0, nt
            assert nt.errin >= 0, nt
            assert nt.errout >= 0, nt
            assert nt.dropin >= 0, nt
            assert nt.dropout >= 0, nt

        ret = psutilcopy.net_io_counters(pernic=False)
        check_ntuple(ret)
        ret = psutilcopy.net_io_counters(pernic=True)
        self.assertNotEqual(ret, [])
        for key in ret:
            self.assertTrue(key)
            self.assertIsInstance(key, str)
            check_ntuple(ret[key])

    def test_net_io_counters_no_nics(self):
        # Emulate a case where no NICs are installed, see:
        # https://github.com/giampaolo/psutil/issues/1062
        with mock.patch('psutil._psplatform.net_io_counters',
                        return_value={}) as m:
            self.assertIsNone(psutilcopy.net_io_counters(pernic=False))
            self.assertEqual(psutilcopy.net_io_counters(pernic=True), {})
            assert m.called

    def test_net_if_addrs(self):
        nics = psutilcopy.net_if_addrs()
        assert nics, nics

        nic_stats = psutilcopy.net_if_stats()

        # Not reliable on all platforms (net_if_addrs() reports more
        # interfaces).
        # self.assertEqual(sorted(nics.keys()),
        #                  sorted(psutil.net_io_counters(pernic=True).keys()))

        families = set([socket.AF_INET, socket.AF_INET6, psutilcopy.AF_LINK])
        for nic, addrs in nics.items():
            self.assertIsInstance(nic, str)
            self.assertEqual(len(set(addrs)), len(addrs))
            for addr in addrs:
                self.assertIsInstance(addr.family, int)
                self.assertIsInstance(addr.address, str)
                self.assertIsInstance(addr.netmask, (str, type(None)))
                self.assertIsInstance(addr.broadcast, (str, type(None)))
                self.assertIn(addr.family, families)
                if sys.version_info >= (3, 4):
                    self.assertIsInstance(addr.family, enum.IntEnum)
                if nic_stats[nic].isup:
                    # Do not test binding to addresses of interfaces
                    # that are down
                    if addr.family == socket.AF_INET:
                        s = socket.socket(addr.family)
                        with contextlib.closing(s):
                            s.bind((addr.address, 0))
                    elif addr.family == socket.AF_INET6:
                        info = socket.getaddrinfo(
                            addr.address, 0, socket.AF_INET6,
                            socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[0]
                        af, socktype, proto, canonname, sa = info
                        s = socket.socket(af, socktype, proto)
                        with contextlib.closing(s):
                            s.bind(sa)
                for ip in (addr.address, addr.netmask, addr.broadcast,
                           addr.ptp):
                    if ip is not None:
                        # TODO: skip AF_INET6 for now because I get:
                        # AddressValueError: Only hex digits permitted in
                        # u'c6f3%lxcbr0' in u'fe80::c8e0:fff:fe54:c6f3%lxcbr0'
                        if addr.family != socket.AF_INET6:
                            check_net_address(ip, addr.family)
                # broadcast and ptp addresses are mutually exclusive
                if addr.broadcast:
                    self.assertIsNone(addr.ptp)
                elif addr.ptp:
                    self.assertIsNone(addr.broadcast)

        if BSD or OSX or SUNOS:
            if hasattr(socket, "AF_LINK"):
                self.assertEqual(psutilcopy.AF_LINK, socket.AF_LINK)
        elif LINUX:
            self.assertEqual(psutilcopy.AF_LINK, socket.AF_PACKET)
        elif WINDOWS:
            self.assertEqual(psutilcopy.AF_LINK, -1)

    def test_net_if_addrs_mac_null_bytes(self):
        # Simulate that the underlying C function returns an incomplete
        # MAC address. psutil is supposed to fill it with null bytes.
        # https://github.com/giampaolo/psutil/issues/786
        if POSIX:
            ret = [('em1', psutilcopy.AF_LINK, '06:3d:29', None, None, None)]
        else:
            ret = [('em1', -1, '06-3d-29', None, None, None)]
        with mock.patch('psutil._psplatform.net_if_addrs',
                        return_value=ret) as m:
            addr = psutilcopy.net_if_addrs()['em1'][0]
            assert m.called
            if POSIX:
                self.assertEqual(addr.address, '06:3d:29:00:00:00')
            else:
                self.assertEqual(addr.address, '06-3d-29-00-00-00')

    @unittest.skipIf(TRAVIS, "unreliable on TRAVIS")  # raises EPERM
    def test_net_if_stats(self):
        nics = psutilcopy.net_if_stats()
        assert nics, nics
        all_duplexes = (psutilcopy.NIC_DUPLEX_FULL,
                        psutilcopy.NIC_DUPLEX_HALF,
                        psutilcopy.NIC_DUPLEX_UNKNOWN)
        for name, stats in nics.items():
            self.assertIsInstance(name, str)
            isup, duplex, speed, mtu = stats
            self.assertIsInstance(isup, bool)
            self.assertIn(duplex, all_duplexes)
            self.assertIn(duplex, all_duplexes)
            self.assertGreaterEqual(speed, 0)
            self.assertGreaterEqual(mtu, 0)

    @unittest.skipIf(LINUX and not os.path.exists('/proc/diskstats'),
                     '/proc/diskstats not available on this linux version')
    @unittest.skipIf(APPVEYOR and psutilcopy.disk_io_counters() is None,
                     "unreliable on APPVEYOR")  # no visible disks
    def test_disk_io_counters(self):
        def check_ntuple(nt):
            self.assertEqual(nt[0], nt.read_count)
            self.assertEqual(nt[1], nt.write_count)
            self.assertEqual(nt[2], nt.read_bytes)
            self.assertEqual(nt[3], nt.write_bytes)
            if not (OPENBSD or NETBSD):
                self.assertEqual(nt[4], nt.read_time)
                self.assertEqual(nt[5], nt.write_time)
                if LINUX:
                    self.assertEqual(nt[6], nt.read_merged_count)
                    self.assertEqual(nt[7], nt.write_merged_count)
                    self.assertEqual(nt[8], nt.busy_time)
                elif FREEBSD:
                    self.assertEqual(nt[6], nt.busy_time)
            for name in nt._fields:
                assert getattr(nt, name) >= 0, nt

        ret = psutilcopy.disk_io_counters(perdisk=False)
        assert ret is not None, "no disks on this system?"
        check_ntuple(ret)
        ret = psutilcopy.disk_io_counters(perdisk=True)
        # make sure there are no duplicates
        self.assertEqual(len(ret), len(set(ret)))
        for key in ret:
            assert key, key
            check_ntuple(ret[key])
            if LINUX and key[-1].isdigit():
                # if 'sda1' is listed 'sda' shouldn't, see:
                # https://github.com/giampaolo/psutil/issues/338
                while key[-1].isdigit():
                    key = key[:-1]
                self.assertNotIn(key, ret.keys())

    def test_disk_io_counters_no_disks(self):
        # Emulate a case where no disks are installed, see:
        # https://github.com/giampaolo/psutil/issues/1062
        with mock.patch('psutil._psplatform.disk_io_counters',
                        return_value={}) as m:
            self.assertIsNone(psutilcopy.disk_io_counters(perdisk=False))
            self.assertEqual(psutilcopy.disk_io_counters(perdisk=True), {})
            assert m.called

    # can't find users on APPVEYOR or TRAVIS
    @unittest.skipIf(APPVEYOR or TRAVIS and not psutilcopy.users(),
                     "unreliable on APPVEYOR or TRAVIS")
    def test_users(self):
        users = psutilcopy.users()
        self.assertNotEqual(users, [])
        for user in users:
            assert user.name, user
            self.assertIsInstance(user.name, str)
            self.assertIsInstance(user.terminal, (str, type(None)))
            if user.host is not None:
                self.assertIsInstance(user.host, (str, type(None)))
            user.terminal
            user.host
            assert user.started > 0.0, user
            datetime.datetime.fromtimestamp(user.started)
            if WINDOWS or OPENBSD:
                self.assertIsNone(user.pid)
            else:
                psutilcopy.Process(user.pid)

    def test_cpu_stats(self):
        # Tested more extensively in per-platform test modules.
        infos = psutilcopy.cpu_stats()
        self.assertEqual(
            infos._fields,
            ('ctx_switches', 'interrupts', 'soft_interrupts', 'syscalls'))
        for name in infos._fields:
            value = getattr(infos, name)
            self.assertGreaterEqual(value, 0)
            # on AIX, ctx_switches is always 0
            if not AIX and name in ('ctx_switches', 'interrupts'):
                self.assertGreater(value, 0)

    @unittest.skipIf(not HAS_CPU_FREQ, "not suported")
    def test_cpu_freq(self):
        def check_ls(ls):
            for nt in ls:
                self.assertEqual(nt._fields, ('current', 'min', 'max'))
                self.assertLessEqual(nt.current, nt.max)
                for name in nt._fields:
                    value = getattr(nt, name)
                    self.assertIsInstance(value, (int, long, float))
                    self.assertGreaterEqual(value, 0)

        ls = psutilcopy.cpu_freq(percpu=True)
        if TRAVIS and not ls:
            return

        assert ls, ls
        check_ls([psutilcopy.cpu_freq(percpu=False)])

        if LINUX:
            self.assertEqual(len(ls), psutilcopy.cpu_count())

    def test_os_constants(self):
        names = ["POSIX", "WINDOWS", "LINUX", "OSX", "FREEBSD", "OPENBSD",
                 "NETBSD", "BSD", "SUNOS"]
        for name in names:
            self.assertIsInstance(getattr(psutilcopy, name), bool, msg=name)

        if os.name == 'posix':
            assert psutilcopy.POSIX
            assert not psutilcopy.WINDOWS
            names.remove("POSIX")
            if "linux" in sys.platform.lower():
                assert psutilcopy.LINUX
                names.remove("LINUX")
            elif "bsd" in sys.platform.lower():
                assert psutilcopy.BSD
                self.assertEqual([psutilcopy.FREEBSD, psutilcopy.OPENBSD,
                                  psutilcopy.NETBSD].count(True), 1)
                names.remove("BSD")
                names.remove("FREEBSD")
                names.remove("OPENBSD")
                names.remove("NETBSD")
            elif "sunos" in sys.platform.lower() or \
                    "solaris" in sys.platform.lower():
                assert psutilcopy.SUNOS
                names.remove("SUNOS")
            elif "darwin" in sys.platform.lower():
                assert psutilcopy.OSX
                names.remove("OSX")
        else:
            assert psutilcopy.WINDOWS
            assert not psutilcopy.POSIX
            names.remove("WINDOWS")

        # assert all other constants are set to False
        for name in names:
            self.assertIs(getattr(psutilcopy, name), False, msg=name)

    @unittest.skipIf(not HAS_SENSORS_TEMPERATURES, "not supported")
    def test_sensors_temperatures(self):
        temps = psutilcopy.sensors_temperatures()
        for name, entries in temps.items():
            self.assertIsInstance(name, str)
            for entry in entries:
                self.assertIsInstance(entry.label, str)
                if entry.current is not None:
                    self.assertGreaterEqual(entry.current, 0)
                if entry.high is not None:
                    self.assertGreaterEqual(entry.high, 0)
                if entry.critical is not None:
                    self.assertGreaterEqual(entry.critical, 0)

    @unittest.skipIf(not HAS_SENSORS_TEMPERATURES, "not supported")
    def test_sensors_temperatures_fahreneit(self):
        d = {'coretemp': [('label', 50.0, 60.0, 70.0)]}
        with mock.patch("psutil._psplatform.sensors_temperatures",
                        return_value=d) as m:
            temps = psutilcopy.sensors_temperatures(
                fahrenheit=True)['coretemp'][0]
            assert m.called
            self.assertEqual(temps.current, 122.0)
            self.assertEqual(temps.high, 140.0)
            self.assertEqual(temps.critical, 158.0)

    @unittest.skipIf(not HAS_SENSORS_BATTERY, "not supported")
    @unittest.skipIf(not HAS_BATTERY, "no battery")
    def test_sensors_battery(self):
        ret = psutilcopy.sensors_battery()
        self.assertGreaterEqual(ret.percent, 0)
        self.assertLessEqual(ret.percent, 100)
        if ret.secsleft not in (psutilcopy.POWER_TIME_UNKNOWN,
                                psutilcopy.POWER_TIME_UNLIMITED):
            self.assertGreaterEqual(ret.secsleft, 0)
        else:
            if ret.secsleft == psutilcopy.POWER_TIME_UNLIMITED:
                self.assertTrue(ret.power_plugged)
        self.assertIsInstance(ret.power_plugged, bool)

    @unittest.skipIf(not HAS_SENSORS_FANS, "not supported")
    def test_sensors_fans(self):
        fans = psutilcopy.sensors_fans()
        for name, entries in fans.items():
            self.assertIsInstance(name, str)
            for entry in entries:
                self.assertIsInstance(entry.label, str)
                self.assertIsInstance(entry.current, (int, long))
                self.assertGreaterEqual(entry.current, 0)


if __name__ == '__main__':
    run_test_module_by_name(__file__)
