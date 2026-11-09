# PP-06 original readiness collector release fence

9 November 2026, feature/post-preview-qris-checkout; base8398b53.

WorkerReadinessServer now serializes start/stop and permanently retires a stopped
capability, including stop-before-start. quiescent closes the original channel
and requires the actual collector thread to finish. Socket closure or deadline
expiration alone never acknowledges that its callback stopped. A later visitor
needs a newly constructed private channel/collector and backend connection.

OriginalMockIsolation accepts an optional exact original readiness server and
holds PREPARE, ACK, pre-ACK process restoration and already-ACKed reply recovery
while that collector remains active. OriginalPilotAdmission also applies this
fence before resetting a retired visitor, including the existing-ACK path.
Original financial/Drive/printer/worker fences and mock-only constructor guards
remain intact. Existing mock launchers have no collector; default None preserves
that exact profile. The future native Sandbox assembly MUST bind its original
collector; this increment does not mount that unfinished profile.

**69 related PASS, zero FAIL/ERROR/SKIP,18.328s**. Five new methods prove a late
collector cannot PREPARE or ACK an unpaid release, cannot bypass a previously
ACKed paid handoff, keeps original PAID/OWED while held, finishes before B, and
cannot restart or send old readiness afterward. Prior generation/scope/nonce
and actual-process bridge tests remain registered. Synthetic callback/device/
payment fixtures only; not actual Ubuntu hardware or merchant acceptance.
[Exact evidence](provider-bootstrap-2026-11-09/collector-verification.json).

Read current bootstrap/presentation reports, original readiness bridge,
security-state worker/PREPARE/ACK contracts and admission/isolation source/tests.
Next source work: protected Recovery Ticket/one receipt and original paid
Drive/strip/delivery/claim/release, then native provider profile assembly without
dummy payment authority or mock-guard removal. Refund/status/operating package,
full mini-PC acceptance and measured final qualification remain unfinished.
No original journals, customer media, keyring or uncertain jobs were reset.

Earlier A2 CI42577500308 passed Ubuntu/native; Windows was cancelled by the
next authorized source push and has no complete verdict. B1 CI42578619179 is
in progress. Full regression and matching CI for this increment remain pending
at publication; never infer PASS from these earlier sources.
