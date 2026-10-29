"""Disposable blocked-main/checkout-worker process; never a real booth."""
from pathlib import Path
import json
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from photobooth.checkout_backend import CheckoutBackend
from photobooth.checkout_store import CheckoutStore
from photobooth.qris_session import KioskCheckout
from photobooth.kiosk_v2.demo_game import GameJobs
from photobooth.kiosk_v2.recovery import LaunchLease
from tests.test_checkout_backend import FakeProvider, KEY, MERCHANT
from tests.test_qris_session import LocalClient


def main(root):
    directory=root/'data'/'kiosk-v2-sandbox'/MERCHANT/'PB001'
    with LaunchLease(root):
        store=CheckoutStore(directory/'orders.sqlite')
        provider=FakeProvider();provider.mode='sandbox'
        client=LocalClient(CheckoutBackend(store,provider,KEY,MERCHANT))
        flow=KioskCheckout(directory/'visit.json',client,mode='sandbox',booth_id='PB001',endpoint='http://127.0.0.1:8000')
        entered,release=threading.Event(),threading.Event()
        jobs=GameJobs(lambda:client,actions={'status'})
        try:
            flow.begin({'template_a':1});flow.refresh()
            oid=flow.snapshot()['order']['order_id']
            provider.rows[oid].update(transaction_status='settlement',status_code='200')
            store.db.execute('UPDATE checkouts SET check_after=0')
            flow.refresh()
            assert flow.snapshot()['phase']=='RESERVED'
            status=client.status
            def frozen(oid):
                entered.set()
                release.wait()
                return status(oid)
            client.status=frozen
            assert jobs.submit('status',0,oid)
            assert entered.wait(5)
            (root/'fixture-ready').write_text('BLOCKED MAIN AND CHECKOUT WORKER')
            # Test control channel only. Production code never sends this.
            sys.stdin.buffer.read(1)
        finally:
            release.set();jobs.wait_closed(5);jobs.close()
            (root/'fixture-result.json').write_text(json.dumps({'charges':provider.charges}))
            flow.close();store.close()


if __name__=='__main__':
    main(Path(sys.argv[1]).resolve())
