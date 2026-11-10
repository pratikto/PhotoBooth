"""Bounded public UI queues over a separately retained trusted visit worker.

Only the trusted launcher keeps the worker/manager handle. GUI code receives
VisitControl, never configuration, worker keys, provider or custody authority.
No customer launcher or default merchant profile is enabled here.
"""
from dataclasses import dataclass,field
import queue
import re
import threading
import time
import uuid

from photobooth.post_preview_sandbox_visits import OriginalSandboxVisits,NativeVisitBinding
from photobooth.post_preview_store import DraftHeld

_EVENTS=frozenset({'USER_CANCEL','APP_SUSPENDED','INACTIVITY_EXPIRED','VISIT_ABANDONED','RESULT_TIMEOUT'})


@dataclass(frozen=True)
class _Command:
    request_id:str
    epoch:int
    action:str
    proof:str|None=field(default=None,repr=False)


@dataclass(frozen=True)
class VisitControlOutcome:
    request_id:str
    epoch:int
    action:str
    state:str
    binding:NativeVisitBinding|None=field(default=None,repr=False)
    snapshot:dict|None=field(default=None,repr=False)


class VisitControl:
    """UI-only nonblocking submission/poll/privacy; not a FREE assertion."""
    def __init__(self):
        self._commands=queue.Queue(maxsize=1)
        self._results=queue.Queue(maxsize=1)
        self._lock=threading.Lock()
        self._privacy=threading.Event()
        self._stop=threading.Event()
        self._stopped=threading.Event()
        self._epoch=0
        self._privacy_serial=0
        self._reason=None
        self._pending=self._issued=self._binding=None
        self._state='PROTECTED'

    @property
    def binding(self):return self._binding

    @property
    def busy(self):
        with self._lock:return self._pending is not None or self._privacy.is_set() or self._stop.is_set() and not self.stopped

    @property
    def stopped(self):return self._stopped.is_set()

    @property
    def state(self):return self._state

    def _submit(self,action,proof=None):
        with self._lock:
            if self._pending is not None or self._privacy.is_set() or self._stop.is_set():return False
            command=_Command(uuid.uuid4().hex,self._epoch,action,proof)
            self._pending=(command.request_id,command.epoch,action)
            self._state='BUSY'
            self._commands.put_nowait(command)
            return True

    def start(self):return self._submit('start')
    def ready(self):return self._submit('ready')

    def claim(self,proof):
        if (type(proof) is not str or len(proof)>256 or re.fullmatch(
                r'MEONG:(?:CCP|RECOVERY):1:PB[0-9]{3,8}:[a-f0-9]{32}:[A-Za-z0-9_-]{43}',proof) is None):
            raise ValueError('Original private customer proof required')
        return self._submit('claim',proof)

    def hide_private(self,event):
        if type(event) is not str or event not in _EVENTS:
            raise ValueError('Original privacy event required')
        with self._lock:
            self._epoch+=1;self._privacy_serial+=1
            if self._reason is None:self._reason=event
            self._privacy.set();self._state='PROTECTED'
            binding=self._binding
            if self._issued is not None:
                self._pending=self._issued=None
            self._discard_results()
        if binding is not None:binding.service.hide_private()

    def request_stop(self):
        if not self._stop.is_set():self.hide_private('APP_SUSPENDED')
        self._stop.set();self._state='STOPPING'

    def _discard_results(self):
        while True:
            try:self._results.get_nowait()
            except queue.Empty:return

    def _discard_commands(self):
        while True:
            try:self._commands.get_nowait()
            except queue.Empty:return

    def _current(self,command):
        with self._lock:
            return self._pending==(command.request_id,command.epoch,command.action) and command.epoch==self._epoch and not self._stop.is_set()

    def _complete(self,command,outcome):
        with self._lock:
            if self._pending!=(command.request_id,command.epoch,command.action):return False
            if command.epoch!=self._epoch or self._stop.is_set():
                self._pending=self._issued=None
                return False
            self._discard_results()
            self._issued=outcome
            self._results.put_nowait(outcome)
            return True

    def poll(self):
        with self._lock:
            try:outcome=self._results.get_nowait()
            except queue.Empty:return None
            if (type(outcome) is not VisitControlOutcome or outcome is not self._issued
                    or self._pending!=(outcome.request_id,outcome.epoch,outcome.action)
                    or outcome.epoch!=self._epoch or self._stop.is_set()):return None
            self._issued=self._pending=None
            self._state=outcome.state
            if outcome.binding is not None:self._binding=outcome.binding
            return outcome


