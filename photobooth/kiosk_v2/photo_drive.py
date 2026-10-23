"""Isolated P3 Drive worker: require retention acknowledgement before upload."""

import json

from photobooth.drive_sync import DriveSyncWorker, sync_manifest
from photobooth.retention import register_drive_retention
from .photos import PURPOSE


class RetentionGuardedSync(DriveSyncWorker):
    def _process_pending_uploads(self):
        for path in self.photos_root.glob('*/manifest.json'):
            if self._stop.is_set():
                return
            try:
                manifest = json.loads(path.read_text(encoding='utf-8'))
                if (manifest.get('purpose') != PURPOSE or not manifest.get('drive_folder_id') or
                        manifest.get('upload_status') in {'UPLOAD_COMPLETE', 'LOCAL_ONLY',
                                                       'LOCAL_EXPIRED', 'ACTION_REQUIRED'}):
                    continue
                register_drive_retention(path, self.client)
                manifest = json.loads(path.read_text(encoding='utf-8'))
                if manifest.get('drive_retention_registered_at'):
                    sync_manifest(path, self.client)
            except (OSError, ValueError, TypeError, RuntimeError):
                # Durable existing queue retains errors/offline progress for the next pass.
                continue
