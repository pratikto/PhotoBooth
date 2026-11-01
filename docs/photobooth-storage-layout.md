# FEAT-004 + BUG-009 — customer photo storage


> **PP-04.d3 source-only addition (1 November 2026):** layout-2 `storage_readiness` inspects existing exact unclaimed READY identities, Drive API/capabilities and current Viewer ACL without reserve/bind/rename/move/share/upload/retention writes. Client validates scope and typed counts; old deployed Web App returns UNKNOWN, never a mutating fallback. Existing Web App was NOT_DEPLOYED in this work; real Google acceptance remains NOT_RUN. [Implementation evidence and limits](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-IMPLEMENTATION-CHECKPOINT.md).
> **LATEST owner-approved refund + lost-proof policy (NEW `feature/post-preview-qris-checkout`, DESIGN ONLY, 1 November 2026):** The old offline print, downloaded-photo and paid-first instructions below retain their historical/legacy scope. New purchased photo strips require a freshly verified PAID binding, exact individual customer Drive URL (verified before print), and one exclusive printer lane. The original Recovery Ticket **ALWAYS appears on screen for 30 actually visible seconds + NEXT, while the SAME original ticket prints exactly ONCE concurrently**. When paid print/Drive/media delivery is independently proven irrecoverable after bounded recovery, owner prefers an **original full refund** (or verified excess only on duplicate settlement) **if Midtrans merchant refund API is activated and a safe printer/Drive fence and original refund intent are verified**. **A genuinely offered CCP/Recovery Ticket that the customer loses is NOT an automatic refund reason**, nor grounds for tokenless private-media release; Meong's failure to offer proof or fulfill the paid service is independent and must still be remedied. Public Advertising/financial refund do not prove machine FREE. Earlier unconditional no-auto-refund/no-URL/conditional-screen rules are legacy historical scope. **112 new PP cases NOT_RUN; merchant Refund API not verified; source unchanged.**
>
> [Full no-loss decision ledger](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md) · [refund + lost-proof](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) · [security](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [112 NOT_RUN QA](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md).


## 1 November 2026 — Post-preview paid-photo addendum (design only)

**Applies to NEW purchases on `feature/post-preview-qris-checkout` only.** The existing numbered Drive tree and 25 READY folders below remain authoritative. Pre-QRIS: inspect authenticated Drive/sharing **health and unclaimed READY pool capacity** read-only; do not consume an anonymous visitor's folder, create a customer-specific share or upload unpaid photos. After independent PAID, atomically bind a numbered folder to the exact frozen paid group, verify its actual individual Viewer URL and only then produce the final paid 3-photo+real-download-QR strip. Upload may finish afterward with honest pending status. If bind/share verification unexpectedly fails after PAID, preserve **PAID/OWED**, withhold purchased-strip printing, and allow secure original-ticket/CCP remedy. **Never print a fake download QR, never expose unpaid photos, never reclaim a claimed/foreign folder.** Earlier offline print and download-pending paper rules lower in this file apply to the historic local/legacy profile, **not** this new paid-strip MVP. A stable Meong resolver QR is future scope, not implemented.

Historical 15-day local and 30-day Drive photo retention still require versioned transaction time anchors; new draft-created, original QR1-created, paid-verification, ticket-created and retention timestamps must be distinct. Exact new-order paid-retention anchor and CCP/Recovery Ticket TTL require separate validated configuration; no token or retention clock silently resets on QR renewal or restart. No actual Drive, Apps Script or deletion action is authorized by this documentation correction.

[Owner-approved master](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OWNER-APPROVED.md) · [Security/identity](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [84 NOT_RUN tests](qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md).


Updated 26 October 2026 (Asia/Jakarta) after the owner's actual Drive/QR failure.
This correction supersedes the earlier transaction-root / Photo/NN cloud tree.
The owner explicitly requires the following **Google Drive** tree:

```text
Drive root/
├── Global_Advertisement/
├── Global_Template/
└── Photobooth/
    └── PB001/
        ├── Local/Advertisement/
        ├── Local/Template/
        └── Photo/
            ├── 00000001/
            │   ├── raw/
            │   ├── bw/
            │   ├── color/
            │   └── manifest.json
            ├── 00000002/
            └── ...
```

At least 25 genuinely empty numbered reserves belong beneath each booth's
`Photo`, before claim. The raw/color/bw directories appear only after binding.
The download QR points at `Photo/00000001`, not PB001 or an asset directory.
Numbering uses the durable transaction suffix. Internal `PB001V2S2_00000001`
identities remain in private counters/claims/journals; they are not the new
Drive folder names. Never reset counters to get back to 00000001.

All sessions in one transaction share these three directories. Prefix filenames
with their stable session ID to avoid overwriting another design's files:
`raw/session_001_photo_01.jpg`, `raw/session_001_retake.jpg`,
`color/session_001_strip.png`, `bw/session_001_strip.png`.
Paper-copy quantity does not create more capture sessions or folders.
Original JPEGs stay full resolution/unmirrored, color photo areas mirror as
approved, and BW remains the exact once-dithered printer raster.

The existing private **local** workspace, manifests and upload-relative paths
are preserved for recovery. BoothDriveClient translates local
`Photo/01/color/strip.png` to remote `color/session_001_strip.png` while reusing
original checksum/size verification. This change does not relocate local data.
Complete verified global/local content caches remain per booth and offline-safe.

## QR and delivery invariants

- Never publish the booth/Photo/assets parent. Only an individual numbered
  customer folder receives Anyone with the link / Viewer.
- Reserve and bind responses must acknowledge the numbered layout and actual
  sharing verification. Python rejects older/private responses before composing
  a new QR. Previously cached unverified reserve URLs are withheld.
- Latest owner instruction, 27 October: result-screen QR appears once the
  individual assigned folder/link is verified, including before file upload.
  QR visibility does not mark bytes uploaded. Pending/retry notices remain;
  checking back in 30 minutes is a suggestion, not a guaranteed deadline.
  For **historical/local/legacy profiles**, automatic physical printing remains independent of network availability. New post-preview purchased strips are **blocked until the exact customer download URL is verified**, even when a previously approved local photo capture was offline.
- One folder belongs to one transaction. Ready/claimed ledger checks reject
  duplicate folders across batches and replacements; bindings persist the same
  claim/folder mapping before publishing the manifest. Existing manifest ownership
  also rejects reuse. The manifest maps exact local upload paths to this folder;
  claimed IDs/folders never return to READY, including after retention/restart.
- For historical/legacy profiles, a missing folder URL may produce download-pending paper, never a fabricated QR. For **new paid post-preview orders**, missing/unverified customer URL means **no purchased-strip print**, while PAID/OWED and safe claim remain durable.
  Existing printed pixels are never rewritten and prints are never replayed.
- Binding/setup failures persist a safe error category for the result GUI;
  retention failures retain the existing upload hold and operator message.

## Recovery and retention

The backend can recover an **exact claimed, empty, app-owned** legacy reserve
from the same booth parent into Photo and rename it to its numeric suffix.
The claim digest must match. Folder ID and any printed QR URL remain identical.
A retry after interrupted move/rename finds the same folder. Foreign, ambiguous,
nonempty or mismatched folders stop for operator review. No broad migration,
archive scan, automatic deletion or unrelated asset cleanup is performed.

The 15-day local and 30-day Drive deadlines remain based on the original
transaction time. Numbered-cloud cleanup validates the stored internal identity,
physical booth, numeric suffix and exact retention marker before deletion;
READY reserves and unrelated content have no valid expiry authorization.
BUG-009 remains OPEN until installed-account expiry evidence is supplied.

`old` is excluded before descent from every inspection/sync/cleanup. V1 and
merchant Sandbox retain their existing profiles. Global/Local content behavior,
payment, printer transport and game behavior are outside this correction.

## Source versus live account

The 26 October read-only Meong Drive inspection found
`Photobooth/PB001/PB001V2S2_00000003` empty, with no anyone-reader permission;
PB001 also contained Photo plus legacy/local asset naming variants. No contents
of old were read. No live folders, permissions or scripts were changed.

The corrected source and fixture tests do not update an existing Apps Script
Web App deployment. Follow [repair setup](qa/drive-photo-layout/README.md).
Do not mark live upload/phone scanning or actual cloud deletion PASS from source tests.
