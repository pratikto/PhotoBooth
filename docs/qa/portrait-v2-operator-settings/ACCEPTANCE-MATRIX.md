# GUI v2 Operator Settings — acceptance, failure-injection and security matrix

**Status: PLANNED / ALL TESTS NOT_RUN as of 29 October 2026.** This is the owner-approved future design's mandatory acceptance contract, **not execution evidence**. Do not run OPS work ahead of **AR-00–AR-13**; follow the [master specification](README.md), [OPS roadmap](IMPLEMENTATION-ROADMAP.md), and current [AR checkpoint](../portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

### Evidence policy

For each test attach **actual** command/fixture, test source SHA, OS/backend/Kivy version, pass/fail/skip/not-run, native capture where applicable, real device/printer/merchant-mode identity (without secrets), regression impact, and reviewer. Pure mocked unit PASS does **not** prove physical paper, camera phone-scan, Android permission, installed Ubuntu startup, merchant validation or production security. An unimplemented feature remains NOT_RUN even if its contract exists in docs.

Definitions: **ADVERT** = first advertising page; **SAFE_IDLE** = authoritative live-service ownership check; **OPS** = Settings-only operator auth; **AR-09** = separate protected financial operator exception route; **visit** = durable logical customer session (may survive app restart, not merely a fresh page render); **DEMO** = local/Mock-only simulation, never proof of merchant payment or receipt.

## A. Navigation, SAFE_IDLE and AR-09 coexistence

| ID | Case / stimulus | Required outcome |
| --- | --- | --- |
| NAV-01 | First Advertising page + true SAFE_IDLE + existing F12 | Operator QR Login opens, never full Settings immediately |
| NAV-02 | First Advertising + SAFE_IDLE + 1.5s Meong header hold | Operator QR Login opens once; one sound cue |
| NAV-03 | Header short tap, movement > threshold, right click or incidental swipe | No login, no blocked customer input |
| NAV-04 | Face invitation appears during held header | Race invalidates operator entry; invitation/customer safety wins deterministically |
| NAV-05 | Face Invitation visible | Login forbidden |
| NAV-06 | Tutorial and Template Carousel | Login forbidden even with F12/secret hold |
| NAV-07 | Meong Fly preview, receipt, gameplay and result | Login forbidden in every state |
| NAV-08 | Local Mock pending/unknown/admitted checkout | Login forbidden |
| NAV-09 | Midtrans Sandbox PENDING, UNKNOWN, PAID and live RECOVERY | Full Settings forbidden |
| NAV-10 | Photo Confirm/Capture/Review/Result | Login forbidden; no lost capture/retake entitlement |
| NAV-11 | Advertising shown while old live customer still owns booth lease | Login forbidden until verified safe isolation |
| NAV-12 | Ad page + independently isolated old recovery or pending Drive upload | Login allowed only if SAFE_IDLE authoritatively true; background jobs continue unchanged |
| NAV-13 | Pending print or active photo write with uncertain outcome | Login forbidden when same local resource/lease is owned; no automatic replay |
| NAV-14 | Login QR becomes valid just as customer starts new visit | Recheck page/generation/SAFE_IDLE; reject late auth |
| NAV-15 | Login QR becomes valid after leaving Advertising | Reject, no return to Settings by stale callback |
| NAV-16 | Existing AR-09 backend operator PIN inspect/release in RECOVERY | Remains separately authenticated/audited; QR Settings cannot call or bypass it |
| NAV-17 | AR-09 safe release completes and displays Advertising | SAFE_IDLE derived from actual fence/ACK before login; preserve original customer recovery rights |
| NAV-18 | Close/login cancel on a true safe idle booth | Return to ordinary Advertising; next tap/invitation works |

## B. Static operator QR, security and offline provisioning

