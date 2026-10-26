# Booth storage/global-content audit — 26 October 2026

Requested work: inspect current folder organization against the owner's explicit
per-booth/session/raw/color/bw/global-cache target. **Audit/documentation only**;
no runtime path switch, source implementation, cloud setup, upload, print,
migration or deletion is performed. The target is not claimed implemented.

[Target contract and implementation map](../../photobooth-storage-layout.md).
Base/source and rollback checkpoint:
**19e3f4d4f0b4148b5daba6d25f6b5fe0387a4802** on required branch
`feature/portrait-kiosk-v2-next`, confirmed against remote before work.
Relevant [reference tips](source-refs.json) were refreshed read-only; no branch
switch/merge, master change or import of a newer lab/reference experiment.

## Archive exclusion and access limits

All repository searches explicitly exclude root/nested `old`; bounded directory
inventory filters its name **before** inspecting/descending an entry. Active
source reads name fourteen specific non-archive files. Experiment recursion is
restricted to newly created temporary fixtures, not the checkout/data/archive.
No content or metadata baseline was read from `old`, and it was not changed.

No Google/Drive connector, private local settings or Drive environment configuration
was available. Actual installed Drive folder names/IDs/content and actual global
cache availability are therefore **NOT_INSPECTED**, not inferred from code.
Configured-parent transaction creation could already be pointed at a manually
created PB001 folder; the audit does not assert that the operator's Drive is flat.

## Executed checks

The owner answered the optional exhaustion/first-offline question: **"Tetap
foto/cetak lokal; upload dan QR download menyusul saat online"**. The target
contract records this decision and the required deferred-binding/ID/QR handling;
the audit has not changed the current no-ready-slot admission gate.

[Existing source tests](existing-tests.txt): **38 PASS / zero failures/errors/skips**,
5.660s, using the prepared Python 3.12.14 cloud environment:

```text
python tools/run_kiosk_unittests.py test_workflow test_drive_workflow test_dither_print test_retention
```

No new application tests or features were added. Those tests verify **existing**
services, not the requested future layout or live Drive acceptance.

The [controlled experiment output](experiment-output.txt),
[structured observations/hashes](audit.json) and [exact experiment source](experiment-source.txt)
record these additional temporary-fixture checks:

- Actual `PhotoTest`: A×2 + B×1 creates two sessions/three copies, seven original
  JPEGs including one retake, and two RGB output PNGs. Files are still
  `raw/session_001/...`, `raw/session_002/...`, `output/session_001.png`, etc.
  No `Photo/01`, `color` or persisted `bw` directory is created.
- Actual `ThermalPrinter._build_payload` with only the ESC/POS in-memory Dummy
  replaced: existing tuned rendering computes a 1-bit 576×1728 raster from the
  640×1920 RGB strip, but writes no new transaction file. No printer send occurs;
  all original JPEG hashes remain unchanged.
- Actual shared `DriveSlotPool` with synthetic remote responses: refresh creates
  25 empty local staging directories; a restarted pool can claim one without a
  client/network, leaving 24. These are cached preverified Drive slots, not a
  newly provisioned actual booth or unlimited offline Drive capacity.
- Actual v2 `prepare`, with background starts stubbed: native code sets
  `target_ready=2`, and an empty Drive pool refuses admission without allocating
  a new transaction. Existing local-only output does not promise later automatic
  Drive binding/upload.

All fixture directories were destroyed by `TemporaryDirectory`; only safe
relative example paths, counts and selected source hashes were retained.
`old` and real customer/operational directories were never fixtures.

## Verification and rollback

Validate target tree/requirements against inspected paths, local Markdown links,
JSON syntax, source-hash stability and changed-path exclusion of `old`.
This documentation-only publication skips Actions; no GUI capture/full 808-case
rerun is needed when application code/layout is unchanged. Prior mirror evidence
remains tied to fc26e3d and is not reissued as target-storage acceptance.

Rollback is a scoped inverse of these audit documents, preserving the existing
source, all photo/print/payment data/counters and `old`. The audit does not
authorize moving an archive or a live Drive parent. Future implementation must
coordinate the storage, pool, raster, upload, retention and content-catalog paths
listed in the target contract before any operational cutover.
