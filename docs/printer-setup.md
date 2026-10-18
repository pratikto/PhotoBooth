# Thermal printer setup

> **CURRENT operational baseline (2026-10-19, `feature/kivy-gui`):** The source on **`feature/kivy-gui`** supports photo strips and DEMO payment QR-slip printing through the saved GUI `PrinterConfig`, including Windows RAW ESC/POS, LAN and Wi-Fi. The owner confirmed **FEAT-001 price and BUG-011 actual multi-copy count PASS on Windows** and reported Floyd image quality / QR paper output PASS (BUG-004/003). This is not independent QA of every width, driver or phone QR scan. Floyd–Steinberg with the **owner-selected photo preprocessing** is the active default; `PHOTOBOOTH_PHOTO_TUNING=legacy` is an explicit fallback. Earlier stage references to only `feature/thermal-printer` and RAW printing untested are **HISTORICAL / SUPERSEDED**.

The booth prints each saved result image as a monochrome ESC/POS raster. Photo
tones use Floyd–Steinberg dithering by default; Bayer ordered dithering and a
plain threshold are also available for comparison. The purchased printer is
the iWare/Barcodia J-82ULW. Its product listing identifies
USB, Wi-Fi, and LAN, with 80 mm and 58 mm paper support and an auto cutter.
Use the 80 mm roll for the booth's 80 × 240 mm photo strips.

## Recommended connection order

The app tries each configured route in this order:

1. LAN — preferred for a fixed booth because the cable provides a stable link
   without Wi-Fi credentials.
2. Wi-Fi — useful when wiring is inconvenient or the booth is moved.
3. USB — last-resort local connection.

Each route is optional. An empty host is skipped. If every configured network
connection fails before it opens, the app tries the next configured route. If a
connection opens and then sending fails, the print status is uncertain and
automatic retry is suppressed to avoid duplicate or partial receipts. The
result screen offers CETAK ULANG for a deliberate retry.

## Printer IP and web configuration

Connect the printer and booth computer to the same local network. The IP
address is used by the browser to open the printer's configuration page, when
that page is available on the selected interface. Reserve the printer's address
in the router's DHCP settings if possible so it does not change unexpectedly.

The browser configuration page is for printer administration. The booth sends
print data separately as raw ESC/POS over TCP, usually to port 9100. Confirm the
actual print port from the printer's self-test/configuration page or manual;
the app keeps the port configurable.

## LAN route: preferred

Connect the printer's Ethernet port to the router or booth network. Find the
LAN IP from its self-test/configuration page or from the router's DHCP client
list. Configure that IP in the environment that launches the booth:

### Windows PowerShell

    $env:PHOTOBOOTH_PRINTER_LAN_HOST = "192.168.1.50"
    $env:PHOTOBOOTH_PRINTER_LAN_PORT = "9100"

### Linux or macOS shell

    export PHOTOBOOTH_PRINTER_LAN_HOST=192.168.1.50
    export PHOTOBOOTH_PRINTER_LAN_PORT=9100

If the printer and computer are on different network segments, routing and
firewall rules must allow the booth computer to reach the printer's print port.

## Wi-Fi route: secondary

Set up the printer's Wi-Fi connection using the printer's own configuration
page or setup utility. Entering the SSID and password is a printer setup step;
the Python booth application does not need those credentials and does not
reconfigure the printer each time it prints.

When the booth is used on a different Wi-Fi network, configure that network on
the printer once and set its Wi-Fi IP below. If the Wi-Fi network and password
stay the same, there is no need to repeat the setup. Find the Wi-Fi IP from the
printer's configuration page or router's DHCP client list.

### Windows PowerShell

    $env:PHOTOBOOTH_PRINTER_WIFI_HOST = "192.168.1.51"
    $env:PHOTOBOOTH_PRINTER_WIFI_PORT = "9100"

### Linux or macOS shell

    export PHOTOBOOTH_PRINTER_WIFI_HOST=192.168.1.51
    export PHOTOBOOTH_PRINTER_WIFI_PORT=9100

