"""Crash ONLY an isolated fake-effects original manager, never customer data."""
from contextlib import nullcontext
import os
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from PIL import Image

from photobooth.catalog import get_templates
from photobooth.checkout_store import CheckoutStore
from photobooth.kiosk_v2.health_service import CachedCamera
from photobooth.post_preview_host import SandboxHostConfig
from photobooth.post_preview_sandbox_visits import OriginalSandboxVisits
from photobooth.post_preview_store import DraftLease, DraftHeld
from photobooth.printer import PrinterConfig
from tests import test_post_preview_sandbox_visits as helpers


def run(storage, mode):
    config=SandboxHostConfig(storage,'MTEST','PB001','Mid-server-DELIVERY-FIXTURE',
        'b'*48,'https://script.google.com/macros/s/INTERRUPTED_FIXTURE/exec','fixture-drive')
    context=nullcontext() if os.name=='nt' else patch(
        'photobooth.linux_credential_vault._read_key',return_value=b'k'*32)
    with context,patch('photobooth.post_preview_bootstrap.CHILD_MODULE','tests.post_preview_host_process_fixture'):
        legacy=CheckoutStore(storage/'legacy.sqlite3')
        frame=np.zeros((24,32,3),dtype=np.uint8)
        manager=OriginalSandboxVisits(config,PrinterConfig(lan_host='fixture-printer',usb_device_path=None),
            legacy,camera=CachedCamera(frame,0),qr_loader=lambda _:Image.new('RGB',(200,200),'white'),
            printer_dial=lambda *_:SimpleNamespace(close=lambda:None),durable_worker_epochs=True)
        binding=manager.start(); service=binding.service
        release=config.private_root/'fixture-http-release'; release.touch()
        helper=helpers.OriginalSandboxVisitTests(methodName='runTest'); helper.frame=frame
        if mode in {'paid','delivery','orphan','receipt'}:
            if mode=='delivery': group,_=helper.paid(binding)
            else:
                group,_=helper.frozen(binding)
                service.begin_payment()
                def paid():
                    if service.check_payment('connectivity')['phase']!='paid_hold': raise DraftHeld('Fixture pacing')
                helper.retry(paid)
                if mode=='receipt':
                    ticket=service.prepare_ticket(); service.ticket_visible(ticket['ticket_offer'])
                    # Keep PREPARED. The parent injects uncertainty into this
                    # isolated pending intent; never rewrite terminal SUBMITTED.
        else:
            service.start(get_templates(),{'template_a':1})
        if mode=='active':
            print('READY',flush=True); os._exit(73)
        service.retire('USER_CANCEL')
        if mode=='unprepared':
            print('READY',flush=True); os._exit(73)
        if not manager._server.stop(timeout=3) or not manager._jobs.retire(timeout=3):
            raise AssertionError('Actual original fixture workers did not finish')
        lease=service.lease
        retired=DraftLease(lease.draft_id,lease.booth_id,lease.visit_id,lease.generation+1)
        operation=helper.retry(lambda:manager._handoff.prepare(retired))
        if mode!='missing-receipt': manager._native.publish(operation.operation_id,timeout=3)
        if mode=='orphan':
            (config.private_root/'fixture-force-http-hold').touch()
            release.unlink()  # Isolated fixture marker, never a customer journal.
            def blocked():
                deadline=time.monotonic()+12
                while not (config.private_root/'fixture-http-entered').exists() and time.monotonic()<deadline:
                    try: manager._client.reconcile(group,trigger='connectivity')
                    except Exception: pass
                    time.sleep(.02)
            threading.Thread(target=blocked,daemon=True).start()
            deadline=time.monotonic()+12
            while not (config.private_root/'fixture-http-entered').exists():
                if time.monotonic()>deadline: raise AssertionError('Actual fixture backend HTTP did not enter')
                time.sleep(.01)
        print('READY',flush=True)  # Static status ONLY: no key/proof/order/photo.
        os._exit(73)  # Intentional isolated test process loss; no force-killed worker.


if __name__=='__main__': run(Path(sys.argv[1]),sys.argv[2])
