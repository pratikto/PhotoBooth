"""Actual runner progress is visible before completion and cannot mask failure."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest


class KioskRunnerProgressTests(unittest.TestCase):
    def test_blocked_case_emits_static_start_before_finish_and_keeps_real_exit_status(self):
        repository=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            temporary=Path(folder);gate=temporary/'release'
            (temporary/'runner_progress_fixture.py').write_text('''import os,time,unittest
from pathlib import Path
class GateTests(unittest.TestCase):
    def test_gate(self):
        deadline=time.monotonic()+15
        while not Path(os.environ['MEONG_PROGRESS_GATE']).exists():
            if time.monotonic()>deadline:raise TimeoutError('Synthetic gate not released')
            time.sleep(.01)
        if os.environ.get('MEONG_PROGRESS_FAIL')=='1':self.fail('Controlled synthetic failure')
''')
            environment=dict(os.environ,PYTHONPATH=str(temporary),MEONG_CI_PROGRESS='1',
                             MEONG_PROGRESS_GATE=str(gate),MEONG_PROGRESS_FAIL='1')
            command=[sys.executable,str(repository/'tools'/'run_kiosk_unittests.py'),
                     'runner_progress_fixture.GateTests.test_gate']
            process=subprocess.Popen(command,cwd=repository,env=environment,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            lines=[];started=threading.Event()
            def read():
                for line in process.stdout:
                    lines.append(line)
                    if line.startswith('KIOSK_TEST_START 1: runner_progress_fixture.GateTests.test_gate'):
                        started.set()
            reader=threading.Thread(target=read,daemon=True);reader.start()
            try:
                self.assertTrue(started.wait(10),'Case START was hidden until completion')
                self.assertIsNone(process.poll());self.assertFalse(gate.exists())
            finally:
                gate.write_text('release synthetic gate')
                process.wait(timeout=10);reader.join(3)
                process.stdout.close();process.stderr.close()
            self.assertFalse(reader.is_alive())
            self.assertEqual(1,process.returncode)
            report=''.join(lines)
            self.assertIn('KIOSK_TEST_END 1: runner_progress_fixture.GateTests.test_gate',report)
            self.assertIn('run=1 failures=1 errors=0 skipped=0 success=False',report)
            self.assertNotIn(str(gate),report)
            # Default output/exit/report still follow the original runner.
            environment.update(MEONG_CI_PROGRESS='0',MEONG_PROGRESS_FAIL='0')
            passed=subprocess.run(command,cwd=repository,env=environment,capture_output=True,
                                  text=True,timeout=15)
            self.assertEqual(0,passed.returncode,passed.stderr)
            self.assertIn('run=1 failures=0 errors=0 skipped=0 success=True',passed.stdout)
            self.assertNotIn('KIOSK_TEST_START',passed.stdout)


if __name__=='__main__':unittest.main()
