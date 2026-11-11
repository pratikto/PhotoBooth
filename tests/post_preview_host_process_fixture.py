"""Child-process fixture ONLY: fake HTTP/key lookup, original production host."""
import io
import json
import os
import sys
import time
from unittest.mock import patch

from photobooth import post_preview_host as host
from photobooth import post_preview_bootstrap as bootstrap

original=host.build_sandbox_app


def assembled(checkout,templates,bridge,drive,**kwargs):
    # Prove secrets arrived over the private channel, not process environment/argv.
    secrets=(kwargs['server_key'],kwargs['booth_token'],drive.client.upload_token)
    assert all(secret not in os.environ.values() and
               not any(secret in arg for arg in sys.argv) for secret in secrets)
    assert 'kivy' not in sys.modules
    worker_key=kwargs.get('worker_fence_key')
    if worker_key is not None:
        assert worker_key.secret.hex() not in os.environ.values()
        assert not any(worker_key.secret.hex() in arg for arg in sys.argv)
    if kwargs['server_key']=='Mid-server-FAIL-FIXTURE':
        raise RuntimeError('Never echo '+kwargs['server_key'])
    ledger=checkout.ledger
    generations=kwargs.get('worker_generations')
    if generations is not None:
        original_bind=generations.bind_locked
        def traced_binding(lease):
            # Test-only actual-child fault witness, never key/proof/media.
            root=checkout.photos.root.parent
            if (root/'fixture-trace-binding').exists():
                (root/'fixture-binding-entered').write_text('synthetic binding entered')
            return original_bind(lease)
        generations.bind_locked=traced_binding
    lost=[kwargs['server_key']=='Mid-server-LOST-FIXTURE']
    def transport(request,timeout):
        assert request.full_url.startswith('https://api.sandbox.midtrans.com/')
        if request.method=='POST' and request.full_url.endswith('/v2/charge'):
            data=json.loads(request.data)['transaction_details']
            order,amount=data['order_id'],data['gross_amount']
            if lost[0]:
                lost[0]=False
                raise OSError('synthetic provider accepted but reply lost')
            state='pending'
        else:
            order=request.full_url.split('/')[-2]
            if kwargs['server_key']=='Mid-server-HTTP-HOLD-FIXTURE':
                root=checkout.photos.root.parent
                (root/'fixture-http-entered').write_text('synthetic HTTP thread entered')
                deadline=time.monotonic()+30
                while not (root/'fixture-http-release').exists():
                    if time.monotonic()>deadline: raise TimeoutError('synthetic held HTTP')
                    time.sleep(.02)
            with ledger.write():
                row=ledger.db.execute('SELECT i.contract_json FROM pp_payment_attempts a '
                    'JOIN pp_checkout_intents i USING(purchase_group_id) WHERE a.provider_order_id=?',
                    (order,)).fetchone()
            assert row
            amount=json.loads(row['contract_json'])['amount']
            state='settlement'
            if (checkout.photos.root.parent/'fixture-keep-pending').exists(): state='pending'
        payload=dict(status_code='201' if state=='pending' else '200',
            transaction_status=state,order_id=order,gross_amount=str(amount),currency='IDR',
            payment_type='qris',merchant_id='MTEST',fraud_status='accept',
            transaction_id='fixture_'+order,
            actions=[{'name':'generate-qr-code','method':'GET',
                'url':'https://api.sandbox.midtrans.com/v4/qris/fixture_'+order+'/qr-code'}])
        return io.BytesIO(json.dumps(payload).encode())
    kwargs['provider_transport']=transport
    delivery_fixture=kwargs['server_key']=='Mid-server-DELIVERY-FIXTURE'
    if kwargs['server_key']=='Mid-server-RECEIPT-FIXTURE' or delivery_fixture:
        import threading
        from photobooth.printer import PrinterConfig,ThermalPrinter
        root=checkout.photos.root.parent
        count=root/('fixture-output-send-count' if delivery_fixture else 'fixture-ticket-send-count')
        def send(_host,_port,_payload):
            # Only a non-secret count persists; no bitmap, bytes or proof.
            count.write_text(str((int(count.read_text()) if count.exists() else 0)+1))
            if delivery_fixture and (root/'fixture-output-uncertain-after-send').exists():
                from photobooth.printer import NetworkSendError
                raise NetworkSendError('Synthetic partial physical output')
        def no_usb(_payload):
            raise AssertionError('No USB fixture route')
        kwargs['receipt_printer']=ThermalPrinter(PrinterConfig(lan_host='fixture-printer'),
            network_sender=send,usb_sender=no_usb)
        kwargs['printer_lane']=threading.Lock()
    if delivery_fixture:
        from types import SimpleNamespace
        drive.workspace.prepare()  # Explicit isolated fixture reserve state.
        def post(_url,**request):
            body=request['json']
            assert body['action']=='bind_transaction'
            folder='syntheticChildB5_'+body['transaction_id']
            return SimpleNamespace(status_code=200,json=lambda:dict(ok=True,storage_layout=2,
                photo_number_layout=1,transaction_id=body['transaction_id'],folder_id=folder,
                folder_url='https://drive.google.com/drive/folders/'+folder,link_verified=True))
        drive.client.session=SimpleNamespace(post=post)
        kwargs['paid_delivery_enabled']=True
        kwargs['background_worker']=False  # Settlement is explicitly driven by this fixture.
    if kwargs['server_key']=='Mid-server-HTTP-HOLD-FIXTURE':kwargs['background_worker']=False
    drive.client.storage_readiness=lambda slots:{'drive_api':'READY','drive_sharing':'READY',
                                                 'capacity_state':'READY'}
    app=original(checkout,templates,bridge,drive,**kwargs)
    if delivery_fixture:
        # No external uploading in this native/process transport fixture.
        # Original worker lifetime is covered by the independent B4 tests.
        app.state.paid_delivery.worker.start=lambda:None
        app.state.paid_delivery.worker.notify_transaction=lambda _:None
    if kwargs['server_key']=='Mid-server-HOLD-FIXTURE':
        stop=app.state.lifecycle_worker.stop
        release=checkout.photos.root.parent/'fixture-release'
        app.state.lifecycle_worker.stop=lambda **args:release.is_file() and stop(**args)
    return app


if __name__=='__main__':
    with patch('photobooth.linux_credential_vault._read_key',return_value=b'k'*32), \
         patch.object(host,'build_sandbox_app',side_effect=assembled):
        raise SystemExit(bootstrap.main())
