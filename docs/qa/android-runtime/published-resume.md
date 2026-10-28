# Published-environment Android build continuation

Date: 28 October 2026 (Asia/Jakarta). Base source:
`a0e6710f856a1547a067e152a116d03e3c60ab25`, existing
`feature/portrait-kiosk-android`. The published filesystem restored the checkout,
JDK/SDK/NDK and staging caches. No environment draft settings were reapplied and
no environment publication was performed by this continuation.

## Confirmed previous source CI

[Android preview run 40601524544](https://github.com/pratikto/PhotoBooth/actions/runs/40601524544)
completed **SUCCESS** at exact functional source
`7d49f34b4cb09a9eca56921ac56ecfbd73a86e6b`. This confirms the previously
unqueried remote preview/policy/widget checks, not an APK or Android device.
[Job evidence](published-source-ci.json) retains the observed step outcomes.

## Local build after publication

Current runtime observations are running/current with enforced network policy.
The FreeType source host is now permitted, but its HTTP 302 redirects to
`https://ftp.cc.uoc.gr/mirrors/nongnu.org/freetype/freetype-2.14.1.tar.gz`.
The redirected host is rejected by the proxy with CONNECT **403 Forbidden**.
The resumed local build therefore exits 1 during recipe download. This is a new
redirect-specific observation; the older primary-host denial is retained in
the previous dated record. No TLS/checksum bypass, alternate unverified source,
cache reset, new network draft or publication was used.

## Hosted build and bounded workflow correction

The documented manual APK route was dispatched once at exact base `a0e6710`:
[run 40622615666](https://github.com/pratikto/PhotoBooth/actions/runs/40622615666).
Its `apk / apk` job **122599994852** failed at
`android-actions/setup-android@v3`, before prerequisite installation or compilation.
The subsequent APK checks were skipped, not passed. The preview job is separate.
GitHub's API annotations expose only action-deprecation/missing-artifact warnings;
they do not identify the SDK action's root error. Detailed log download is blocked
at `results-receiver.actions.githubusercontent.com`. Do not infer a Node-version
or application defect from the warnings.

The official [Ubuntu 24.04 runner inventory](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md#android)
already supplies an Android SDK and `ANDROID_HOME`. The corrected APK workflow
uses that SDK's `cmdline-tools/latest/bin/sdkmanager` directly, checks executable
presence, accepts the required SDK licenses, and installs the same pinned API35,
build-tools35.0.0 and NDK28.2.13676358. This removes the failed second-SDK bootstrap
dependency. It preserves the native toolchain, source staging, signature, metadata,
ELF and alignment gates; no application/payment/device logic changes.

The same official sdkmanager license/package commands passed locally against
the retained SDK. Portable package/verifier group: **14 PASS, zero failures/errors/
skips**. Workflow YAML, all Bash run blocks and whitespace validation passed.
The prior 929-case application regression belongs to functional source `7d49f34`;
it is not relabelled as a fresh test of this workflow-only change. Hosted build
validation is required before claiming this correction produces an APK.

## Continuation and limits

Publish only the bounded workflow/docs change to the existing Android branch,
then use the registered manual `android-preview.yml` dispatch with `build_apk=true`.
Record the new exact source/run and actual final outcome. A dispatched/running
job is not a successful APK. Preserve all caches, app-private data and journals.
Actual Android camera/USB/media, merchant Sandbox, Drive/retention and installation
remain NOT_RUN. The [device checklist](device-acceptance.md) stays unchecked.

Rollback is a scoped inverse workflow commit; do not alter desktop/master,
credentials, payment or print journals. Local mirror and log-host access would
require separately reviewed network settings; none were changed here.

## Confirmed hosted outcome after the SDK correction

Source **0c0d66d361836030829c86eaef3555e887faf804** was pushed and its remote
SHA verified after the owner's explicit source-push/build approval. The manual
[run 40623523015](https://github.com/pratikto/PhotoBooth/actions/runs/40623523015)
has now completed. Its preview job is **SUCCESS**. The APK job passes native
prerequisite installation and packaging policy, confirming that the replacement
SDK bootstrap gets past the earlier failed setup step. The **Compile curated
Android v2 APK** step fails; signature/manifest/native-payload/alignment checks
are **SKIPPED**, not passed. The compile command also owns recipe downloads, so
this step outcome alone does not identify a C/Java compiler defect.

[Exact job outcomes](hosted-sdk-fix-jobs.json),
[artifact metadata](hosted-sdk-fix-artifacts.json) and
[structured status](hosted-sdk-fix-status.json) preserve the current observation.
The `meong-android-debug` artifact exists (147,301 bytes), but its name does not
prove that it contains an APK. Its contents have not been downloaded or inspected.

The detailed job-log route is blocked at
`results-receiver.actions.githubusercontent.com`. Artifact download independently
reaches `productionresultssa18.blob.core.windows.net`, also rejected with proxy
Forbidden. API annotations provide only exit code 1 and deprecation warnings;
the build's root error remains **UNKNOWN**. No application or recipe patch is
justified by that metadata alone, and the unchanged build has not been rerun.
Signed download URLs are deliberately excluded from this report.

The latest environment draft preserves all existing custom domains and adds
only these two observed evidence hosts plus the previously observed local
FreeType redirect host `ftp.cc.uoc.gr`. Saving the new requirements is confirmed;
it neither changes runtime access nor publishes the environment. After the user
reviews/saves these network additions and publishes, download **the existing**
run's artifact/log first, diagnose its actual error, and correct/retry only the
affected build. There is no need to rerun passing preview/application tests just
to retrieve existing evidence. No environment scripts, repository membership,
credentials or earlier setup changes were reapplied here.

No new runtime source was changed in this evidence-only continuation. Current
APK binary verification and physical Android/merchant/Drive acceptance remain
unverified. Earlier source-specific passes retain their exact scope and SHA.
