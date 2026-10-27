# Meong Photobooth — product and technical decisions

## Owner saved Sandbox credentials request — 28 October 2026

The owner explicitly requests persisting Merchant ID and Server Key locally,
for example beside Drive settings in ignored `photobooth/local_settings.py`.
This supersedes the earlier prompt/environment-only source restriction. Reuse
the ignored file with separate Sandbox-specific fields; no private values are
written/published by this source change. Preserve backend-only credential
forwarding, fixed Sandbox transport and existing payment/Drive state.
[Implementation and source precedence](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).

## Latest owner delivery instruction — 27 October 2026

Owner authorizes implementation of holding old retries, reserves and content
while customer uploads run, FIFO across waiting sessions and bounded failure
release. A subsequent explicit correction requests the real download QR before
upload success, superseding the former UPLOAD_COMPLETE screen-QR rule. Every
customer keeps a distinct immutable folder and a durable local-file mapping.
The UI suggests checking again in 30 minutes; no unverified upload deadline is
guaranteed. [Contract and evidence](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md).

Owner accepts the 27 October recommendation to isolate old failed delivery
retries and add specific safe bind diagnostics. This scope preserves claims,
folder identity and retention; no automatic repair/deletion or batch-upload
protocol is authorized. [Retry continuation](qa/drive-delivery-performance/RETRY.md).

## Owner delivery-performance continuation — 27 October 2026

Owner approves same-branch investigation/implementation/tests/documentation and
staged pushes for Google Drive latency and v2 responsiveness. Subsequently asks
to inspect v1's faster link generation, with no blind port. V1 publishes a real
folder URL before upload completion; v2 keeps the stricter UPLOAD_COMPLETE screen
QR contract, while the strip may use an earlier verified real folder. Preserve
operator-disabled printing, original clocks/claims/checksums/durable queues and
numbered cloud layout. No live Apps Script deployment/cloud deletion is authorized.
[Implementation, limits, comparison and update guide](qa/drive-delivery-performance/README.md).

## Owner working rule and platform — 27 October 2026

Documentation review must be thorough/comprehensive/careful before code changes;
documentation updates follow code. This is the primary rule, persisted in
AGENTS, protocol and continuation prompt. Development runs on Windows; deployment
will use an Ubuntu mini PC. Preserve Windows support and provide target-specific
Ubuntu startup guidance without claiming actual Ubuntu device acceptance.
The next roadmap request continues FEAT-009 with a read-only recovery gate,
per-checkout launch ownership and generated Ubuntu user service. No automatic
restart, replay, service installation or production deployment follows.

## Owner correction — customer Drive folders (26 October 2026)

The owner explicitly clarifies PB001/Photo/00000001/{raw,bw,color}; internal transaction IDs are not customer Drive folder names. This supersedes the previous cloud tree. Preserve local state, QR folder IDs and no print replay.


Updated **26 October 2026**. Decisions establish product direction and scope;
[current status](FEATURE_STATUS.md) and [test ledger](test_checklist.md) establish
implementation/evidence. Preserve historical IDs and separate later authorization
from the original decision. A design decision alone does not authorize new code.

## DEC-023 — GUI v2 development focus and intended primary branch

The owner directs continued development on **`feature/portrait-kiosk-v2-next`**,
with reference to working features on other branches, and intends GUI v2 to
become the primary branch. GitHub default remains `master`; `main.py` remains v1.
No new branch/restart/default change/rename/merge/release/deployment follows from
this direction. [Reference audit](gui-v2-branch-audit.md) · [transition plan](gui-v2-promotion-plan.md).

The owner explicitly approved P3, P4 DEMO/MOCK and then P4b Sandbox/P5 with manual
tests at the end. On 25 October the owner authorized safe source continuation
while laptop checks wait, reusing the actual v1 implementation. The bounded
read-only Device Health/local report increment is now in source. Selection,
production, trusted merchant promotion and repository operations stay separate.
[Operator scope/proof](qa/portrait-v2-operator-health/README.md).