| ID | Case / stimulus | Required outcome |
| --- | --- | --- |
| AUTH-01 | Provision random QR for Booth A, scan at Booth A while SAFE_IDLE | Authenticates Settings, only the three Settings tabs |
| AUTH-02 | Scan Booth A operator QR at Booth B | Rejected; no shared global credential |
| AUTH-03 | Scan QRIS payment QR, photo download QR, Recovery Ticket | Each rejected; no secret contents printed |
| AUTH-04 | Scan Merchant Promo / Meong Fly DEMO ticket in operator scanner | Rejected even if its QR is otherwise readable |
| AUTH-05 | Scan random plaintext, malformed code, unsupported version | Rejected with neutral message |
| AUTH-06 | Reuse valid static operator QR for second legitimate login | Accepted until operator credential is rotated/revoked |
| AUTH-07 | Rotate Booth A secret; rescan prior secret and new secret | Old rejects, new works; Booth B unaffected |
| AUTH-08 | Revoke secret, restart, attempt prior QR | Prior secret still rejects; no anonymous fallback |
| AUTH-09 | Local verification configuration missing/corrupt | Fail closed; OS maintenance remains possible |
| AUTH-10 | Scan while offline/unplugged network | Booth-bound local static credential still works; no Internet auth requirement in dev |
| AUTH-11 | Twenty fast wrong-code/ambient QR frames and a valid scan | Bounded throttle; no CPU exhaustion or permanent lockout for authorized operator |
| AUTH-12 | Logs, crash report, test capture, diagnostics, clipboard, root Git | No raw operator QR/token or recoverable secret |
| AUTH-13 | Auth success then full menu close | Session immediately revoked; no persisted “logged in” bit |
| AUTH-14 | Auth success then 3 min without interaction | Automatic logout; background poll not treated as interaction |
| AUTH-15 | Auth success then minimize, close or process restart | Session revoked; no Settings auto-open on resume |
| AUTH-16 | Valid login QR while camera fails | Cannot bypass using visible PIN; safe OS-authenticated maintenance path documented and tested |
| AUTH-17 | Tamper booth/config binding or local auth verifier | Reject without altering financial records |
| AUTH-18 | Login request while ordinary customer action/camera worker busy | No camera racing, no privilege escalation or worker teardown |

## C. QR camera scanner, advertisement/sensor/audio lifecycle

| ID | Case / stimulus | Required outcome |
| --- | --- | --- |
| SCAN-01 | Live preview displays front-camera frame | Preview mirrored, raw frame decoded in correct orientation |
| SCAN-02 | Phone QR appears in scan box, different positions/orientations | Auto-decode once; no manual frame capture needed |
| SCAN-03 | Tiny, oversaturated, glare, dark or unfocused phone QR | Bounded retry tips; no crash or busy-loop |
| SCAN-04 | Bad QR code read repeatedly at 5–10 fps proposal | Work throttled, no runaway threads/DB writes |
| SCAN-05 | Another device asks for camera while scanner owns mailbox | One existing camera manager; no second camera open |
| SCAN-06 | Operator Cancel/Back during decode | Scanner retired; no stale authentication |
| SCAN-07 | Scanner timeout without success | Return Advertising and restore ads/sensors/music |
| SCAN-08 | Video advertisement + music owns output when secret action triggered | Ad video and audio safely suspended once; no double media loop |
| SCAN-09 | Face stays in front of booth for 5 s while login scanning | Face Invitation does not overtake operator login |
| SCAN-10 | Login scan succeeds then app suspends immediately | Session revoked; scanner closes, no Settings leak |
| SCAN-11 | Valid payload late callback after cancellation/logout/new visit | Ignored by generation/lease checks |
| SCAN-12 | Return to Advertising and enter customer photo flow | Camera remains usable, preview mirror preserved, original capture unmirrored |
| SCAN-13 | Android tablet rotates/minimizes/denies permission (future device) | Bounded failure and recovery; do not assume desktop event semantics |
| SCAN-14 | Wrong namespace scanned via promo/game scanner | Rejected without reopening operator auth or customer photo |

## D. Device Health preservation

| ID | Case / stimulus | Required outcome |
| --- | --- | --- |
| DH-01 | Authenticated Device Health tab opens | Original read-only panel/checks reused; no new hardware ownership |
| DH-02 | Refresh and rapid mixed taps (BUG-018 regression) | One bounded worker; no hang or orphan popup |
| DH-03 | Probe fails, printer unplugged, camera unavailable | Honest Warning/Error/Unknown rather than fabricated Ready |
| DH-04 | Save local diagnostic report | Atomic allowlisted report, zero secrets/photos/order refs |
| DH-05 | Copy Diagnostic Report convenience feature | Clipboard contains only safe allowlisted text, no raw PII |
| DH-06 | Attempt disabled device selection/staging | Cannot change camera/printer route or hot-swap |
| DH-07 | Close/minimize while health result pending | Old callback ignored; next real operator/customer action responsive |
| DH-08 | Operator report says LAN reachable/print queued | UI never misstates physical paper or Midtrans authorization as verified |
| DH-09 | Enter from old protected RECOVERY exception path | Dedicated AR-09 controls remain separate, full Settings not exposed |
| DH-10 | Ad playback with active safe background Drive | Health observation cannot cancel/cloud-delete/rebind Drive jobs |

## E. Audio Mixer + persistence