LAN and Wi-Fi are different network interfaces and can have different IP
addresses. Set each host only after confirming that the printer accepts jobs
on that interface. If only Wi-Fi is configured, it is tried first because the
LAN route is skipped.

## USB route: final fallback

The USB route is OS-dependent. The current ESC/POS adapter uses the printer's
USB vendor/product IDs through PyUSB, or the Linux device file
/dev/usb/lp0 when it exists. Find the USB IDs on Linux with:

    lsusb

Then configure both hexadecimal IDs:

    export PHOTOBOOTH_PRINTER_USB_VENDOR_ID=xxxx
    export PHOTOBOOTH_PRINTER_USB_PRODUCT_ID=xxxx

On Linux, if native USB access fails because of permissions, configure a udev
rule for the exact IDs or use an appropriate system group. The optional Linux
device-node path can be changed with:

    export PHOTOBOOTH_PRINTER_USB_DEVICE=/dev/usb/lp1

Windows does not have the Linux /dev/usb/lp0 device file. The USB-ID route may
need a compatible PyUSB backend and device driver, so test that fallback on the
target Windows PC before relying on it. On Android, USB host support and app
permissions also require device-specific validation. This platform variance is
why network printing is preferred for the Windows, Linux SBC/mini PC, and
Android rollout.

## Other settings

- PHOTOBOOTH_PRINTER_NETWORK_TIMEOUT — timeout in seconds for each network
  connection and write; default 2.0.
- PHOTOBOOTH_PRINTER_WIFI_TIMEOUT — legacy alias used only when the new common
  network timeout is not set.
- PHOTOBOOTH_PRINTER_WIDTH_DOTS — maximum raster width; default 576, which
  matches a common printable area on an 80 mm printer. Set it to 384 for the
  narrower 58 mm roll, then verify the QR code on a physical sample.
- PHOTOBOOTH_PRINTER_USB_VENDOR_ID and PHOTOBOOTH_PRINTER_USB_PRODUCT_ID —
  both must be set together. Values are hexadecimal.
- PHOTOBOOTH_PRINTER_USB_DEVICE — Linux file-device fallback; default
  /dev/usb/lp0.
- PHOTOBOOTH_PRINTER_DITHER — image conversion method: `floyd-steinberg`
  (default), `bayer`, or `threshold`. Changes apply after restarting the app.
- PHOTOBOOTH_PRINTER_THRESHOLD — grayscale cutoff from 0 to 255 for the
  `threshold` method; default 128. A higher value prints more pixels as black.
  This setting does not change Floyd–Steinberg or Bayer output.

## Compare the three image methods

To compare output on the same saved composition, run the helper with a PNG
from a completed session. It sends three separate jobs, each labeled above the
image, in this order: Floyd–Steinberg, Bayer, then threshold. It stops if a
print fails, so check the printer before deliberately running it again.

    python tools/print_dither_comparison.py "photos/PB001_00000001/output/session_01/template_a.png"

Replace the example path with the actual saved result path. Configure the
printer connection and width first; for an 80 mm roll, 576 dots is the default,
while a 58 mm roll commonly uses 384 dots. The app's normal automatic print
continues to use the configured `PHOTOBOOTH_PRINTER_DITHER` mode.

Install the repository dependencies before running the app:

    python -m pip install -r requirements.txt

The network connection has no acknowledgement protocol. A “data terkirim”
status means the job bytes were accepted by the OS socket or USB driver; the
app cannot confirm paper movement, print darkness, or cutter operation without
a physical test print.

## Windows USB printing through the installed POS80ENG driver

On the tested PC, Device Manager reports Caysn IW-J82ULW with
`USB\\VID_4838&PID_3830`; Windows shows `POS80 Printer` and
`POS80 Printer(2)`, driver `POS80ENG`, port `USB001`. A normal
Windows `Out-Printer` text test historically succeeded. **CURRENT:** the owner subsequently confirmed physical RAW ESC/POS copy-count behavior on Windows (BUG-011 OWNER TESTED PASS); the precise local queue, firmware, and 1/2/3 cut-sheet matrix were not provided, so full driver compatibility across configurations remains unverified.