Reuse working UI/controllers/renderers/assets as well as logic; refresh reference
SHA and record concrete adapter exceptions. Avoid redundant successful GUI CI for
documentation. This documentation request authorizes reconciliation in English;
it adds no new application feature approval. [AGENTS.md](../AGENTS.md).

## Product decisions

**Owner storage target, 26 October:** ignore the entire `old` archive without
inspection/change. Requested new data layout is `Photobooth/PB001...PB00X`,
booth-specific assets, at least 25 empty transaction reserves and
`PB001/Photo/00000001/{raw,bw,color}` in Drive (26 October correction). Root `Global_Advertisement` and `Global_Template` are
shared sources with complete offline copies in every booth. The
[audit/target contract](photobooth-storage-layout.md) records current gaps and
reuse; it does not claim implementation or an actual Drive cutover. The owner
selected continued local photo/print if Drive/25 reserves are unavailable, with
upload and QR deferred until online; this requires explicit deferred-binding
state, not silently uploading previously local-only visits. Asset-priority
recommendations are labelled separately.

The owner explicitly links this target to **FEAT-004 ads + BUG-009**. Treat
foldering, global/local caches and photo-retention integration as coordinated
work. Preserve separate source/device/cloud evidence and keep BUG-009 OPEN
until its real deletion gate is verified; do not call the linkage implemented.

**Owner BUG-009 continuation, 26 October:** resume bounded photo-retention
remediation; setup and redeployment have not been confirmed. This supersedes
the earlier deferral for this bug, without starting FEAT-004 advertising sync.
Reuse v1 setup/cleanup/client/configuration, preserve immutable deadlines and
v2 upload holds. Prepare tested source/diagnostics and a concrete activation
guide; installed-account changes/deletion evidence remain separate from source
verification. [Current repair](qa/bug-009-retention/README.md).

**Owner print/Drive priority, 25 October:** after BUG-018's 4/4 monitoring retest,
the owner redirected the next development to these two features only and chose
automatic print after approving photos (v1 behavior), with Drive in background.
Use existing clients/configuration/queues/QR, explicit ordinary-launcher opt-ins,
durable one-batch/uncertainty guards and verified delivery. Watchdog is postponed;
no production/provider/scanner, cloud deletion/deployment or repository operation
follows. [Scope and acceptance](qa/portrait-v2-print-drive/README.md).

