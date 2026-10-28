"""Offline crash-only bounded restart admission, no camera or provider."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from photobooth.kiosk_v2.crash_supervisor import CrashBudget
import json

class CrashSupervisorTests(TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.now=[1000.0];self.budget=CrashBudget(self.root/'budget.json',clock=lambda:self.now[0])
        self.env={'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'1','MEONG_QRIS_MODE':'sandbox','PHOTOBOOTH_LOCAL_ONLY':'1',
            'PHOTOBOOTH_V2_PRINT':'0','PHOTOBOOTH_V2_DRIVE':'0','MEONG_QRIS_JOURNAL':str(self.root/'visit.json'),
            'MEONG_QRIS_BOOTH_ID':'PB001','MEONG_QRIS_API_URL':'http://127.0.0.1:8765'}
    def reserve(self,code=1,**env):return self.budget.reserve(code,dict(self.env,**env),child_exited=True)
    def test_three_crashes_have_persisted_budget_and_bounded_backoff(self):
        self.assertEqual(self.reserve(),5);self.now[0]+=5
        self.assertEqual(self.reserve(),10);self.now[0]+=10
        reopened=CrashBudget(self.root/'budget.json',clock=lambda:self.now[0])
        self.assertEqual(reopened.reserve(1,self.env,child_exited=True),20)
        self.assertIsNone(self.reserve());self.now[0]+=601
        self.assertEqual(self.reserve(),5)
    def test_normal_operator_hold_or_living_process_never_restarts(self):
        for code in (0,2,3,130,-2,-15):self.assertIsNone(self.reserve(code))
        self.assertIsNone(self.budget.reserve(1,self.env,child_exited=False))
        self.assertFalse(self.budget.path.exists())
    def test_delivery_production_and_corrupt_journal_fail_closed(self):
        for fields in ({'PHOTOBOOTH_V2_PRINT':'1'},{'PHOTOBOOTH_V2_DRIVE':'1'},
                       {'MEONG_QRIS_MODE':'production'},{'MIDTRANS_SERVER_KEY':'test-only'}):
            self.assertIsNone(self.reserve(**fields))
        (self.root/'visit.json').write_text('corrupt')
        self.assertIsNone(self.reserve())
    def test_bad_budget_and_clock_rollback_never_reset_restart_allowance(self):
        self.reserve();self.now[0]-=1
        with self.assertRaises(RuntimeError):self.reserve()
        self.budget.path.write_text('{"version":1,"attempts":[],"observed_at":"invalid"}')
        with self.assertRaises(RuntimeError):self.reserve()

    def test_launcher_restarts_exited_child_once_then_preserves_normal_exit(self):
        import contextlib,io,os
        from unittest.mock import Mock,patch
        from tools.run_qris_sandbox import main
        from tools.run_portrait_v2_sandbox import v2_environments
        server,crashed,finished=Mock(),Mock(),Mock()
        server.poll.return_value=None;crashed.poll.return_value=1;finished.poll.return_value=0
        calls=[]
        def spawn(command,**kwargs):
            calls.append((list(command),dict(kwargs['env'])))
            return [server,crashed,finished][len(calls)-1]
        def environments(parent,merchant,key,booth,port):
            return v2_environments(parent,merchant,key,booth,port,self.root)
        with patch.dict(os.environ,{'MIDTRANS_SERVER_KEY':'SB-Mid-server-TEST','MIDTRANS_MERCHANT_ID':'MTEST'},clear=True), \
             patch('importlib.util.find_spec',return_value=object()),patch('tools.run_qris_sandbox.socket.socket'), \
             patch('tools.run_qris_sandbox.wait_ready'),patch('tools.run_qris_sandbox.subprocess.Popen',side_effect=spawn), \
             patch('tools.run_qris_sandbox.time.sleep') as wait, \
             patch('photobooth.kiosk_v2.recovery.LaunchLease') as launch_lease,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--restart-crashed-gui'],environment_factory=environments,
                gui_entry=('tools/run_portrait_v2.py',),allow_crash_restart=True),0)
        self.assertEqual(len(calls),3)
        wait.assert_called_once_with(5)
        launch_lease.assert_called_once()
        self.assertEqual(calls[1],calls[2])
        self.assertNotIn('MIDTRANS_SERVER_KEY',calls[2][1])
        self.assertFalse(crashed.terminate.called)
