# Thermal printer setup

The booth sends each saved result image as a monochrome ESC/POS raster. The
network transport is tried first when configured; USB is the fallback. The
purchased model is the **iWare/Barcodia J-82ULW**. The product image identifies
USB, Wi-Fi, and LAN; it supports 80 mm and 58 mm paper with a separator, and
has an auto cutter. Use the 80 mm roll for the booth's 80 × 240 mm photo strips.

## Dependencies

Install the repository dependencies:

    python -m pip install -r requirements.txt

The requirements file installs python-escpos with its USB extra. This supplies
ESC/POS raster encoding and the PyUSB dependency used by the USB transport.

## Wi-Fi: primary route

Connect the printer to the same Wi-Fi network as the booth computer. Print its
self-test/configuration page or check the router's DHCP client list to find its
current IP address. Reserve that IP in the router if possible, then configure
the shell that launches the booth:

    export PHOTOBOOTH_PRINTER_WIFI_HOST=192.168.1.50
    export PHOTOBOOTH_PRINTER_WIFI_PORT=9100
    export PHOTOBOOTH_PRINTER_WIFI_TIMEOUT=2

The app uses raw ESC/POS over TCP, with port 9100 as the default. The port is
configurable because the exact network settings should be confirmed from the
printer's self-test page or manual. The booth computer and printer must be on
the same reachable network.

If the TCP connection cannot be opened before a job starts, the app sends the
same prepared job through USB. If the network connection opens but the write
fails, the print state is uncertain, so automatic USB fallback is suppressed
to avoid a duplicate partial job. The result screen offers CETAK ULANG for a
deliberate retry.

## USB fallback

Connect the printer and run:

    lsusb

Find the printer's xxxx:xxxx vendor and product IDs. Configure both values in
the shell that launches the booth; use the four-digit hexadecimal values shown
by lsusb:

    export PHOTOBOOTH_PRINTER_USB_VENDOR_ID=xxxx
    export PHOTOBOOTH_PRINTER_USB_PRODUCT_ID=xxxx

The application passes those IDs to python-escpos. If native USB access fails
because of permissions, configure a udev rule for the exact VID/PID or use the
Linux device-node route below.

As a Linux alternative, the application uses /dev/usb/lp0 when it exists and
neither USB ID is configured. A different node can be selected with:

    export PHOTOBOOTH_PRINTER_USB_DEVICE=/dev/usb/lp1

The booth process needs permission to open the USB device. Prefer an
appropriate udev rule or system group over running the kiosk as root.

Other optional settings:

- PHOTOBOOTH_PRINTER_WIDTH_DOTS — maximum raster width; default 576, which
  matches a common printable area on an 80 mm printer. Set it to 384 for the
  narrower 58 mm roll, then verify the smaller QR on a physical sample.
- PHOTOBOOTH_PRINTER_USB_VENDOR_ID and PHOTOBOOTH_PRINTER_USB_PRODUCT_ID —
  both must be set together. Values are hexadecimal, as printed by lsusb.
- PHOTOBOOTH_PRINTER_USB_DEVICE — Linux file-device fallback; default
  /dev/usb/lp0.

The network connection uses no acknowledgement protocol. A “data terkirim”
status means the job bytes were accepted by the OS socket or USB driver; the
app cannot confirm paper movement, print darkness, or cutter operation without
a physical test print.
