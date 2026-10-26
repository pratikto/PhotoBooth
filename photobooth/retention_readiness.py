"""Redacted, read-only BUG-009 diagnostics using the original Apps Script client."""

from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError
from photobooth.kiosk_v2.readiness import inventory


HINTS = {
    'READY': 'Activation observed. Test authorized synthetic expiry; this is not proof of deletion.',
    'NOT_CONFIGURED': 'Use the existing v1 Apps Script URL/token locally. Direct OAuth alone has no independent cloud timer.',
    'LOCAL_CONFIGURATION_INVALID': 'Check the existing local Apps Script configuration; do not paste credentials into a report.',
    'WEB_APP_UPDATE_REQUIRED': 'Update Code.gs in the existing project, run setup, then deploy a new version at the same /exec URL.',
    'CONFIGURATION_REQUIRED': 'Check DRIVE_FOLDER_ID in the existing project Script Properties.',
    'SETUP_REQUIRED': 'Run setupPhotoRetention in the existing Apps Script editor, authorize, then redeploy.',
    'TRIGGER_MISSING': 'Run setupPhotoRetention as the Web App owner; verify one hourly cleanupPhotoRetention trigger.',
    'DUPLICATE_TRIGGERS': 'Run the existing setup once as the Web App owner to retain one cleanup clock.',
    'TRIGGER_ACCESS_REQUIRED': 'Authorize trigger access and run setup as the account executing the Web App.',
    'DRIVE_API_UNAVAILABLE': 'Enable Drive API v3 and verify the deploying account can read the configured photo parent.',
    'DRIVE_PARENT_INVALID': 'DRIVE_FOLDER_ID must identify the dedicated photo folder, separate from ad media.',
    'AUTHENTICATION_FAILED': 'Compare the existing local UPLOAD_TOKEN with the project Script Property locally.',
    'WEB_APP_ACCESS_REQUIRED': 'Check existing deployment access and executing-account authorization.',
    'NETWORK_UNAVAILABLE': 'Check connectivity or retry later. No cleanup or setup was attempted.',
    'CHECK_FAILED': 'The diagnostic could not verify status. Inspect setup/deployment locally; no raw errors are exported.',
}


def check(root, *, client_factory=None, storage_layout=1):
    """Perform one authenticated status request, never pool/registration/cleanup."""
    report = inventory(root)
    state, status = 'CHECK_FAILED', None
    try:
        factory = client_factory or AppsScriptDriveClient.from_configuration
        try:
            client = factory()
        except (ValueError, TypeError, ImportError):
            state = 'LOCAL_CONFIGURATION_INVALID'
        else:
            if client is None:
                state = 'NOT_CONFIGURED'
            else:
                if storage_layout == 2:
                    from photobooth.booth_sync import BoothDriveClient
                    from photobooth.kiosk_v2.photos import configured_workspace
                    client = BoothDriveClient(client, configured_workspace(root).booth_id)
                status = client.retention_status()
                state = status['state']
    except DriveApiError as error:
        # Backend/network messages may contain account identifiers. Export codes only.
        state = ('AUTHENTICATION_FAILED' if error.status_code == 401 else
                 'WEB_APP_ACCESS_REQUIRED' if error.status_code == 403 else
                 'WEB_APP_UPDATE_REQUIRED' if error.status_code in {400, 404, 409} else
                 'NETWORK_UNAVAILABLE' if error.transient else 'CHECK_FAILED')
    except Exception:
        state = 'CHECK_FAILED'
    report['kind'] = 'drive-retention-readiness'
    report['storage_layout'] = storage_layout
    report['drive_retention'] = {
        'state': state, 'next_action': HINTS[state], 'backend': status,
        'read_only': True, 'cloud_deletion_verified': False,
    }
    report['notes'].extend([
        'Only the configured Apps Script retention_status action may contact the network.',
        'Status reads parent metadata/owning-account clock presence, never customer photo bytes.',
        'No setup, deploy, trigger write, registration, upload or deletion was requested.',
        'A clock exists does not prove its interval, future success or permanent deletion.',
    ])
    # The inherited P5 statement describes inventory only; this command also probes status.
    report['notes'][0] = 'Device inventory is read-only; the separate retention status probe is described below.'
    return report
