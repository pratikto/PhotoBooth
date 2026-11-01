"""Post-preview original PAID upload completion, never premature legacy success."""
import unittest
from photobooth.drive_sync import _refresh_upload_status


class PostPreviewPaidUploadStatusTests(unittest.TestCase):
    def paid(self, **updates):
        m={'purpose':'POST_PREVIEW_PAID',
           'status':'READY_FOR_PAID_DELIVERY',
           'paid_media_import_ready':True,
           'drive_binding_verified':True,
           'photo_number_layout':1,
           'drive_intent':True,
           'drive_folder_id':'verifiedFolder',
           'upload_files':{'Photo/01/raw/photo_01.jpg':{'status':'VERIFIED'},
                           'Photo/01/color/strip.png':{'status':'VERIFIED'}}}
        m.update(updates)
        return m

    def test_exact_ready_paid_folder_becomes_upload_complete(self):
        m=self.paid()
        _refresh_upload_status(m)
        self.assertEqual('UPLOAD_COMPLETE',m['upload_status'])

    def test_missing_any_verified_file_remains_pending(self):
        m=self.paid()
        m['upload_files']['Photo/01/color/strip.png']['status']='PENDING_UPLOAD'
        _refresh_upload_status(m)
        self.assertEqual('PENDING_UPLOAD',m['upload_status'])

    def test_not_prepared_paid_transaction_never_becomes_complete(self):
        for change in (
            {'paid_media_import_ready':False},
            {'drive_binding_verified':False},
            {'photo_number_layout':2},
            {'status':'IN_PROGRESS'},
            {'purpose':'PORTRAIT_V2_PHOTO_TEST'}):
            with self.subTest(change=change):
                m=self.paid(**change)
                _refresh_upload_status(m)
                self.assertEqual('PENDING_UPLOAD',m['upload_status'])

    def test_existing_completed_legacy_transaction_remains_complete(self):
        m=self.paid(purpose='PORTRAIT_V2_PHOTO_TEST',status='COMPLETED')
        _refresh_upload_status(m)
        self.assertEqual('UPLOAD_COMPLETE',m['upload_status'])

    def test_action_required_never_becomes_complete(self):
        m=self.paid()
        m['upload_files']['Photo/01/raw/photo_01.jpg']['status']='ACTION_REQUIRED'
        _refresh_upload_status(m)
        self.assertEqual('ACTION_REQUIRED',m['upload_status'])


if __name__=='__main__':
    unittest.main()