| ID | Case / stimulus | Required outcome |
| --- | --- | --- |
| AUD-01 | Set Master to 0/50/100% | Gain bounded, multiplies configured buses without OS global audio hijack |
| AUD-02 | Set Music without changing others | GUI BGM and game loop respect requested bus; button/other unaffected |
| AUD-03 | Set Button SFX to 0% | Click sounds silent; other effects and music keep own gain |
| AUD-04 | Set Other SFX to 0% | Shutter/countdown/notifications/game effects obey bus without affecting normal BGM |
| AUD-05 | Mute then unmute | Silence then restore prior four slider values |
| AUD-06 | Test Sound on each category | Bounded single preview, no real shutter/charge/game result |
| AUD-07 | Rapid slider dragging and tab switch | No repeated track restarts, runaway writes or overlapping playback |
| AUD-08 | Save preferences then restart (same Booth ID) | Persistent exact bounded values, no reset |
| AUD-09 | Open another booth config | Independent volume values, no cross-booth state leak |
| AUD-10 | Corrupt/partial config and invalid numeric value | Atomic/fallback defaults and clamping; kiosk opens |
| AUD-11 | Still advertising media and video ad alternation | Keep correct video-own-audio versus GUI BGM owner, no two tracks |
| AUD-12 | Game intro/receipt/play/result and transition to Template | Correct distinct game loop and main GUI music handoff |
| AUD-13 | Minimize/close/return from QR login | Audio lifecycle suspends/resumes only through owner, no Windows mixer stuck-muted |
| AUD-14 | Missing WAV provider/asset | Error reported safely, no locked page or unexpected full app failure |
| AUD-15 | Slider labels on 800×1280 / 452×900 | Accessible/touchable numeric percentages, scroll/clip correct |
| AUD-16 | Master 100% + bus 100% with normal asset audio | No uncontrolled digital gain above documented safe ceiling |

## F. Emulate Ticket — Merchant Promo DEMO

| ID | Case / stimulus | Required outcome |
| --- | --- | --- |
| PROMO-01 | Open Emulate Ticket then select Merchant Promo | Correct static demo identity, distinct from operator login/recovery/payment |
| PROMO-02 | Reopen Eligible preset 10 times, restart, print multiple times | Encoded static QR payload identical across repeats |
| PROMO-03 | Scan eligible mocked merchant receipt >= illustrative threshold | One valid eligibility verdict, one base-fee waiver in the same MOCK visit |
| PROMO-04 | Scan valid below-threshold ticket | Valid receipt syntax but ineligible; no discount |
| PROMO-05 | Scan invalid/foreign/unsupported version | Rejected; no payment/discount |
| PROMO-06 | Scan eligible ticket twice in same visit | At most one promo consumption; no duplicate waiver |
| PROMO-07 | Repeat after app restart within same logical visit | Still one claimed promo; no ledger reset |
| PROMO-08 | New independent local test visit | Same static DEMO QR permitted according to one-per-visit test contract |
| PROMO-09 | Apply merchant promo then attempt Meong Fly Rp2,500 discount stacking | Initial no-stacking rule enforced; no silent sum |
| PROMO-10 | Eligible QR in actual Midtrans Sandbox / production gateway | No trusted server discount or quote mutation |
| PROMO-11 | Two design templates / 1–9 copies scenario | Only allowed illustrative base fee affected; print fees untouched |
| PROMO-12 | Malformed amount, huge/negative value, mismatched merchant, cross booth | Fails closed; server-authorized quote never derives from untrusted QR amount |
| PROMO-13 | Two concurrent scanner callbacks | Single atomic effect and durable event |
| PROMO-14 | History review | Safe verdict/visit identity, not raw receipt PII or merchant credential |

## G. Emulate Ticket — Meong Fly DEMO

| ID | Case / stimulus | Required outcome |
| --- | --- | --- |
| FLY-01 | Valid static game QR in fresh Mock/DEMO visit A | Exactly one admission, original Meong Fly starts |
| FLY-02 | Same QR scanned again before first attempt completes | Denied as already claimed in A |
| FLY-03 | Same QR after win/loss/exit in A | Denied; no MAIN LAGI |
| FLY-04 | App restart after first A claim, before result | Preserves A consumption; no new attempt |
| FLY-05 | A returns after safe recovery and scans same QR | Still consumed; A not redefined as new visit |
| FLY-06 | Separate genuinely new visit B scans same QR | One fresh permitted attempt in B |
| FLY-07 | Already Used preset selected | Test genuinely rescanning previously accepted QR; no QR with fake “USED” content |
| FLY-08 | Invalid entry/merchant promo/operator/recovery QR in game scanner | Rejected without game starting |
| FLY-09 | Multiple rapid valid frames/callbacks | Exactly one durable claim, one game engine |
| FLY-10 | Win game, no merchant promotion | Existing local MOCK Rp2,500 reward once, continue to Template |
| FLY-11 | Lose game / abandon game | No reward; continue according to original flow |
| FLY-12 | Existing original `DEMO-` manual one-use claim path | Existing irreversible one-use ledger remains supported and unchanged |
| FLY-13 | DB exception during claim/commit | No duplicate opportunity; safe retry/reconciliation |
| FLY-14 | Quit/switch page during game | Original physics/timer/music and no-second-attempt invariants preserved |
| FLY-15 | Game static QR decoded in a production path | Rejected; no real merchant game entitlement |

