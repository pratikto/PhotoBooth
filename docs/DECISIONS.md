# Meong Photobooth — Decision record

Last updated: 2026-10-17. Each item records an agreed product direction or current technical boundary. It does **not** certify that every feature is bug-free.

| Decision | Rationale / consequence |
| --- | --- |
| Continue GUI development on **`feature/kivy-gui`**, without creating a new branch | Keeps the user's established GitHub workflow and history |
| Use Kivy for the active GUI; retain older Tkinter code only as historical implementation | Controller logic is separated from presentation |
| Preserve the finalized bright Meong cat-camera logo and colorful, elegant UI | Consistent brand across pages and folder QR |
| Keep 12 approved 80 mm templates and price Rp5,000/session | One quantity unit is an independent three-photo session |
| Support both face invitation and always-visible manual Start on idle ads | Non-camera fallback remains accessible |
| Face hold 5 s; invitation expires in 15 s; cooldown default 45 s | Avoid disruptive repeated prompts; settings are configurable |
| Change requested journey to **ad -> tutorial -> layout selection** | Tutorial must not be skipped by Start; source navigation now enforces the guide for manual and face-triggered entry, pending device verification |
| Idle ads may play source-video sound; payment ad video is always muted | Avoid competing with application music and preserve payment clarity |
| Keep music and interaction sounds on photography pages with separate user controls | Mute/volume settings should survive restart |
| Separate payment QR from transaction-folder access QR | Payment and retrieval are different functions |
| Keep QRIS explicitly non-payable until verified provider integration exists | A demo click, printed QR or screenshot is not proof of payment |
| Offer optional payment QR printing without blocking the visible QR; offer dismisses after 15 s | Assists users who cannot scan the display; does not change payment status |
| Target local photo retention 15 days and Drive retention 30 days | Storage housekeeping must respect transaction lifecycle and remote setup |
| Keep LAN payment slip separate from thermal **photo** printing work | Avoid silently mixing GUI and printer-branch changes |
| Document architecture, decisions, feature status and next steps in-repo | Makes continuation possible when a ChatGPT conversation/model reaches limits |
| Keep source comments explanatory and detailed, in English | Easier maintenance and handover |

## Open decisions / verification

- Exact final dimensions for the enlarged idle video should be adjusted and checked at 800×600, 1200×800 and 1920×1080, without distorting aspect ratio.
- Confirm video compatibility with the machine's installed codecs/SDL/Kivy environment and local playlist paths.
- Confirm the final tutorial navigation for automatic face-offer acceptance, manual Start, and return/back buttons.
- Choose and integrate a real payment provider only when ready; never auto-enable real payment from a demo.
