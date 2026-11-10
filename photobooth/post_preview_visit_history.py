"""Original visit-history SQL and pre-key review; no recovery/media authority.

Reuse original finance and backend-verified ACK algorithms. Read-only review
does not migrate/create journals or publish a FREE row; post-open and original
fresh worker/provider admission checks remain independently required.
"""
from contextlib import closing
from pathlib import Path
import sqlite3
import stat

from photobooth.kiosk_v2.recovery import LaunchLease, checked_path
from photobooth.post_preview_financial_history import original_financial_class
from photobooth.post_preview_host import SandboxHostConfig, require_original_host_context
from photobooth.post_preview_sandbox_handoff import require_acked_worker_receipt_from_db
from photobooth.post_preview_store import DraftHeld, ORDER_VERSION


def require_free_visit_history(db, booth):
    """Same SQL policy in a caller-owned original transaction/read snapshot."""
    # Empty draft table alone cannot stand in for the original protected schema.
    if [tuple(r) for r in db.execute('SELECT singleton,version FROM pp_schema')] != [(1,8)]:
        raise DraftHeld('Original protected history schema required')
    for table, columns in (
            ('pp_checkout_intents','purchase_group_id,draft_id,contract_sha256'),
            ('pp_purchase_finance','purchase_group_id,entitlement_id,review_required,legitimate_paid_attempt'),
            ('pp_payment_attempts','attempt_id,purchase_group_id,payment_state,provider_ref,verified_at'),
            ('pp_ccp_credentials','purchase_group_id,offered_at'),
            ('pp_ticket_presentations','purchase_group_id,receipt_state'),
            ('pp_paid_strip_jobs','purchase_group_id,state'),
            ('pp_isolation_ops','operation_id,draft_id,booth_id,original_generation,state,financial_class,acknowledged_at'),
            ('pp_worker_retirements','operation_id,key_id,frame_json,mac,backend_verified_at')):
        db.execute('SELECT '+columns+' FROM '+table+' LIMIT 0')
    for draft in db.execute('SELECT * FROM pp_drafts').fetchall():
        if (draft['booth_id'] != booth or draft['version'] != ORDER_VERSION
                or not draft['closed'] or draft['lifecycle'] != 'ISOLATED'):
            raise DraftHeld('Original booth has an unresolved visitor')
        operation = db.execute('''SELECT * FROM pp_isolation_ops
            WHERE draft_id=? AND booth_id=? AND original_generation=? AND state='ACKED' ''',
            (draft['draft_id'], booth, draft['generation']-1)).fetchone()
        if not operation:
            raise DraftHeld('Original exact protected release required')
        require_acked_worker_receipt_from_db(db, operation)
        financial = original_financial_class(db, draft)
        if (financial != operation['financial_class'] and
                (operation['financial_class'], financial) != ('TERMINAL_UNPAID', 'PAID_OWED')):
            raise DraftHeld('Original released financial classification changed')


def _regular(path):
    path = checked_path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise DraftHeld('Original regular private history required')
    return path


def _lock_directory(root):
    root = checked_path(root)
    if {p.name for p in root.iterdir()} != {'data'}:
        raise DraftHeld('Unknown original private history')
    data = checked_path(root/'data')
    if {p.name for p in data.iterdir()} != {'kiosk-v2-launch.lock'}:
        raise DraftHeld('Unknown original private lock history')
    _regular(data/'kiosk-v2-launch.lock')


def review_before_original_worker(launcher, config):
    """Before key/spawn, under actual native and backend-owner kernel leases.

    This is a HOLD preflight only; it cannot restore old workers, create a
    release or prove global/remote/device safety. Original post-open checks stay.
    """
    try:
        if (type(launcher) is not LaunchLease or launcher.stream.closed
                or type(config) is not SandboxHostConfig
                or checked_path(Path(launcher.stream.name)) !=
                    config.private_root/'data'/'kiosk-v2-launch.lock'):
            raise DraftHeld('Exact original private-root owner required')
        root = config.private_root
        path = checked_path(root/'drafts.sqlite3')
        for suffix in ('-wal', '-shm'):
            side = checked_path(str(path)+suffix)
            if side.exists():
                _regular(side)
                if not path.exists():
                    raise DraftHeld('Original history is missing beside its journal')
        existing = path.exists()
        if not existing:
            if {p.name for p in root.iterdir()} - {'data', 'backend-owner'}:
                raise DraftHeld('Missing original protected history')
            if (root/'backend-owner').exists():
                _lock_directory(root/'backend-owner')
            # Check native directory without descending unknown customer paths.
            data = checked_path(root/'data')
            if {p.name for p in data.iterdir()} != {'kiosk-v2-launch.lock'}:
                raise DraftHeld('Unknown original native lock history')
            _regular(data/'kiosk-v2-launch.lock')
        # Independent original orphan lease. Its failure must precede mint/spawn.
        with LaunchLease(root/'backend-owner'):
            if existing:
                _regular(path)
                _regular(root/'host-context.json')
                require_original_host_context(root, config)
                with closing(sqlite3.connect(path.as_uri()+'?mode=ro', uri=True, timeout=.2)) as db:
                    db.row_factory = sqlite3.Row
                    db.execute('PRAGMA query_only=ON')
                    db.execute('BEGIN')  # Observe original WAL in the same snapshot.
                    try:
                        require_free_visit_history(db, config.booth_id)
                    finally:
                        db.rollback()
    except Exception:
        raise DraftHeld('Original pre-key history or backend owner is held') from None
