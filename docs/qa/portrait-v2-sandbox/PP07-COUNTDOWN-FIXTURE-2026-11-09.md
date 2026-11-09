# PP-07 deterministic native blocked-receipt clock fixture

9 November 2026, branch feature/post-preview-qris-checkout.

Sourcef098c05 local full regression: **672 backend PASS (292.753s) and 74 native
PASS (210.320s)**, zero failures/errors/skips. The original Apps Script syntax
check and all **34 offline VM tests PASS**. Matching CI42579045180 Ubuntu672
PASS (231.130s); native74 failed two portrait subtests of one method: expected
10 seconds, observed11. Windows is still running at this report's publication.

The failure is an uptime-dependent floating-point fixture boundary, not evidence
that a printer blocked the countdown. Deterministic reproducer:
(27.48696930099077+20)-27.48696930099077 == 19.999999999999996.
Ceiling 30 minus that elapsed value is11. The test had patched clock to the
host's arbitrary start+20 and required exact integer10. Product timing and all
other native methods are unchanged; do not relax the actual 30-second deadline.

The native blocked-receipt test now constructs the ORIGINAL VisibleTicketWindow
with an injected exact clock100. It checks10 at120, keeps the same private card
and active timer just before130, then requires immediate QR/full-code wipe at
exact130 while the original receipt remains SENDING. It still checks both
800x1280 and452x900, one charge, one eventual receipt and durable DISMISSED.
No production clock, countdown code, privacy guard or timeout was modified.
The exact previously failing method now **1 PASS /both sizes,6.364s**, zero
failures/errors/skips. Fresh source-matched full CI is required after this fix.

Local native setup initially lacked Xvfb and writable default Kivy home. No sudo
or system-package helper exists. Official Debian13 display packages were
fetched over HTTPS, SHA256 checked against the official package index and
extracted into an untracked local work directory; Kivy home was also local.
No system image/sudo/network policy changes, device input or actual paper.
An initial local command wrapper indexed the Python argument incorrectly;
corrected before the completed native result above. Standard unittest discovery
hid its successful report through Kivy redirection; the exact focused result
above comes from the original fd-safe registered runner, not an assumed count.

A retrospective guard regression also ran the two new collector PREPARE/ACK
methods against prior8398b53 isolation source: **two expected assertion failures,
zero errors**, proving that the prior code ignored the still-live collector.
Current collector scope69 PASS and full672 PASS remain recorded separately.
This prior-source test is not described as a test-first chronology.

[Machine evidence](provider-bootstrap-2026-11-09/countdown-verification.json).
Commercial status remains NOT_READY. Complete protected native paid ticket/
delivery/claim/release mounting, actual refund/status and operating package,
then supported Ubuntu/account/device/long-duration acceptance. Do not rerun
owner's eleven reported checks without a relevant change or evidence gap.
