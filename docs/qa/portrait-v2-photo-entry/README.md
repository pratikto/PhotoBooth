# GUI v2 — mandatory tutorial without a separate help button

Owner request, **26 October 2026 (Asia/Jakarta)**: remove the separate button
for entering the tutorial because starting a photo visit already requires it.

## Scope and baseline

Required branch: `feature/portrait-kiosk-v2-next`. Base/rollback checkpoint:
`f79fa583f208c1ac1981985c1e1f9de5c81eba0f`, confirmed against remote HEAD before
editing. Reuse the current v2 idle layout, action/input/audio adapter and
`VisitFlow`; no new navigation engine or reference-branch port is needed.

Remove only the idle **CARA PAKAI** action and its redundant two-column wrapper.
Keep MULAI FOTO, MAIN MEONG FLY and UNDANGAN (DEMO). A fresh direct/invitation/
postgame photo visit still goes through the four-step tutorial before templates.
Keep the tutorial's acknowledgement, cancellation and safe visit-reset rules.
Unrelated print/Drive, device, game, payment and retention behavior is outside
this change.

## Validation and acceptance

Functional source **`20453fe302447ebf349165c44a695817a66c6f34`**, committed and
remote-verified on the required branch. Only `photobooth/kiosk_v2/app.py` and
the existing native widget test changed among runtime/test files; `VisitFlow`,
v1 application/services and original mini-game files are unchanged.

The updated native entry case activates the actual Start/acknowledgement and
invitation buttons, verifies the idle control set, and checks fresh-visit reset.
Existing game/routing cases cover the postgame tutorial gate. Preliminary
[focused run](focused-tests.txt): 57 cases, **55 PASS / two opt-in skips**, zero
failures/errors, 27.317s. Those palm-assets/native-audio opt-ins are included in
the [final full run](full-tests.txt): **800 PASS / zero failures/errors/skips**,
217.888s. The full run began before commit; all [232 functional hashes](tested-source-sha256.json)
still match source `20453fe` exactly.

The unchanged renderer produced twelve clean-source PNGs; source SHA, hashes
and dimensions were verified. Six affected views (idle/invitation/tutorial at
both required sizes) were inspected: no help button or empty split column;
remaining actions, overlay and tutorial acknowledgement/cancel fit.
[Validation record](validation.json) · [800×1280 report](report-800x1280.json) ·
[452×900 report](report-452x900.json).

| View | 800×1280 | 452×900 |
| --- | --- | --- |
| Idle | [Screenshot](screenshots/01-advert-800x12800001.png) | [Screenshot](screenshots/01-advert-452x9000001.png) |
| Invitation | [Screenshot](screenshots/02-invitation-800x12800001.png) | [Screenshot](screenshots/02-invitation-452x9000001.png) |
| Required tutorial | [Screenshot](screenshots/03-tutorial-800x12800001.png) | [Screenshot](screenshots/03-tutorial-452x9000001.png) |

Checks use Linux/Python 3.12.14/Kivy 2.3.1, software GL, dummy PCM and prepared
offline model/transport fixtures. They do not certify Windows touch, audible
speakers, physical printing, cloud retention or merchant acceptance.

[Matching-source CI 40248962384](https://github.com/pratikto/PhotoBooth/actions/runs/40248962384)
completed with **all three jobs SUCCESS** ([job metadata](final-ci.json)).
Raw [CI reports](ci-reports/) record delivery 17 PASS, health 80 PASS, Sandbox
139 PASS, and native widgets 104 cases / **103 PASS / one optional palm-assets
skip**. That skipped model case ran in the local full suite; the CI skip stays
explicit. Windows audio also uses dummy output. [Artifact inventory](ci-artifacts.json)
retains the screenshot package reference; the twelve verified/reviewed local
captures above are separate exact-source evidence. Documentation-only evidence
delivery skips another Actions run.

```powershell
git pull --ff-only origin feature/portrait-kiosk-v2-next
git rev-parse --short HEAD
python tools/run_portrait_v2.py
```

Windows spot checks (NOT_RUN here; no extra twenty-cycle gate):

- [ ] Idle has MULAI FOTO and MAIN MEONG FLY, with no separate CARA PAKAI button.
- [ ] One MULAI FOTO tap opens the four-step tutorial; acknowledgement opens templates.
- [ ] Cancel/finish to idle, then Start again: the new visit requires the tutorial.
- [ ] Invitation AYO FOTO and game-to-photo keep the required tutorial flow.
- [ ] At 800×1280 and 452×900, ads/buttons remain visible and each active tap sounds once.

## Rollback

Use a scoped inverse commit of this change on the same authorized branch after
inspection. Restore the prior idle action/layout if needed; preserve transaction
journals, consumed game codes, photo/print manifests, counters, configuration and
customer data. No reset, new branch, merge or production activation is involved.
