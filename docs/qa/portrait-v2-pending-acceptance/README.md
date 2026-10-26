# All outstanding GUI v2 acceptance — 26 October 2026

Owner asks for every remaining untested gate. Runtime baseline **53e7b4c**,
documentation baseline **6ab54d3**, required branch `feature/portrait-kiosk-v2-next`.
This documentation/form does not change runtime, execute tests on the owner
device, deploy Google/provider services, delete photos or grant release approval.

[Open the 49-item interactive checklist](windows-checklist.html) ·
[Plain checkbox checklist](checklist.md) · [Canonical item data](checklist-data.json).

Reuse the existing storage/P5 form: offline checkboxes, safe metadata import,
Submit-to-prompt, copy/download/print, local persistence and original Sandbox
twenty-cycle rule. Every item starts unchecked and uses a new storage key.
Submit prepares text for chat; the owner must paste/send it.

Earlier owner PASS/monitoring reports and twenty local photo/game cycles remain
recorded at their original source/metadata. They are not reopened as failures.
Section A is a short current-build/device integration check, not a demand for
another old twenty-cycle run. G01/G02 alone require twenty NEW Sandbox
integration cycles, as the existing P5 gate already requires. Raising the
counter does not check those boxes; lowering it clears/disables them. A–F/H
can proceed independently; unavailable tests stay blank, never PASS.

## Start on Windows

Use the existing checkout/venv. Preserve local edits and pending jobs.

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
git rev-parse HEAD
python tools/check_portrait_v2.py
Start-Process .\docs\qa\portrait-v2-pending-acceptance\windows-checklist.html
```

Import `data/diagnostics/windows-readiness.json`, then verify the actual kiosk
monitor/device. Metadata import does not mark results passed. Use only synthetic
photos/order/retention fixtures; keep customer photos and credentials out of
reports. Never inspect/modify `old`, clear counters/journals, replay an
uncertain job, or change the Windows clock to force an expiry test.

- A: current Windows/profile integration (6 items).
- B: actual paper/mirror/QR/uncertain print (6).
- C: real Drive, first-offline/exhausted reserves, reconnect and restart (7).
- D: actual Google setup, per-booth content/cache and idle activation (7).
- E: real retention activation/status/local expiry/cloud expiry/hourly execution (8).
- F: real Sandbox account + official simulator/order/recovery (10).
- G: twenty NEW Sandbox cycles/restart (2).
- H: privacy/report and acceptance-package review (3).

First test local. Ordinary test printing/Drive uses
`python tools/run_portrait_v2.py --print --drive` after existing configuration
and manual Code.gs setup. Close it before
`python tools/run_portrait_v2_sandbox.py`; this dedicated trial keeps printer/
Drive off. Use only the official provider simulator, never a bank/wallet app.
If Sandbox access is missing, leave F/G blank and finish other available groups.

## Coverage and boundaries

| Outstanding evidence | Existing source/runbook | Consolidated items |
| --- | --- | --- |
| Current Windows/P5 integration and source/device metadata | [P5](../portrait-v2-p5/README.md) | A01–A06; F/G for new merchant integration |
| New raw/color/BW layout and physical output | [Storage setup](../feat-004-storage/SETUP.md), [print/Drive](../portrait-v2-print-drive/README.md), [mirror](../portrait-v2-mirrored-output/README.md) | A03; B01–B06 |
| Phone download, queued upload, no replay | Same storage/print guides | C01–C07 |
| Global/local content, 25 empty reserves, operator overlay | [FEAT-004 evidence/setup](../feat-004-storage/README.md) | D01–D07 |
| Actual BUG-009 expiry/timer evidence | Current storage setup, [earlier retention diagnosis](../bug-009-retention/README.md) | E01–E08 |
| Official provider credentials/simulator/recovery | [Sandbox](../portrait-v2-sandbox/README.md) | F01–F10; G01–G02 |
| Consent/access/report/operator review | [P5](../portrait-v2-p5/README.md), [promotion boundaries](../../gui-v2-promotion-plan.md) | H01–H03 |

The older retention form's coarse folder-age precondition does not apply to the
new layout-2 sweep: original transaction deadlines govern late-created folders.
The older print/Drive form's remote-ready consent gate is superseded: current
layout 2 admits local photos/print without a ready remote slot. This combined
checklist uses the latest behavior, not those historical requirements.

Not added as failed/untested checkboxes for an existing feature: production
payments/POS/scanner, trusted merchant game promotion, public webhook deployment,
AI/WhatsApp/device switching, newer experimental lab GUI, default/rename/merge
and production release. These need their own approved scope or repository
operation. Public webhook acceptance is separate from the current simulator/
polling trial. v1 BUG-001/007 and prior accepted monitoring reports are also
separate. H03 records package review, not authority to perform those actions.

No owner results have been submitted for this new combined form. Source
824-PASS/24-Code.gs/CI evidence remains separate from physical/provider acceptance.
BUG-009 remains OPEN until actual authorized deletion evidence. Browser tests
of this form are synthetic UI checks, not Windows/Drive/paper/provider passes.
Rollback: restore only these new documentation files/links; preserve old forms,
old localStorage keys, source/state/journals and all dated evidence.

## Form verification (synthetic, not device/provider acceptance)

[Browser checks](browser-tests.txt) · [structured result/screenshots](browser-results.json) ·
[reusable verification driver](browser-driver.cjs.txt).

49 fresh unchecked items; older form passes remain separate; metadata/forged
pass fields cannot pass cloud/paper/provider or borrow a cycle count. Partial
Submit reports 2/49 and 47 unchecked. G01/G02 stay disabled below twenty new
Sandbox cycles, do not auto-check at twenty and clear when the count drops or
stale persisted state disagrees. Other groups stay independent. Optional booth/
printer metadata, persistence, download and reset are verified; zero JS errors.

Initial browser QA exposed horizontal overflow from long launcher/path text
at 360px. The new form now wraps those spans/paths; the final test passes
360/452/800px bounds and reachable Submit. Top/footer were visually reviewed at
800×1280/452×900. Published screenshots show reset/empty answers, not synthetic
paper/provider PASS. No full application regression or GitHub Actions rerun is
needed for these documentation-only changes; runtime hashes remain unchanged.
