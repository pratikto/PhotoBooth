"""AR-12 actual exited-process WAL boundaries and failed-writer atomicity."""
from contextlib import closing
from pathlib import Path
import subprocess,sys,sqlite3
from unittest import TestCase
from photobooth.checkout_store import CheckoutStore
from photobooth import checkout_release
import tests.test_checkout_release as fixture

class RecoveryFaultTests(TestCase):
    def setUp(self):fixture.ReleaseTests.setUp(self)
    def test_abrupt_release_exit_preserves_wal_integrity_and_owed_rights(self):
        for phase in ('prepared','acked'):
            with self.subTest(phase=phase):
                # New isolated fixture per crash, never real customer state.
                case=fixture.ReleaseTests();case.setUp()
                try:
                    before=case.store.get(case.oid)
                    result=subprocess.run([sys.executable,'-m','tests.release_crash_fixture',str(case.path),case.oid,phase],
                        cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,timeout=20)
                    self.assertEqual(result.returncode,71,result.stderr)
                    with closing(CheckoutStore(case.path)) as reopened:
                        self.assertEqual(reopened.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
                        after=reopened.get(case.oid)
                        for key in ('state','grant_id','service_state','local_transaction_id'):
                            self.assertEqual(after[key],before[key])
                        self.assertEqual(reopened.fulfillment(case.oid,'PB001')['obligation_state'],'OWED')
                        self.assertEqual(bool(after['closed']),phase=='acked')
                        self.assertEqual(reopened.db.execute('SELECT count(*) FROM checkout_releases').fetchone()[0],1)
                finally:case.doCleanups()
    def test_locked_sqlite_writer_cannot_partially_fence_or_ack_release(self):
        before=self.store.get(self.oid)
        with closing(CheckoutStore(self.path)) as blocker:
            blocker.db.execute('BEGIN IMMEDIATE');self.store.db.execute('PRAGMA busy_timeout=1')
            try:
                with self.assertRaises(sqlite3.OperationalError):
                    checkout_release.prepare(self.store,self.oid,'PB001','e'*32,'lock-fixture')
            finally:blocker.db.rollback()
        self.assertEqual(self.store.get(self.oid),before)
        self.assertIsNone(self.store.service_fence(self.oid,'PB001'))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM checkout_releases').fetchone()[0],0)
        checkout_release.prepare(self.store,self.oid,'PB001','e'*32,'lock-fixture')
        self.assertEqual(self.store.service_fence(self.oid,'PB001')['generation'],1)