| ID | Owner-confirmed decision | Current interpretation / boundary |
| --- | --- | --- |
| DEC-001 | Earlier development targeted `feature/kivy-gui` | Historical; v1 was subsequently released. Continue v2 on its existing branch under DEC-020/023 |
| DEC-002 | Branded colorful Meong Kivy GUI, final cat-camera identity and twelve approved 80 mm designs | Preserve artwork and readable QR; current v2 header/typography follows DEC-022 and later visual corrections |
| DEC-003 | Advertising → acknowledged tutorial once per active visit → template gallery | Applies to direct entry and either game result if unseen; safe idle resets transient state, never consumed game attempts |
| DEC-004 | Image/video advertising with a nearby face held for five seconds inviting entry | Manual Start retained; default offer timeout 15s, cooldown 45s. Presence detection does not recognize identity |
| DEC-005 | Video owns its audio; still ads use GUI BGM; tutorial/gallery/photo use a continuous GUI loop, game a distinct loop; one cue/enabled action | One v2 owner, separate from v1. Muted payment-ad policy applies to v1's placement; native v2 Sandbox has no payment-ad panel |
| DEC-006 | Payment QRIS differs from photo-folder/download QR; separate local MOCK and merchant Sandbox clearly | Backend/client/journal Sandbox source integrated; no production activation or acceptance inferred from QR/GUI clicks |
| DEC-007 | V1 may offer a QR slip without hiding the main QR or extending validity/confirming payment | V1/shared-slip feature, not ported native v2 Sandbox UI. Dedicated merchant trial forces printer/Drive off |
| DEC-008 | Thermal printing supports configured LAN/Wi-Fi/Windows RAW USB and Floyd–Steinberg/Bayer/threshold modes | Existing printer baseline retained; owner reports quality/QR-slip/copy counts passed (BUG-004/003/011), with formal source/device/scan limits preserved. Newer lab UI is separate |
| DEC-009 | Rp5,000 per selected design/three-photo session plus Rp5,000 per identical paper copy | Separate base per design; N image+cut streams in one RAW batch. Zero deselects, 1–9 is current UI range. Digital-only/final commercial maximum policy undecided; Sandbox recomputes server price |
| DEC-010 | Design-only FEAT-002A merchant-style receipt scan/discount at checkout | Replace only payment ads with live preview, preserve QR/order; success closes scanner, failure allows retry. Example Rp50,000 food order waives one Rp5,000 base fee, never print fees; illustrative campaign, not game reward or implemented v2 path |
| DEC-011 | Real FEAT-002B POS integration waits for a partner and receipt/API evidence | Prefer existing POS receipt; detected code is not purchase/eligibility proof. Require one-use/replay-resistant verification |
| DEC-012 | Every implemented live preview is horizontally mirrored; owner extends v2 output on 26 October | V2 review and photo areas in the shared result/printed/digital strip now mirror too. Preserve full-resolution JPEG originals, detector/decoder inputs, template/text/logo/QR orientation. V1 defaults unchanged; earlier 18 October acceptance remains historical |
| DEC-013 | Future ads sync from dedicated Meong Drive into per-machine local media, typically weekly | Proposed FEAT-004, offline/atomic/fallback-safe; not a shipped central ad service |
| DEC-014 | Real merchant ordering uses a compatible customer-facing partner service; do not maintain a full Meong production POS by default | FEAT-005A standalone local DEMO ordering proposal passes a single-use promo on the same kiosk without scanning; external receipts retain their independent path. Ordering not implemented in v2 |
| DEC-015 | Configurable visual themes share one codebase | FEAT-006 proposal; admin-controlled per-machine default remains a recommendation pending final choice |
| DEC-016 | Retention target: 15 days local, 30 days Drive | Local bytes may expire even after failed upload. Cloud schedule/deletion unverified; assess delivery notice/promises before monetized digital delivery |
| DEC-017 | Coordinate BUG-009 cloud retention remediation with future FEAT-004 ads sync | Separate scopes/evidence for photo deletion and ad sync. Existing Apps Script functions may need setup/deployment rather than replacement; no deployment/deletion authorized by docs |
| DEC-018 | Earlier payment deferral has later scoped overrides | P4b Sandbox/P5 explicitly approved 24 October and source delivered; production, paid reprints, real POS/promotion settlement remain separate |
| DEC-019 | Accept FEAT-001 DEMO pricing and BUG-011 physical copy-count owner test; monitor after RAW fixes | Owner's successive confirmations preserved in [QA](qa/FEAT-001-BUG-011-acceptance.md). Focused 15/15 mock CI and paper report are separate; exact device SHA/count matrix missing. Earlier CI failure later repaired; not formally CLOSED or all-device certified |
| DEC-020 | Owner approved old-master backup, tested v1 merge and immutable `v1.0.0` source release on 19 October | Completed source operation; [release notes](releases/v1.0.0.md). Not approval for future v2 merge or hardware/production certification |

DEC-021 is not assigned in this branch's decision log; do not invent or renumber
historical entries. The branch-local FEAT-021 collision is a separate issue.

## DEC-003 addendum — tutorial and visit lifetime

**Owner refinement, 26 October 2026:** remove the separate idle CARA PAKAI
button. MULAI FOTO and invitation AYO FOTO already open the required tutorial
for a fresh visit; keep acknowledgement, cancellation and postgame routing.
This simplifies entry without bypassing or duplicating the existing tutorial gate.
[Scope, checks and rollback](qa/portrait-v2-photo-entry/README.md).

Acknowledgement, not merely rendering the tutorial, sets `tutorial_seen`.
Direct entry and win/lose both route to the original twelve-template picker,
showing the tutorial only if unseen. The game route is intro → manual DEMO input
→ one irreversible attempt → result → tutorial if needed → gallery, without replay
or direct payment jump. Local MOCK validates its reward; Sandbox requires server
verification/grant/ACK and has no trusted game-promo contract.

