"""AR-05 exact frozen photo progress, no media disclosure without resume permit."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
from photobooth.catalog import get_templates
from photobooth.kiosk_v2.photos import PhotoTest
import tests.test_photo_allocation as allocation_fixture


class PhotoReconstructionTests(unittest.TestCase):
    # Reuse the existing synthetic backend/immutable binding fixture.
    def setUp(self):
        allocation_fixture.BoundPhotoTests.setUp(self)
    def original(self):
        photo=PhotoTest(self.root/'photos');self.addCleanup(photo.close)
        photo.start_bound(get_templates(),self.quantities,self.binding)
        return photo

    def permit(self):
        from photobooth.resume_authority import trusted_resume_permit
        return trusted_resume_permit(self.binding)

    def test_partial_three_capture_states_restore_exact_count_without_new_ids(self):
        for count in (1,2,3):
            with self.subTest(count=count):
                photo=self.original() if count==1 else self.current
                photo.capture(np.zeros((24,32,3),dtype=np.uint8))
                self.current=photo
                resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
                view=resumed.restore(get_templates(),self.binding,self.permit())
                self.assertEqual(view['captured'],count)
                self.assertEqual(view['phase'],'review' if count==3 else 'capture')
                self.assertEqual(view['transaction_id'],self.binding['transaction_id'])
                self.assertFalse(resumed.store.state_path.exists())

    def test_no_permit_inspection_reveals_no_pixels_and_restore_rejects(self):
        photo=self.original();photo.capture(np.zeros((24,32,3),dtype=np.uint8))
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        observation=resumed.inspect_resume(get_templates(),self.binding)
        self.assertNotIn('thumbnails',observation);self.assertNotIn('strip',observation)
        with self.assertRaises(RuntimeError):resumed.restore(get_templates(),self.binding,None)
        self.assertIsNone(resumed.transaction)

    def test_retake_selected_and_used_restore_without_renewing_quota(self):
        photo=self.original();frame=np.zeros((24,32,3),dtype=np.uint8)
        for _ in range(3):photo.capture(frame)
        photo.retake(1)
        pending=PhotoTest(self.root/'photos');self.addCleanup(pending.close)
        view=pending.restore(get_templates(),self.binding,self.permit())
        self.assertEqual(view['phase'],'capture');self.assertTrue(view['retake'])
        pending.capture(frame)
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        view=resumed.restore(get_templates(),self.binding,self.permit())
        self.assertTrue(view['retake_used']);self.assertEqual(view['phase'],'review')
        self.assertEqual(resumed.session.retake_target_index,1)
        with self.assertRaises(ValueError):resumed.retake(0)

    def test_published_capture_is_adopted_only_by_matching_hash_without_new_frame(self):
        photo=self.original()
        def stop(stage):
            if stage=='published':raise RuntimeError('synthetic crash')
        with patch('photobooth.capture_journal.boundary',side_effect=stop):
            with self.assertRaises(RuntimeError):photo.capture(np.zeros((24,32,3),dtype=np.uint8))
        path=photo.transaction.folder_path/'raw/session_001/photo_01.jpg';before=path.read_bytes()
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        view=resumed.restore(get_templates(),self.binding,self.permit())
        self.assertEqual(view['captured'],1);self.assertEqual(path.read_bytes(),before)

    def test_published_output_reuses_saved_pixels_without_renderer_or_print(self):
        photo=self.original()
        for _ in range(3):photo.capture(np.zeros((24,32,3),dtype=np.uint8))
        def stop(stage):
            if stage=='output_published':raise RuntimeError('synthetic crash')
        with patch('photobooth.capture_journal.boundary',side_effect=stop):
            with self.assertRaises(RuntimeError):photo.compose()
        output=photo.store.output_path(photo.transaction,photo.session.plan);before=output.read_bytes()
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        with patch('photobooth.kiosk_v2.photos.compose_result',side_effect=AssertionError('No rerender')):
            view=resumed.restore(get_templates(),self.binding,self.permit())
        self.assertEqual(view['phase'],'result');self.assertEqual(output.read_bytes(),before)
        self.assertEqual(view['print_state'],'NOT_SENT')

    def test_corrupt_media_or_wrong_binding_stays_held_without_data_rewrite(self):
        photo=self.original();photo.capture(np.zeros((24,32,3),dtype=np.uint8))
        path=photo.session.initial_photo_paths[0];path.write_bytes(b'corrupt')
        before=photo.transaction.manifest_path.read_bytes()
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        with self.assertRaises(RuntimeError):resumed.restore(get_templates(),self.binding,self.permit())
        self.assertEqual(photo.transaction.manifest_path.read_bytes(),before)
        self.assertEqual(path.read_bytes(),b'corrupt')

    def test_multiple_designs_resume_only_unfinished_design_and_original_copies(self):
        self.store.recovery_action(self.binding['order_id'],'PB001','c'*32,'abandon','Isolated fixture cart',None,'operator')
        self.quantities={'template_a':2,'template_b':1}
        oid=self.backend.create_order('PB001',self.quantities,'d'*32)['order_id']
        self.provider.rows[oid].update(transaction_status='settlement',status_code='200')
        self.backend._apply(self.store.get(oid),self.provider.get_status(oid))
        grant=self.backend.claim(oid,'PB001','d'*32)['grant_id']
        result=self.backend.allocate(oid,'PB001',grant,'e'*32)
        allocation=result['fulfillment']
        self.binding={k:allocation[k] for k in ('fulfillment_id','transaction_id','allocation_operation_id','contract_hash','booth_id','merchant_id')}
        self.binding.update(order_id=oid,grant_id=grant)
        photo=self.original();frame=np.zeros((24,32,3),dtype=np.uint8)
        for _ in range(3):photo.capture(frame)
        photo.compose();output=photo.session.output_path;before=output.read_bytes()
        photo.next();photo.capture(frame)
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        view=resumed.restore(get_templates(),self.binding,self.permit())
        self.assertEqual((view['session_number'],view['copies'],view['captured']),(2,1,1))
        self.assertEqual(output.read_bytes(),before)
        self.assertEqual(resumed.sessions[0].plan.print_copies,2)

    def test_intent_without_saved_bytes_requires_new_customer_capture_without_losing_audit(self):
        photo=self.original()
        def stop(stage):
            if stage=='intent':raise RuntimeError('synthetic crash')
        with patch('photobooth.capture_journal.boundary',side_effect=stop):
            with self.assertRaises(RuntimeError):photo.capture(np.zeros((24,32,3),dtype=np.uint8))
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        view=resumed.restore(get_templates(),self.binding,self.permit())
        self.assertEqual(view['captured'],0)
        resumed.capture(np.zeros((24,32,3),dtype=np.uint8))
        intents=json.loads(resumed.transaction.manifest_path.read_text())['capture_intents']
        self.assertEqual(len(intents),2)
        self.assertEqual(sorted(i['state'] for i in intents.values()),['COMMITTED','VOID_BEFORE_FRAME'])

    def test_resume_permit_is_bound_single_use_and_expires_in_memory(self):
        from photobooth.resume_authority import trusted_resume_permit
        self.original()
        now=[100.0];permit=trusted_resume_permit(self.binding,now=lambda:now[0])
        now[0]+=61
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        with self.assertRaises(RuntimeError):resumed.restore(get_templates(),self.binding,permit)
        fresh=self.permit();resumed.restore(get_templates(),self.binding,fresh)
        other=PhotoTest(self.root/'photos');self.addCleanup(other.close)
        with self.assertRaises(RuntimeError):other.restore(get_templates(),self.binding,fresh)

    def test_privacy_lock_hides_pixels_and_requires_new_permit_for_same_session(self):
        photo=self.original();photo.capture(np.zeros((24,32,3),dtype=np.uint8))
        before=photo.transaction.manifest_path.read_bytes()
        photo.hide_private()
        self.assertEqual(photo.snapshot(),{'phase':'claim_required'})
        self.assertEqual(photo.transaction.manifest_path.read_bytes(),before)
        with self.assertRaises(RuntimeError):photo.restore(get_templates(),self.binding,None)
        view=photo.restore(get_templates(),self.binding,self.permit())
        self.assertEqual(view['captured'],1)
        self.assertEqual(len(view['thumbnails']),1)

    def test_lock_during_reconstruction_cannot_publish_private_view(self):
        from photobooth.kiosk_v2.photo_recovery import reconstruct
        photo=self.original();photo.capture(np.zeros((24,32,3),dtype=np.uint8));photo.hide_private()
        def locked(*args,**kwargs):
            value=reconstruct(*args,**kwargs);photo.hide_private();return value
        with patch('photobooth.kiosk_v2.photo_recovery.reconstruct',side_effect=locked):
            with self.assertRaises(RuntimeError):photo.restore(get_templates(),self.binding,self.permit())
        self.assertEqual(photo.snapshot(),{'phase':'claim_required'})

    def test_original_reserved_allocation_before_first_manifest_can_initialize_only_same_id(self):
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        view=resumed.restore_allocated(get_templates(),self.quantities,self.binding,self.permit(),'RESERVED')
        self.assertEqual(view['transaction_id'],self.binding['transaction_id'])
        self.assertEqual(view['captured'],0)
        self.assertEqual(resumed.transaction.manifest['payment_binding'],self.binding)
        self.assertFalse(resumed.store.state_path.exists())

    def test_started_missing_manifest_or_unknown_bytes_never_restarts_capture(self):
        resumed=PhotoTest(self.root/'photos');self.addCleanup(resumed.close)
        with self.assertRaises(RuntimeError):
            resumed.restore_allocated(get_templates(),self.quantities,self.binding,self.permit(),'STARTED')
        folder=resumed.store.photos_root/self.binding['transaction_id'];folder.mkdir(parents=True)
        unknown=folder/'unknown.bin';unknown.write_bytes(b'synthetic orphan')
        with self.assertRaises(RuntimeError):
            resumed.restore_allocated(get_templates(),self.quantities,self.binding,self.permit(),'RESERVED')
        self.assertEqual(unknown.read_bytes(),b'synthetic orphan')
        self.assertFalse((folder/'manifest.json').exists())
