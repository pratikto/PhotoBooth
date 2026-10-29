"""Actual frozen fixture process under the original crash-only launcher loop."""
import contextlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from unittest import TestCase
from unittest.mock import Mock, patch

from photobooth.qris_session import KioskLease
from photobooth.kiosk_v2.recovery import LaunchLease
from tests.test_checkout_backend import MERCHANT


class FrozenProcessHoldTests(TestCase):
    def test_ux11_real_blocked_main_and_worker_keep_paid_lease_without_restart_or_replay(self):
        from tools.run_qris_sandbox import main
        from tools.run_portrait_v2_sandbox import v2_environments
        repo=Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as temp:
            root=Path(temp).resolve()
            directory=root/'data'/'kiosk-v2-sandbox'/MERCHANT/'PB001'
            with (root/'fixture-stderr.txt').open('wb') as errors:
                child=subprocess.Popen([sys.executable,str(repo/'tests'/'ux11_frozen_fixture.py'),str(root)],
                    cwd=repo,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=errors)
                try:
                    deadline=time.monotonic()+10
                    while not (root/'fixture-ready').exists() and time.monotonic()<deadline:
                        self.assertIsNone(child.poll(),'Synthetic child exited before readiness')
                        time.sleep(.02)
                    self.assertTrue((root/'fixture-ready').exists())
                    journal=(directory/'visit.json').read_bytes()
                    def financial():
                        with contextlib.closing(sqlite3.connect(directory/'orders.sqlite')) as db:
                            return (db.execute('SELECT * FROM checkouts').fetchall(),
                                    db.execute('SELECT * FROM checkout_fulfillments').fetchall())
                    original=financial()
                    with contextlib.closing(sqlite3.connect(directory/'orders.sqlite')) as db:
                        self.assertEqual(db.execute("SELECT COUNT(*) FROM checkouts WHERE state='PAID' AND grant_id IS NOT NULL").fetchone()[0],1)
                        self.assertEqual(db.execute("SELECT obligation_state FROM checkout_fulfillments").fetchone()[0],'OWED')
                    server=Mock();server.poll.return_value=None
                    spawn=Mock(side_effect=[server,child]);stop=Mock();cycles=[]
                    def factory(parent,merchant,key,booth,port):
                        return v2_environments(parent,merchant,key,booth,port,root)
                    def observe(delay):
                        self.assertEqual(delay,1)  # Observation, never restart cooldown.
                        self.assertIsNone(child.poll())
                        self.assertFalse(stop.called)
                        self.assertEqual(spawn.call_count,2)
                        self.assertEqual((directory/'visit.json').read_bytes(),journal)
                        self.assertEqual(financial(),original)
                        self.assertFalse((directory/'crash-budget.json').exists())
                        # Windows mandatory byte locks may reject the initial
                        # read with OSError before KioskLease wraps lock failure.
                        # Both outcomes deny the second owner; no error message
                        # or platform-specific errno is part of this contract.
                        with self.assertRaises((RuntimeError,OSError)):
                            KioskLease(str(directory/'visit.json')+'.lock')
                        with self.assertRaises(OSError):LaunchLease(root)
                        cycles.append(delay)
                        if len(cycles)==3:raise KeyboardInterrupt
                    with patch.dict(os.environ,{'MIDTRANS_SERVER_KEY':'SB-Mid-server-TEST','MIDTRANS_MERCHANT_ID':MERCHANT}), \
                         patch('importlib.util.find_spec',return_value=object()), \
                         patch('tools.run_qris_sandbox.ROOT',root), \
                         patch('tools.run_qris_sandbox.socket.socket'), \
                         patch('tools.run_qris_sandbox.wait_ready'), \
                         patch('tools.run_qris_sandbox.subprocess.Popen',spawn), \
                         patch('tools.run_qris_sandbox.stop',stop), \
                         patch('tools.run_qris_sandbox.time.sleep',side_effect=observe), \
                         patch('photobooth.kiosk_v2.crash_supervisor.CrashBudget.reserve',side_effect=AssertionError('Live child cannot reserve restart')), \
                         contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(main(['--restart-crashed-gui','--booth-id','PB001'],
                            environment_factory=factory,gui_entry=('synthetic-held-gui',),allow_crash_restart=True),130)
                    self.assertEqual(len(cycles),3)
                    self.assertEqual(spawn.call_count,2)
                    self.assertIsNone(child.poll())
                    self.assertEqual(financial(),original)
                    self.assertEqual((directory/'visit.json').read_bytes(),journal)
                finally:
                    # Only the test ends its own disposable process, after observation.
                    if child.poll() is None:
                        try:child.communicate(input=b'x',timeout=10)
                        except subprocess.TimeoutExpired:child.kill();child.communicate(timeout=5)
                    else:child.communicate(timeout=5)
                self.assertEqual(child.returncode,0)
                self.assertEqual(json.loads((root/'fixture-result.json').read_text())['charges'],1)