Reset transient tutorial/cart/reward UI only on safe visit completion/abandonment.
Never reset consumed attempts, pending/unknown/paid orders or uncertain print
state using an idle timer. The original tutorial-gate branch remains historical
design evidence; current VisitFlow integration has since been implemented.

## DEC-022 — approved portrait direction and corrected navigation

Owner selected Pixel Arcade Space / original Meong Fly visuals for a new
portrait-first 10.1-inch UI and independent audio lifecycle. This was a UI rebuild,
not permission to replace working camera/photo/print/templates/Drive services.
[Main artboard](assets/portrait-v2/meong-main-flow-approved.webp) and
[revised game board](assets/portrait-v2/meong-fly-revised-approved.webp) retain
provenance; explicit flow/price corrections override illustrative arrows and text.

Advertising/invitation share one media surface and both entry paths. The game has
its own intro before input. One receipt/code means one consumed attempt; no MAIN
LAGI after either result. Win reward is Rp2,500 per order in local/MOCK simulation;
a future provider promotion needs backend authority. Loss has no reward. Original
80×240 mm strips retain three photos plus one download QR, separate from QRIS.

Later owner typography preference supersedes bitmap main-app captions: use native
readable Roboto without mandatory icons, original game frames, larger animated
Meong and strip-focused gallery. [Visual specification](portrait-kiosk-v2-visual-spec.md).
Current source includes photo workflow, original DEMO game, MOCK/Sandbox and
read-only health/report. [Status](FEATURE_STATUS.md) records current proof;
P0–P2 design-only/no-camera statements apply only to their original snapshots.

## Business/software direction

| ID | Decision | Boundary |
| --- | --- | --- |
| BIZ-001 | Sell complete hardware as well as Meong-operated, rental/managed and contracted revenue-share arrangements | Separate hardware ownership/margin, photo income, service/warranty, operator duties and platform revenue |
| BIZ-002 | Every sold unit has a software tier: Free (Rp0 recurring), Business or Enterprise | Free is valid licensing, not a requirement to pay a subscription; entitlement implementation remains future scope |
| BIZ-003 | Free permits commercial core photo/capture/print operation and charging end customers | No Free revenue cap or disabling core capture/print because tier is unpaid; production gateway remains a separate undelivered capability |
| BIZ-004 | Meong controls all Free ad content | Central per-machine delivery and enforcement not implemented; ordinary operators do not replace/remove Meong inventory under this model |
| BIZ-005 | Business/Enterprise manage their own ads while retaining reserved Meong slots | Reserved share/frequency TBD, not illustrative 20%/10%; disclose terms and venue/competitor exclusions. Enforcement not implemented |
| BIZ-006 | Subsidy applies only to actually redeemed eligible photo discounts | Meong-operated booth may reimburse Meong; sold booth ordinarily reimburses the operator bearing the waived fee, with separate contracted platform fees. Contract controls ownership |
| BIZ-007 | Other monetization ideas are parked for evaluation | Premium content/events/analytics/support/warranty/white-label/ad-network candidates are not priced or approved implementations |

## Open policies and evidence

Graceful paid-tier downgrade to commercially usable Free without interrupting
orders is recommended, not finalized. Paid entitlements/prices/periods, licensing,
Meong slot quotas, venue rights, campaign eligibility/expiry/refunds/stacking,
merchant-of-record/settlement/fees, digital-only purchases, commercial print
limits, warranty/SLA and partner ordering availability remain open. Mixed-template
calculation already exists under DEC-009; future commercial revisions need approval.

BUG-009 remains OPEN. BUG-012/013/014/015/016/017 retain owner-reported monitoring
within their metadata limits; v1 BUG-001/007 are not closed by v2 audio.
Preflight `0dc6555` does not certify new Windows/merchant/paper/Drive/privacy
acceptance. Public webhook deployment, trusted QRIS game promotion, production,
POS/scanning, merge and release are separate scopes, not hidden prerequisites
for a local simulator trial.

[Protocol](DEVELOPMENT_PROTOCOL.md) · [current features](FEATURE_STATUS.md) ·
[backlog](next_step.md) · [handover](DEVELOPMENT_HANDOVER.md) · [changelog](CHANGELOG.md).

