"""Trusted optional child startup bundle; never customer HTTP or a mode toggle."""
from dataclasses import dataclass,asdict,fields
import re

from photobooth.printer import PrinterConfig,DITHER_MODES
from photobooth.post_preview_readiness import finite_number
from photobooth.post_preview_worker_fence import WorkerFenceKey


@dataclass(frozen=True,repr=False)
class SandboxHostFulfillment:
    printer_config: PrinterConfig
    worker_key: WorkerFenceKey
    durable_worker_epochs: bool = False
    recovery_operation: str | None = None

    def __post_init__(self):
        if (type(self.printer_config) is not PrinterConfig or type(self.worker_key) is not WorkerFenceKey
                or type(self.durable_worker_epochs) is not bool
                or self.recovery_operation is not None and (type(self.recovery_operation) is not str
                    or re.fullmatch(r'[a-f0-9]{32}',self.recovery_operation) is None or self.durable_worker_epochs)):
            raise ValueError('Exact private original fulfillment dependencies required')
        validate_original_printer_config(self.printer_config)

    def __repr__(self):
        return '<SandboxHostFulfillment: private original child dependencies>'

    def to_private_startup(self):
        """Only for the original anonymous startup socket; never log/persist."""
        value = dict(version=1,printer=asdict(self.printer_config),
                    worker_key=dict(key_id=self.worker_key.key_id,secret_hex=self.worker_key.secret.hex()))
        if self.durable_worker_epochs: value['durable_worker_epochs'] = True
        if self.recovery_operation is not None: value['recovery_operation'] = self.recovery_operation
        return value

    @classmethod
    def from_private_startup(cls,value):
        try:
            if (type(value) is not dict or set(value) not in (
                    {'version','printer','worker_key'}, {'version','printer','worker_key','durable_worker_epochs'},
                    {'version','printer','worker_key','recovery_operation'})
                    or type(value.get('durable_worker_epochs',False)) is not bool
                    or 'recovery_operation' in value and (type(value['recovery_operation']) is not str
                        or re.fullmatch(r'[a-f0-9]{32}',value['recovery_operation']) is None)
                    or type(value['version']) is not int or value['version']!=1
                    or type(value['printer']) is not dict
                    or set(value['printer'])!={f.name for f in fields(PrinterConfig)}
                    or type(value['worker_key']) is not dict
                    or set(value['worker_key'])!={'key_id','secret_hex'}
                    or type(value['worker_key']['secret_hex']) is not str
                    or re.fullmatch(r'[a-f0-9]{64}',value['worker_key']['secret_hex']) is None):
                raise ValueError
            printer=PrinterConfig(**value['printer'])
            bundle=cls(printer,WorkerFenceKey(value['worker_key']['key_id'],
                                           bytes.fromhex(value['worker_key']['secret_hex'])),
                       value.get('durable_worker_epochs',False),value.get('recovery_operation'))
            # Original permissive printer normalization is for legacy settings.
            # This private protocol requires exact typed values, no fallbacks.
            actual=asdict(printer)
            if any(type(actual[k]) is not type(v) or actual[k]!=v for k,v in value['printer'].items()):
                raise ValueError
            return bundle
        except (ValueError,TypeError,KeyError):
            raise ValueError('Exact private original fulfillment bundle required') from None


def validate_original_printer_config(config):
    """Pure original configuration policy; never mint a worker capability."""
    if type(config) is not PrinterConfig:
        raise ValueError('Exact private original fulfillment dependencies required')
    for host in (config.lan_host,config.wifi_host):
        if type(host) is not str or host and re.fullmatch(r'[A-Za-z0-9.-]{1,253}',host) is None:
            raise ValueError('Bounded original printer configuration required')
    if (any(type(port) is not int or not 1<=port<=65535 for port in (config.lan_port,config.wifi_port))
            or not finite_number(config.network_timeout) or not .1<=config.network_timeout<=30
            or type(config.windows_printer_name) is not str or len(config.windows_printer_name)>256
            or any(ord(c)<32 or ord(c)==127 for c in config.windows_printer_name)
            or any(value is not None and (type(value) is not int or not 1<=value<=65535)
                   for value in (config.usb_vendor_id,config.usb_product_id))
            or (config.usb_vendor_id is None)!=(config.usb_product_id is None)
            or config.usb_device_path is not None and (type(config.usb_device_path) is not str
                or re.fullmatch(r'/dev/usb/lp[0-9]{1,3}',config.usb_device_path) is None)
            or type(config.print_width_dots) is not int or config.print_width_dots!=576
            or type(config.dither_mode) is not str or config.dither_mode not in DITHER_MODES
            or type(config.dither_threshold) is not int or not 0<=config.dither_threshold<=255
            or not (config.lan_host or config.wifi_host or config.windows_printer_name
                    or config.usb_vendor_id is not None or config.usb_device_path)):
        raise ValueError('Explicit original POS80 printer configuration required')
