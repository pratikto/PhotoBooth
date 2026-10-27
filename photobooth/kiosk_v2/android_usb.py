"""Android UsbManager sender injected into the original ThermalPrinter.

No PyUSB/Linux node or Windows driver. The original durable PhotoTest journal
owns retries; this sender never retries a partial/ambiguous job.
"""
import time


def usb_context():
    from jnius import autoclass
    activity = autoclass('org.kivy.android.PythonActivity').mActivity
    return activity, activity.getSystemService('usb')


def find_device(manager, vendor, product):
    devices = manager.getDeviceList().values().iterator()
    selected = []
    while devices.hasNext():
        device = devices.next()
        if device.getVendorId() == vendor and device.getProductId() == product:
            selected.append(device)
    if len(selected) != 1:
        raise RuntimeError('Connect exactly one configured USB printer')
    return selected[0]


def request_usb_permission(vendor, product):
    from jnius import autoclass
    activity, manager = usb_context()
    device = find_device(manager, vendor, product)
    if not manager.hasPermission(device):
        intent = autoclass('android.content.Intent')(activity.getPackageName()+'.USB_PERMISSION')
        intent.setPackage(activity.getPackageName())
        pending = autoclass('android.app.PendingIntent')
        manager.requestPermission(device, pending.getBroadcast(activity, 0, intent,
            pending.FLAG_IMMUTABLE | pending.FLAG_UPDATE_CURRENT))


class UsbOtgSender:
    def __init__(self, vendor, product, *, context_factory=usb_context,
                 clock=time.monotonic):
        self.vendor, self.product = vendor, product
        self._context, self._clock = context_factory, clock

    def __call__(self, payload):
        _, manager = self._context()
        device = find_device(manager, self.vendor, self.product)
        if not manager.hasPermission(device):
            raise RuntimeError('USB printer permission required')
        # Select one bulk OUT interface/endpoint, never broadcast to devices.
        route = None
        for i in range(device.getInterfaceCount()):
            interface = device.getInterface(i)
            for j in range(interface.getEndpointCount()):
                endpoint = interface.getEndpoint(j)
                if endpoint.getType() == 2 and endpoint.getDirection() == 0:
                    route = (interface, endpoint)
                    break
            if route:
                break
        if route is None:
            raise RuntimeError('USB printer has no bulk OUT endpoint')
        interface, endpoint = route
        connection = manager.openDevice(device)
        if connection is None:
            raise RuntimeError('USB printer unavailable')
        claimed = False
        try:
            claimed = bool(connection.claimInterface(interface, True))
            if not claimed:
                raise RuntimeError('USB printer interface unavailable')
            offset, deadline = 0, self._clock()+120
            while offset < len(payload):
                if self._clock() >= deadline:
                    raise RuntimeError('USB job timed out; inspect physical paper')
                block = payload[offset:offset+16384]
                count = connection.bulkTransfer(endpoint, block, len(block), 5000)
                if count <= 0 or count > len(block):
                    raise RuntimeError('USB outcome uncertain; inspect physical paper')
                # A short positive transfer advances only the accepted prefix.
                offset += count
        finally:
            try:
                if claimed:
                    connection.releaseInterface(interface)
            finally:
                connection.close()