## H. Printing, QR validity, history, device and release

| ID | Case / stimulus | Required outcome |
| --- | --- | --- |
| PRINT-01 | Select DEMO preset and preview | Correct category, DEMO label, normal unmirrored scannable QR |
| PRINT-02 | Print same static ticket twice deliberately | QR payload identical, each print event distinctly tracked |
| PRINT-03 | Press Print rapidly 20 times while busy | Bounded/disabled action; no uncontrolled printer job burst |
| PRINT-04 | Printer unset or offline | PREVIEW ONLY / explicit unavailable error, no false Printed |
| PRINT-05 | Printer transport succeeds | Report SENT/QUEUED, not physically verified paper |
| PRINT-06 | Process exit before send/after partial bytes/after ACK before result | Durable attempt replay protection; UNCERTAIN never silently reprinted |
| PRINT-07 | Printer recovers after uncertain send | Needs deliberate safe inspection/action, not auto replay |
| PRINT-08 | QR printed on 80 mm actual thermal paper, phone scans | Same category/payload as preview, 4-module quiet zone and readable contrast |
| PRINT-09 | Printing DEMO while customer print/recovery queued | No competing queue side effect or high-priority starvation |
| PRINT-10 | Run dedicated Midtrans Sandbox launcher | Physical printer still explicitly OFF; no DEMO feature backdoor |
| PRINT-11 | Attempt to print operator secret or private recovery ticket from Emulate Ticket | Rejected: only DEMO categories selectable |
| PRINT-12 | Ticket/test history list and DEMO cleanup | Nonsecret bounded status; no deletion of finance/customer/media records |
| PRINT-13 | Photo strip generator, Drive QR, QRIS Payment Slip source | No accidental change in contents, orientation, payment order or copy count |
| PRINT-14 | Printer LAN, Wi-Fi and Windows USB configured (where existing service supports) | Reused transport; identical correct QR payload; no new driver path |
| QA-01 | Screenshot two portrait sizes of all three tabs and scanner/errors | No clipping, safe QR preview, touch targets responsive |
| QA-02 | Windows physical camera/laptop demo acceptance | Actual result/equipment/source documented, not inferred from mock |
| QA-03 | Ubuntu mini-PC real sound/camera/print acceptance | Separate installed-run evidence, no claimed result before run |
| QA-04 | Tablet Android camera direction, permissions, decode performance | Separate future device gate, not assumed to pass |
| QA-05 | Full applicable test runner at final functional SHA | Actual PASS/FAIL/SKIP and CI alignment recorded |
| QA-06 | Force restart in SETTINGS and midscan | No persisted operator session; protected AR ledgers intact |
| QA-07 | Open user Capture/Payment while scan intent still pending | Race protected; customer workflow controls preserved |
| QA-08 | Attempt invalid QR after several successful scans | No role confusion, secret leak, scanner misclassification |
| QA-09 | Compare source to AR-00–AR-13 final snapshot | No privacy/payment/print/retention invariant regressed |
| QA-10 | Report owner go/no-go | No deployment/production/`master` transition without separate explicit approval |

---

## Fault-injection minimum matrix

| Boundary | Inject | Required durable outcome |
| --- | --- | --- |
| Static operator provision | Crash during config write | Old valid config or failed closed; no half-config anonymous auth |
| Operator rotate | Crash after hash persisted before handoff | Old/new validity explicitly deterministic, recovery through OS-authenticated maintenance only |
| Scanner | Camera loss, frame stall, stale decode callback | No late auth, no leaked old frame/gesture |
| Visit admission | Two QR scans before SQLite commit | Single visit-scoped entry/promo claim; next valid visit distinct |
| Meong Fly | Crash before/after consumption commit | Original attempt state reconstructed or held; never second chance same visit |
| Promo | Crash between validation and quote snapshot | No double discount and no unverified Midtrans amount |
| Audio | Crash during atomic local config replace | Valid prior or new config; no corrupted startup crash |
| Print | Before-send, partial send, after-ACK before journal update | No blind duplicate print; uncertain quarantined for operator |
| Recovery isolation | Background old payment/Drive continues while Settings open | Isolation and tokens preserved; never exposed to operator demo |
| Production fence | Present valid static DEMO QR to production endpoint | Rejected on backend; not merely hidden in GUI |

### Exit rule

OPS implementation cannot be marked VERIFIED solely by passing unit tests. Actual device and integration evidence must be truthfully separated from source tests. **Every test in this file starts NOT_RUN; this documentation commit does not execute or satisfy any case.** Keep the AR-00–AR-13 test matrix authoritative and unaffected by the OPS suite.
