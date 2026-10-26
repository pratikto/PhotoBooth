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

Update the existing native entry test to exercise the actual Start and invitation
buttons and confirm the help action is absent. Run the existing routing/native
checks, one final full regression, and the existing renderer at 800×1280 and
452×900. Record results and screenshot source/hash/dimensions here after execution;
do not infer Windows touch/audio or physical acceptance from cloud fixtures.

Windows spot checks (initially untested):

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
