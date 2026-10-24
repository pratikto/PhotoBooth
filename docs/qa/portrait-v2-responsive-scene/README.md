# Responsive Meong Fly and compact gallery — 2026-10-24

Owner requests a unified game scene, real component resizing instead of separate
side filler, simpler price information and removal of the CETAK caption.
Required branch: feature/portrait-kiosk-v2-next. Starting rollback: 87a13b9.
Read-only game reference remains 672e3f7089bb40940e5b41644ceb656aa63aafbb.

## Stage 1: compact gallery

Keep the three strip previews and floating navigation. Replace the dense price
formula and repeated offer sentence with − / selected quantity / +, prominent
TOTAL SIMULASI and two short details: total sheets/sessions and savings when
applicable. Remove CETAK. Quote math, consumed discount and disabled production
payment behavior are unchanged. The card remains 98 logical pixels even with
a discount, returning space to the strip preview.

Local native checks: **20 PASS**, zero skips; see stage1-gallery-tests.txt.
Includes resize bounds at 800×1280, 452×900, 360×640, 452×600 and 800×600,
intact 1:3 strips, visible price labels, MOCK quote consistency and twenty
simulated MOCK visits. An initial test invocation used the wrong class name;
a concurrent render then caused a timed-out test worker. Correct invocation
run alone passed. These are cloud checks, not Windows hardware acceptance.

Stage 2 will replace the rejected separate filler with responsive original-art
composition. Do not treat the earlier filler QA as acceptance of this request.

Reviewed native capture: [winning gallery at 452×900](stage1-gallery-452x900.png),
with Rp7.500 net total and Hemat Rp2.500. Preview strips remain the visual focus.
