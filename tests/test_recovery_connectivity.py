"""Passive OS hints and coalesced restoration; no real OS/network requests."""
import subprocess
import unittest
from unittest.mock import Mock

from photobooth.kiosk_v2.connectivity import ConnectivityRestoration, read_connectivity_hint


class ConnectivityReaderTests(unittest.TestCase):
    def test_linux_reads_cached_networkmanager_state_without_active_probe(self):
        run = Mock(return_value=subprocess.CompletedProcess([], 0, b'full\n'))
        self.assertTrue(read_connectivity_hint(system='Linux', run=run, environ={'PATH': '/usr/bin'}))
        args, options = run.call_args
        self.assertEqual(args[0], ['nmcli', '--terse', '--fields', 'CONNECTIVITY', 'general'])
        self.assertNotIn('check', args[0])
        self.assertFalse(options['shell'])
        self.assertLessEqual(options['timeout'], 2)
        self.assertIs(options['stderr'], subprocess.DEVNULL)

    def test_linux_offline_portal_and_unknown_never_imply_online(self):
        for output, expected in ((b'none\n', False), (b'limited\n', False),
                                 (b'portal\n', False), (b'unknown\n', None),
                                 (b'connected\n', None)):
            with self.subTest(output=output):
                run = Mock(return_value=subprocess.CompletedProcess([], 0, output))
                self.assertIs(read_connectivity_hint(system='Linux', run=run, environ={}), expected)

    def test_windows_reads_nlm_flags_without_profile_or_credential_environment(self):
        env = {'SystemRoot': r'C:\Windows', 'PATH': 'system-bin',
               'MIDTRANS_SERVER_KEY': 'SYNTHETIC-SECRET', 'MEONG_QRIS_BOOTH_TOKEN': 'SYNTHETIC-TOKEN',
               'MEONG_QRIS_RECOVERY_PIN': '12345678', 'PSModulePath': 'untrusted-profile'}
        run = Mock(return_value=subprocess.CompletedProcess([], 0, b'64\r\n'))
        self.assertTrue(read_connectivity_hint(system='Windows', run=run, environ=env))
        args, options = run.call_args
        self.assertEqual(args[0][0], r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe')
        self.assertIn('-NoProfile', args[0])
        self.assertIn('-NonInteractive', args[0])
        self.assertIn('GetConnectivity', args[0][-1])
        self.assertEqual(options['env'], {'SystemRoot': r'C:\Windows', 'PATH': 'system-bin'})
        self.assertNotIn('SYNTHETIC', str(args[0]))

    def test_windows_ipv4_ipv6_local_only_and_invalid_results(self):
        for output, expected in ((b'0', False), (b'32', False), (b'512', False),
                                 (b'1024', True), (b'1088', True), (b'-1', None),
                                 (b'not-a-state', None), (b'65535', None)):
            with self.subTest(output=output):
                run = Mock(return_value=subprocess.CompletedProcess([], 0, output))
                self.assertIs(read_connectivity_hint(system='Windows', run=run,
                    environ={'SystemRoot': r'C:\Windows'}), expected)

    def test_unavailable_failed_timeout_and_oversized_queries_are_unknown(self):
        runs = [Mock(side_effect=FileNotFoundError()),
                Mock(side_effect=subprocess.TimeoutExpired('nmcli', 1.5)),
                Mock(return_value=subprocess.CompletedProcess([], 1, b'full')),
                Mock(return_value=subprocess.CompletedProcess([], 0, b'x' * 65)),
                Mock(return_value=subprocess.CompletedProcess([], 0, b'\xff'))]
        for run in runs:
            with self.subTest(run=run):
                self.assertIsNone(read_connectivity_hint(system='Linux', run=run, environ={}))

    def test_unsupported_platform_and_unsafe_windows_root_do_not_launch(self):
        run = Mock(side_effect=AssertionError('No command expected'))
        self.assertIsNone(read_connectivity_hint(system='Darwin', run=run, environ={}))
        for root in ('', 'relative', r'\\remote\share', r'C:\Windows\..\other'):
            with self.subTest(root=root):
                self.assertIsNone(read_connectivity_hint(system='Windows', run=run,
                                                        environ={'SystemRoot': root}))
        run.assert_not_called()


class ConnectivityObserverTests(unittest.TestCase):
    def test_initial_online_is_not_a_restoration_and_polling_is_bounded(self):
        now = [100.0]
        read = Mock(return_value=True)
        observer = ConnectivityRestoration(read=read, clock=lambda: now[0])
        self.assertFalse(observer.poll())
        for _ in range(50):
            self.assertFalse(observer.poll())
        self.assertEqual(read.call_count, 1)
        now[0] += 5
        self.assertFalse(observer.poll())
        self.assertEqual(read.call_count, 2)

    def test_offline_unknown_online_emits_once_and_a_new_outage_can_rearm(self):
        now = [100.0]
        read = Mock(side_effect=[False, None, True, True, False, True])
        observer = ConnectivityRestoration(read=read, clock=lambda: now[0])
        events = []
        for _ in range(6):
            events.append(observer.poll())
            now[0] += 5
        self.assertEqual(events, [False, False, True, False, False, True])

    def test_unknown_or_reader_failure_without_offline_never_invents_an_edge(self):
        now = [100.0]
        observer = ConnectivityRestoration(read=Mock(side_effect=[None, OSError(), True]),
                                           clock=lambda: now[0])
        for _ in range(3):
            self.assertFalse(observer.poll())
            now[0] += 5
