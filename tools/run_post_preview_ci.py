"""Complete post-preview CI registry; bounded Windows shards omit no methods.

Ubuntu runs all. Windows runs disjoint core/delivery jobs under the original
15-minute budget. Both retain the original fd-safe unittest runner/exit status.
"""
import argparse
from pathlib import Path
import sys

CORE_MODULES=(
    'test_kiosk_unittest_progress',
    'test_post_preview_store',
    'test_post_preview_photos',
    'test_post_preview_checkout',
    'test_post_preview_freeze',
    'test_post_preview_freeze_backend',
    'test_post_preview_resources',
    'test_post_preview_worker',
    'test_post_preview_idle',
    'test_credential_vault',
    'test_post_preview_worker_custody',
    'test_post_preview_process_identity',
    'test_post_preview_worker_escrow',
    'test_post_preview_worker_start',
    'test_post_preview_ccp',
    'test_post_preview_payments',
    'test_post_preview_api',
    'test_post_preview_host',
    'test_post_preview_host_fulfillment',
    'test_post_preview_sandbox_visits',
    'test_post_preview_visit_control',
    'test_post_preview_launch',
    'test_post_preview_launch_settings',
    'test_post_preview_acceptance',
    'test_post_preview_enrollment',
    'test_post_preview_graceful_exit',
    'test_post_preview_windows_entry',
    'test_qris_sandbox_launcher',
    'test_post_preview_presentation',
    'test_post_preview_ticket_presentation',
    'test_post_preview_remote_receipt',
    'test_post_preview_payment_crashes',
    'test_post_preview_process_crash',
    'test_post_preview_protected_restore',
    'test_post_preview_checkout_worker',
    'test_post_preview_lifecycle_worker',
    'test_post_preview_readiness',
)

DELIVERY_MODULES=(
    'test_post_preview_worker_fence',
    'test_post_preview_sandbox_handoff',
    'test_post_preview_claim_requests',
    'test_post_preview_handoff_api',
    'test_post_preview_handoff_client',
    'test_post_preview_drive_readiness',
    'test_post_preview_paid_drive',
    'test_post_preview_sandbox_delivery',
    'test_post_preview_sandbox_delivery_api',
    'test_post_preview_protected_checkout',
    'test_post_preview_paid_media',
    'test_post_preview_paid_strips',
    'test_post_preview_paid_print',
    'test_post_preview_paid_upload_status',
    'test_post_preview_paid_delivery',
    'test_post_preview_checkout_delivery',
    'test_post_preview_journey_matrix',
    'test_post_preview_pilot_launcher',
    'test_post_preview_pilot_preflight',
    'test_post_preview_device_entry',
    'test_post_preview_pilot_early_root',
    'test_post_preview_isolation',
    'test_post_preview_pilot_admission',
    'test_post_preview_refund_assessment',
    'test_post_preview_refund_simulation',
    'test_post_preview_claim',
    'test_post_preview_authority',
    'test_post_preview_ticket',
    'test_post_preview_ticket_receipt',
    'test_post_preview_ticket_window',
    'test_post_preview_checkout_ticket',
    'test_booth_sync',
    'test_booth_storage',
    'test_apps_script_drive',
    'test_retention_readiness',
    'test_checkout_backend',
    'test_checkout_durability',
    'test_payment_quote',
    'test_workflow',
    'test_capture_journal',
    'test_photo_reconstruction',
)

ALL_MODULES=CORE_MODULES+DELIVERY_MODULES

# Preserve ALL's original execution order; rebalance only Windows shards.
# Sourcef4b8c07 delivery reached15min while advancing. Its measured215s journey
# and37s handoff client fit the lighter core job; no methods/fsync/budget waived.
_WINDOWS_TRANSFER=('test_post_preview_journey_matrix','test_post_preview_handoff_client')
CORE_MODULES=CORE_MODULES+_WINDOWS_TRANSFER
DELIVERY_MODULES=tuple(name for name in DELIVERY_MODULES if name not in _WINDOWS_TRANSFER)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('suite',choices=('all','core','delivery'))
    suite=parser.parse_args(argv).suite
    # Preserve normal script/import context for the existing original runner.
    tools_root=str(Path(__file__).resolve().parent)
    if tools_root not in sys.path:sys.path.insert(0,tools_root)
    from run_kiosk_unittests import main as run
    modules={'all':ALL_MODULES,'core':CORE_MODULES,'delivery':DELIVERY_MODULES}[suite]
    return run(list(modules))


if __name__=='__main__':raise SystemExit(main())
