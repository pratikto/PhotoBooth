"""Windows-first private settings under actual original global ownership."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photobooth.checkout_store import CheckoutStore
from photobooth.post_preview_launch import ProtectedSandboxLaunch,ProtectedLaunchHeld
from photobooth.post_preview_launch_settings import load_settings


class ProtectedLaunchSettingsTests(unittest.TestCase):
    @contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{},clear=True):
            root=Path(directory);(root/'photobooth').mkdir()
            local=root/'photobooth'/'local_settings.py'
            local.write_text("MIDTRANS_SANDBOX_MERCHANT_ID='MTEST'\nMIDTRANS_SANDBOX_SERVER_KEY='Mid-server-SETTINGS-FIXTURE'\nWEB_APP_URL='https://script.google.com/macros/s/SETTINGS_FIXTURE/exec'\nUPLOAD_TOKEN='synthetic-settings-token'\nraise AssertionError('Settings must never execute')\n")
            history=root/'data'/'kiosk-v2-sandbox'/'MTEST'/'PB001'/'orders.sqlite'
            CheckoutStore(history).close()
            (history.parent/'visit.json').write_text(json.dumps({'version':1,'phase':'CANCELLED'}))
            (root/'data'/'printer_settings.json').write_text(json.dumps({'windows_printer_name':'Fixture POS80'}))
            owner=ProtectedSandboxLaunch(root)
            try:yield owner,root,local,history
            finally:self.assertTrue(owner.stop(timeout=1))

    def load(self,owner,root):return load_settings(owner,storage_root=root/'protected',booth_id='PB001')

    def test_original_literal_fields_not_executed_and_canonical_history_preserved(self):
        with self.fixture() as (owner,root,local,history):
            before=hashlib.sha256(history.read_bytes()).hexdigest()
            result=self.load(owner,root)
            self.assertEqual('MTEST',result.config.merchant_id)
            self.assertEqual(history,result.legacy_path)
            self.assertEqual('Fixture POS80',result.printer_config.windows_printer_name)
            self.assertEqual(before,hashlib.sha256(history.read_bytes()).hexdigest())
            self.assertFalse((root/'protected').exists())
            self.assertNotIn(result.config.server_key,repr(result))
            self.assertNotIn(result.config.drive_token,repr(result))
            self.assertIsNone(owner._visits);self.assertIsNone(owner._camera)

    def test_active_global_owner_required_before_reading_private_file(self):
        with self.fixture() as (owner,root,local,history):
            owner.stop(timeout=0)
            with patch.object(Path,'read_text',side_effect=AssertionError('No private read')):
                with self.assertRaises(ProtectedLaunchHeld):self.load(owner,root)

    def test_partial_environment_pairs_never_mix_with_local_accounts(self):
        for name in ('MIDTRANS_MERCHANT_ID','MIDTRANS_SERVER_KEY','PHOTOBOOTH_WEB_APP_URL','PHOTOBOOTH_UPLOAD_TOKEN'):
            with self.subTest(field=name),self.fixture() as (owner,root,local,history):
                os.environ[name]='private-invalid-override'
                with self.assertRaises(ProtectedLaunchHeld) as result:self.load(owner,root)
                self.assertNotIn('private-invalid-override',str(result.exception))

    def test_complete_environment_pairs_reuse_same_account_and_generate_no_persistent_token(self):
        with self.fixture() as (owner,root,local,history):
            os.environ.update(MIDTRANS_MERCHANT_ID='MTEST',MIDTRANS_SERVER_KEY='Mid-server-ENV-FIXTURE',
                PHOTOBOOTH_WEB_APP_URL='https://script.google.com/macros/s/ENV_FIXTURE/exec',
                PHOTOBOOTH_UPLOAD_TOKEN='synthetic-env-token')
            first=self.load(owner,root);second=self.load(owner,root)
            self.assertEqual('Mid-server-ENV-FIXTURE',first.config.server_key)
            self.assertEqual('synthetic-env-token',first.config.drive_token)
            self.assertNotEqual(first.config.booth_token,second.config.booth_token)
            self.assertFalse((root/'protected').exists())

    def test_absent_canonical_history_cannot_fall_back_to_another_empty_ledger(self):
        with self.fixture() as (owner,root,local,history):
            history.rename(history.with_suffix('.preserved'))
            CheckoutStore(root/'convenient.sqlite3').close()
            with self.assertRaises(ProtectedLaunchHeld):self.load(owner,root)
            self.assertFalse(history.exists());self.assertTrue(history.with_suffix('.preserved').exists())

    def test_unresolved_original_journal_and_older_v1_history_hold(self):
        for kind in ('pending','v1'):
            with self.subTest(kind=kind),self.fixture() as (owner,root,local,history):
                if kind=='pending':
                    (history.parent/'visit.json').write_text(json.dumps({'version':1,'phase':'WAITING'}))
                else:(root/'data'/'qris-sandbox-trial'/'MTEST'/'PB001').mkdir(parents=True)
                with self.assertRaises(ProtectedLaunchHeld):self.load(owner,root)
                self.assertIsNone(owner._camera)

    def test_terminal_looking_journal_cannot_hide_an_active_original_legacy_order(self):
        with self.fixture() as (owner,root,local,history):
            store=CheckoutStore(history)
            try:store.begin('PB001',{'template_a':1},10000,'original-settings-key-0001')
            finally:store.close()
            before=hashlib.sha256(history.read_bytes()).hexdigest()
            with self.assertRaises(ProtectedLaunchHeld):self.load(owner,root)
            self.assertEqual(before,hashlib.sha256(history.read_bytes()).hexdigest())

    def test_shared_legacy_policy_preserves_paid_owed_and_requires_exact_release_fence(self):
        from tests import test_checkout_release as legacy
        from photobooth.post_preview_legacy_history import legacy_history_clear
        fixture=legacy.ReleaseTests(methodName='runTest');fixture.setUp()
        try:
            self.assertFalse(legacy_history_clear(fixture.store.db,'PB001'))
            fixture.prepare();self.assertFalse(legacy_history_clear(fixture.store.db,'PB001'))
            fixture.ack();self.assertTrue(legacy_history_clear(fixture.store.db,'PB001'))
            self.assertEqual('OWED',fixture.store.fulfillment(fixture.oid,'PB001')['obligation_state'])
            fixture.store.db.execute('UPDATE checkout_service_fences SET generation=generation+1 WHERE order_id=?',
                                     (fixture.oid,))
            self.assertFalse(legacy_history_clear(fixture.store.db,'PB001'))
        finally:fixture.doCleanups()

    def test_no_implicit_linux_usb_route_or_placeholders(self):
        for kind in ('printer','drive'):
            with self.subTest(kind=kind),self.fixture() as (owner,root,local,history):
                if kind=='printer':(root/'data'/'printer_settings.json').unlink()
                else:local.write_text(local.read_text().replace('synthetic-settings-token','PASTE_TOKEN'))
                with self.assertRaises(ProtectedLaunchHeld):self.load(owner,root)

    def test_invalid_archive_storage_and_nonliteral_settings_fail_redacted(self):
        with self.fixture() as (owner,root,local,history):
            with self.assertRaises(ProtectedLaunchHeld):
                load_settings(owner,storage_root=root/'old'/'data',booth_id='PB001')
            local.write_text("MIDTRANS_SANDBOX_MERCHANT_ID = private_function()\n")
            with self.assertRaises(ProtectedLaunchHeld) as result:self.load(owner,root)
            self.assertNotIn('private_function',str(result.exception))


if __name__=='__main__':unittest.main()
