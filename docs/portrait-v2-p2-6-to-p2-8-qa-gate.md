# Portrait GUI v2 — P2.6–P2.8 quality gate

**Scope:** GUI v2 branch `feature/portrait-kiosk-v2-next` only. Meong Fly remains read-only; no integration, real scanner, QRIS, discounts, capture, or printing changes.

## Checkpoint and evidence policy

- Last confirmed successful GitHub Actions workflow at the time of this document: `d7509f34e91a704892f1271bb17a406fe7b0e2f3`. Newer commits must not inherit this PASS.
- A pushed commit and verified remote HEAD mean **published**, not **tested**.
- Gate requires a GitHub Actions run with `head_sha` **exactly equal** to the milestone checkpoint SHA and both jobs successful. If no matching run is available, mark **BLOCKED / NOT VERIFIED**, never PASS.
- The desktop job must upload twelve screenshots (six pages × two viewports). Download and inspect those screenshots; existence alone does not prove legibility or alignment.
- Never claim hardware audio, camera, printer, QR/payment, or touch accuracy from Xvfb synthetic tests.

## P2.6 — Visual unification

- [x] Extract game palette and pixel geometry as pure design tokens.
- [x] Replace native v2 card/button backgrounds with stepped arcade styling.
- [x] Add design-token and clipped-corner regression tests; include them in CI.
- [ ] Review all six rendered pages at **800×1280** and **452×900**, with no clipping, obscured CTA, unreadable text, or accidental rounded v1 elements.
- [ ] Record a matching-SHA CI PASS and preserve artifact reference.

## P2.7 — Responsive, interactive and audio lifecycle

- [x] Add fake-provider tests for page ownership, game-preview handoff, suspension, resume, cleanup, and idempotent teardown.
- [ ] Verify navigation and touch targets across both viewport sizes with widget smoke and visual evidence.
- [ ] Check transitions, timeout-to-idle behavior, one-tutorial-per-visit, and no restart of soundtrack during tutorial-to-template navigation.
- [ ] Verify game preview does not overlap GUI music; actual Meong Fly is not integrated.
- [ ] Verify real Windows speaker playback and camera only during later operator acceptance, not in CI.

## P2.8 — Visual QA and rollback

- [ ] Review screenshot artifact pixel-by-pixel for each page, each viewport.
- [ ] Record screenshot artifact URL, exact SHA, test run ID, test summary and known limitations.
- [ ] Close all P2.6–P2.8 blockers; mark non-hardware gates PASS only with evidence.
- [ ] Record final stable commit as rollback reference; do not merge to `master`.
- [ ] Present Windows acceptance checklist for user approval **after** P2.8 evidence is ready.

## Operator Windows acceptance (approval required later)

1. Run the GUI v2 on the actual 10.1-inch portrait touchscreen at its native resolution.
2. Confirm idle/invitation/tutorial/templates/cart/game-preview screen alignment and all CTA touch areas.
3. Confirm music audible on tutorial/templates, silent on advertisement and game preview; suspend/resume and exit cleanly.
4. Confirm the camera and thermal printer are **not** represented as validated by this prototype; verify those only in separately authorized end-to-end integration.
5. Compare approved 12 vertical thermal designs and three-photo/QR layout against their existing source of truth; GUI prototype must not silently modify print output.

**Release rule:** no automatic promotion to master, no game integration, no assertion of production readiness from synthetic checks.
