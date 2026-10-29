# AR-02.d / PAY-08 — bounded native connectivity restoration

29 October 2026 (Asia/Jakarta). Owner authorizes continuation and documentation
updates after the source audit. Base/remote verified
`e0f4bb663f25247003176da555dbd30744c0e2e3`, existing feature branch only.
**Contract before code — implementation/tests NOT_RUN at this initial entry.**

## Review, reuse and scope

Reviewed AGENTS, protocol/prompt, current index/handover/checkpoint/roadmap,
master/provider/operations/reconciliation contracts, current audit/matrix/readiness
and existing controller/client/API/store/worker/native tests. The earlier project
architecture/status/decisions review still applies; no intervening runtime change
since 4642841. No archive/customer/configuration contents are inspected.

Reuse authenticated client `reconcile(trigger='connectivity')`, the backend's
durable priority_after/request lease/evidence revision, and SandboxJobs' existing
single worker plus native check polling. Existing v1 check_network actively dials
an external IP and is an operator diagnostic, so it cannot serve as a passive OS
event source here without adding unrelated external probes. No change to v1,
MOCK, charge creation, camera/countdown, grants, release, print or Drive.

## Two micro-increments

1. AR-02.d1: independently tested passive OS hint reader and coalesced edge
   observer, initially unmounted. Windows reads Network List Manager connectivity
   through built-in noninteractive/no-profile PowerShell; Ubuntu reads the cached
   NetworkManager CONNECTIVITY field through nmcli. Both query local OS state;
   neither asks NetworkManager to perform a connectivity check or contacts an
   external host. Fixed argv, shell=False, sanitized minimal child environment,
   bounded timeout/output acceptance, no credentials or command output logged.
2. AR-02.d2: mount on the existing native Sandbox check worker for an active known
   order needing recovery. A sampled offline→online edge immediately invokes the
   original order's read-only connectivity reconciliation, even during local error
   backoff. No ordinary refresh in the same iteration, and no grant/service or
   photo action. Current privacy epoch/ownership barriers remain authoritative.

OS sampling is at most once per five seconds while recovery needs observation.
Initial online and unknown samples do not invent a restoration edge; unknown
does not erase a previously observed offline state. Repeated online samples emit
no further event. Rapid real edges still obey persisted backend ten-second
priority budget and active GET lease, including across reopen/restart.

An OS hint never proves provider reachability or payment. Missing nmcli/NLM,
timeout, unknown/captive state or unsupported platforms fall back to existing
bounded provider polling. Short outages between OS samples and network changes
that the OS does not report are not promised immediate detection. This portable
source feature does not certify Windows/Ubuntu physical reconnection or Android.

## Acceptance and evidence plan

- Reader fixtures: Windows/Ubuntu offline/online/unknown, unavailable command,
  malformed/oversized output, timeout, unsupported OS and no secret inheritance.
- Observer: initial-online silence, offline→unknown→online one edge, repeated
  online silence and bounded sample frequency.
- Real API/client/SQLite plus native worker fixture: repeated provider outage
  builds backoff; fake OS reader produces offline→online before next deadline;
  exactly one provider GET reconciles original order without new POST/grant,
  service transition, media disclosure, camera/print/Drive action.
- Duplicate edges and reopened client cannot bypass persisted priority/lease;
  offline/refund evidence cannot authorize customer resume; main thread stays
  responsive and late callbacks retain privacy guards.

Focused tests each increment, then immediate docs/commit/push/remote verification.
One final full regression and matching CI at the functional SHA. No new layout:
retain source-specific native screenshots, do not claim new physical evidence.
PAY-08 remains NOT_RUN until actual integrated synthetic assertions execute.

## Migration, rollback and remaining gates

No schema or journal field migration. Observer state is transient and lost on
restart; backend retry priority/lease remains durable. Scoped inverse unmounts
the observer and preserves all orders/claims/media/fences/backoff/budgets. No
repeat charge, production, OPS implementation, service install, actual paper,
Drive upload/deletion or public ingress activation. BUG-023 and other exact
fault/device/provider/privacy/operational gates remain open.

## AR-02.d1 delivery — reader/observer only

Nine focused tests PASS, zero failures/errors/skips, 0.004s, Python 3.12.14/Linux.
Before implementation the new module failed to import (one loader ERROR).
[Exact command/report/source hashes](evidence/pay08-reader.json). Reader and edge
observer are unmounted; no actual OS command is executed by these fixtures.
CI groups include the new portable module. Full regression/native integration
and PAY-08 classification stay pending until AR-02.d2. No schema/journal change.
Next: sample on existing recovery check worker and submit only same-order GET;
verify outage/backoff/edge/duplicate/reopen/privacy invariants before activation.
