# Physical-device test readiness — 5 November 2026

**SOFTWARE_READY_FOR_SUPERVISED_PHYSICAL_TEST** — the final verification below supersedes initial PENDING notes. Use the [short physical quick start](PP07-PHYSICAL-QUICK-START.md). Owner hardware observations remain NOT_RUN.

The owner requests a directly usable supervised physical test entry point. This work targets the existing synthetic-payment pilot with real camera/touch/audio and separately opted-in printer/test Drive. Actual merchant QRIS/refund and production are separate gates; completing pre-ACK protected worker restoration is not a prerequisite for a fresh-root, same-process device trial.

Baseline: `4e637e3186d6b3a23f4b02499b591b89c8334e54`, runtime/test source `17f7863`, 1,766 local PASS and CI 41944005227 all three SUCCESS. No source changes to working photo/payment/claim/print services are planned for this packaging increment.

## Implementation and verification scope

Reuse the existing launcher and its validation functions. Add one cross-platform Python entry that validates the same interpreter/source/branch, creates a unique unused trial identity, sets only the child process's isolated physical-camera/synthetic-payment profile, forwards the original dual-consent paper/Drive flags, and records a redacted local session result. Check-only must perform no directory/device/cloud writes. Launch exit zero is not hardware acceptance PASS. Never reopen or reset old trial roots.

Provide a Windows PowerShell entry that reuses `.venv-kivy`/`.venv`, explicitly installs dependencies only when requested, checks each command's exit status, then calls the Python entry. Keep standard 452x900 and 800x1280 layout options. Preserve actual-camera index selection and parent environment. Default print/cloud remain virtual. Ignore generated private trial roots and reports in Git.

Tests must cover blocked preflight/dual consent/occupied or symlink paths, unique roots, exact child command/environment, missing interpreter/setup failures, exit propagation, metadata containing no secret values, and no check-only side effects. Verify the packaged native path with the existing GUI journey suites and source-matched Windows/Linux CI. Update the quick start and record exact results before calling this a software-ready physical-test candidate.

## Acceptance boundary

Physical webcam/touch/speaker/paper/cutter and signed-out real Drive access need owner observation at the actual device. Full restart/uncertain-paper/merchant/refund/release gates stay explicit. No physical result is claimed by this implementation record.

## Initial focused execution

Twenty-seven command/preflight/root tests PASS, followed by a combined exact-source **28 PASS / zero failure/error/skip in 4.861s**, including the actual pilot `main`/build/worker-binding path at both 452x900 and 800x1280. Native window/widgets and actual API/service calls are exercised with a synthetic camera and virtual transports; `App.run` is intercepted for deterministic button/worker driving. This is not actual camera acquisition or a real-time timer qualification. The real SIMULASI PAID control produces one charge, one ticket receipt and exact 2+1 strip sends, preserving OWED/no physical-paper claim.

The helper clears only child-process headless/dummy drivers and conflicting legacy flags, sets physical camera/index/audio, and keeps manual capture. Source HEAD metadata explicitly does not attest a clean working tree; session exit zero is CLOSED_NOT_ACCEPTED and hardware acceptance remains NOT_RUN. Paper/Drive require the existing two flags each. Check-only is read-only; local session records are siblings rather than occupying the child's new private root. Git ignore checks verify default trial/report paths cannot be accidentally added normally.

Initial native probe errors were environment/harness issues: this managed host's default HOME is read-only, so diagnostics use a task-only KIVY_HOME; the first harness referenced an incorrect private coordinator field and was corrected to the existing `_pilot_admission`. No product defect or relaxed guard is claimed. The original pilot now configures window size before importing native widgets and only after acquiring its existing launch lock.

Windows PowerShell setup/check-only, Linux packaged check-only, final broad regression and exact-source CI remain PENDING at this implementation publication. The [quick start](PP07-PHYSICAL-QUICK-START.md) becomes the owner entry after those verification results are recorded.

## Final source-matched verification

Source `8901bbcd2fb302e278106a7b49aa5d4f4c9a726d`: **1,778 local PASS**, zero failures/errors/skips, all GUI/audio/video/real-model opt-ins enabled, process duration **488.262s**. Pinned public assets were independently hash-verified again. No actual camera/printer/cloud/merchant operation ran in this managed environment.

[CI 41952947024](https://github.com/pratikto/PhotoBooth/actions/runs/41952947024) is completed **3/3 SUCCESS** at the exact same source: **574 Windows + 574 Ubuntu + 68 native Kivy PASS**, each zero failures/errors/skips, all logs independently inspected. Windows also executed the actual **Start-PostPreviewDeviceTest.ps1 -Setup -CheckOnly** path in a fresh venv: all three requirements files installed, pip check passed, and the same interpreter reported READY_FOR_SUPERVISED_SYNTHETIC_PILOT without device acquisition. Linux's packaged check-only also passed. The native main/build/binding/paid-output test ran both portrait sizes. These software counts overlap and are not full acceptance-case counts.

[Machine-readable provenance and source/log digests](evidence/pp07-physical-entry-2026-11-05.json). Generated private trial/report paths were checked with git check-ignore; Python source parses, diff whitespace and relative documentation links pass. The final documentation checkpoint does not change the verified runtime/test files or require retriggering the successful workflow.

**Owner can now start the fresh-root supervised physical trial** using the quick start: Windows setup/check command, then one launch command, real camera/audio/manual capture by default, optional separately consented POS80/test Drive. Report actual hardware observations independently. Full protected pre-ACK/reboot/Ubuntu restoration, real merchant/refund/legal/production, physical peripheral acceptance and qualification remain separate gates; the helper does not claim or enable them. All canonical PP/PILOT/UAH full acceptance outcomes remain unchanged until independently observed.