The **current `feature/kivy-gui` branch** supports a named Windows
spooler queue; the older `feature/thermal-printer` branch remains an archived reference. This avoids replacing the installed USB driver. In PowerShell:

```powershell
python -m pip install pywin32
python tools/test_usb_raw_windows.py --printer "POS80 Printer"
# Optional: --cut to test the cutter only after ordinary printing succeeds
```

If the working queue is the second entry, specify `--printer "POS80 Printer(2)"`.
A successful command means Windows accepted RAW bytes, not that a physical
receipt printed. Check paper before retrying. For actual photo printing in the
application, set the queue explicitly (restart the app after setting it):

```powershell
$env:PHOTOBOOTH_PRINTER_WINDOWS_NAME = "POS80 Printer"
```

Install `pywin32` in the active Windows virtual environment. Network routes
retain their priority; leave LAN and Wi-Fi host settings blank when testing USB.
On non-Windows systems, existing PyUSB/Linux device-file behavior is unchanged.
The print width and three dithering modes remain configurable as above.

## Controlled 80 mm dither comparison over Windows USB

With the existing POS80ENG queue configured, the comparison helper can first
write safe, paper-free previews, or submit **one** labeled test job at a time.
It reuses the identical resize, alpha compositing, width and dithering logic
used in the production printer adapter.

```powershell
$env:PHOTOBOOTH_PRINTER_WINDOWS_NAME = "POS80 Printer"
Remove-Item Env:PHOTOBOOTH_PRINTER_LAN_HOST -ErrorAction SilentlyContinue
Remove-Item Env:PHOTOBOOTH_PRINTER_WIFI_HOST -ErrorAction SilentlyContinue
$env:PHOTOBOOTH_PRINTER_WIDTH_DOTS = "576"
python tools/print_dither_comparison.py "path\\to\\result.png" --preview-dir previews
python tools/print_dither_comparison.py "path\\to\\result.png" --mode floyd-steinberg
python tools/print_dither_comparison.py "path\\to\\result.png" --mode bayer
python tools/print_dither_comparison.py "path\\to\\result.png" --mode threshold
```

Replace the path with a real photo composition, and check each physical job
before proceeding to the next. The script's original mode without flags still
sends all three prints, which uses more paper. The preview option **never**
opens a printer connection. Queue acceptance is not confirmation of print
quality, legibility or cutter behavior; do not retry blindly after partial output.

## Current GUI printer settings — in Kivy; specific device test evidence remains separate

On branch `feature/kivy-gui`, use the gear icon in the Kivy header,
choose **PENGATURAN PRINTER**, then select **USB Windows**, **LAN**, or **Wi-Fi**.
The popup lets the operator edit the Windows queue name (for example,
`POS80 Printer`), network IP and TCP port, 576/384-dot print width, and
Floyd–Steinberg/Bayer/threshold dithering. Save to apply to new print jobs;
settings persist under ignored `data/printer_settings.json` across restarts.
Only the selected route is activated; switching from LAN to USB clears the
active network hosts to prevent accidental duplicate connection attempts.
The app does not store the Wi-Fi SSID/password.

**TEST PRINT** intentionally uses the *last saved* configuration. It sends a
short ESC/POS test receipt from a worker thread so the UI remains responsive.
It is an operator-initiated action and should be used only with the printer
connected and paper loaded. A positive message confirms job submission, not
verified paper output. **The owner confirmed actual paper copy-count PASS in the normal photo flow**; that does not by itself confirm this dedicated settings TEST PRINT button on every route.
Windows USB uses the existing `POS80ENG` driver and requires `pywin32`.

The existing music Settings remains under **PENGATURAN AUDIO** in the same
gear menu. Saved printer config is separate from application audio settings.

Tests: `python -m unittest tests.test_printer_settings -v`.
**Acceptance separation:** owner-tested Windows photo printing / copy count is PASS; full width/network-route, QR phone-scannability, spool-error and cutter acceptance remains separately unverified. See [QA checklist](test_checklist.md).