class TrustedVisitWorker:
    """Launcher-only handle. stop=False retains thread/manager/kernel ownership."""
    def __init__(self,visits,control,*,finish_on_stop=False):
        if (type(visits) is not OriginalSandboxVisits or type(control) is not VisitControl
                or type(finish_on_stop) is not bool):
            raise TypeError('Exact original trusted visit manager/control required')
        self._visits,self._control=visits,control
        self._finish_on_stop=finish_on_stop
        self._thread=threading.Thread(target=self._run,name='postpay-native-control',daemon=True)

    def start(self):self._thread.start()

    def stop(self,*,timeout=0):
        if type(timeout) not in (int,float) or not 0<=timeout<=15:
            raise ValueError('Bounded trusted worker shutdown required')
        self._control.request_stop()
        self._thread.join(timeout)
        return not self._thread.is_alive() and self._control.stopped

    def _retire(self):
        control=self._control
        with control._lock:serial,reason=control._privacy_serial,control._reason
        if reason is None:return True
        try:
            if self._finish_on_stop and control._stop.is_set():
                self._visits.retire_for_shutdown(reason)
            else:self._visits.retire_current(reason)
        except Exception:return False  # No private exception/proof/config in GUI output.
        with control._lock:
            if serial==control._privacy_serial:
                control._reason=None;control._privacy.clear()
                return True
        return False

    def _claim_can_retry(self):
        visits=self._visits
        if visits._closing or visits._opening or visits._acked:return True
        pending=visits._pending_claim
        if pending is None or pending[3]!=visits._epoch:return False
        try:
            with visits.ledger.lock:
                row=visits.ledger.db.execute('SELECT * FROM pp_protected_claim_ops WHERE request_id=?',
                                             (pending[0],)).fetchone()
                return bool(row and (row['purchase_group_id'],row['proof_sha256'])==(pending[1],pending[2]))
        except Exception:return False

    def _execute(self,command):
        visits=self._visits;deadline=time.monotonic()+12
        while True:
            if not self._control._current(command):raise DraftHeld('Original UI request retired')
            try:
                if command.action in {'start','ready'}:
                    binding=visits.start() if command.action=='start' and not visits._admitted else visits.ensure_new_visitor_ready()
                    state,snapshot='READY',None
                else:
                    result=visits.recover_paid(command.proof)
                    if result['state']=='WAIT':return VisitControlOutcome(command.request_id,command.epoch,command.action,'WAIT')
                    binding=result['binding'];snapshot=result['snapshot'];state='RESTORED'
                    if snapshot.get('phase')=='hold':raise DraftHeld('Original private result held')
                if type(binding) is not NativeVisitBinding or binding is not visits._binding:
                    raise DraftHeld('Original native binding changed')
                return VisitControlOutcome(command.request_id,command.epoch,command.action,state,binding,snapshot)
            except DraftHeld:
                if (not self._control._current(command) or time.monotonic()>=deadline
                        or command.action=='claim' and not self._claim_can_retry()):raise
                self._control._stop.wait(.25)

    def _run(self):
        control=self._control;visits=self._visits
        while True:
            if control._stop.is_set():
                # A failed/unknown startup may close its own handles without
                # adopting any old owner. An admitted privacy-late claim must
                # first complete its exact metadata retirement.
                if visits._admitted and not visits._stopping and control._privacy.is_set() and not self._retire():
                    control._stop.wait(.05);time.sleep(.05);continue
                if self._finish_on_stop and visits._admitted and not visits._stopping:
                    try:visits.finish_for_shutdown()
                    except Exception:
                        time.sleep(.05);continue  # Original financial/receipt uncertainty is NOT a release.
                try:closed=visits.stop()
                except Exception:closed=False
                if closed and visits._closed and visits._launcher.stream.closed:
                    with control._lock:
                        control._pending=control._issued=None;control._discard_results()
                        control._discard_commands()
                        control._reason=None;control._privacy.clear()
                        control._state='STOPPED';control._stopped.set()
                    return
                time.sleep(.05);continue
            if control._privacy.is_set():
                if not self._retire():time.sleep(.05)
                continue
            try:command=control._commands.get(timeout=.05)
            except queue.Empty:continue
            try:
                try:outcome=self._execute(command)
                except PermissionError:outcome=VisitControlOutcome(command.request_id,command.epoch,command.action,'DENIED')
                except Exception:outcome=VisitControlOutcome(command.request_id,command.epoch,command.action,'HOLD')
                if not control._complete(command,outcome):
                    binding=visits._binding
                    if binding is not None:binding.service.hide_private()
            finally:
                command=outcome=None  # Drop transient private proof/snapshot references.


def create_visit_control(visits,*,finish_on_stop=False):
    """Trusted launcher retains worker; only control is supplied to the GUI."""
    control=VisitControl();worker=TrustedVisitWorker(visits,control,finish_on_stop=finish_on_stop);worker.start()
    return control,worker
