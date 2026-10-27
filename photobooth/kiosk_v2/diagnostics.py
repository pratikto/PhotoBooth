"""Local launch diagnostics for Python exceptions and native fatal tracebacks.

No Kivy import, network, customer data or global production-booth configuration.
The dedicated v2 launcher keeps this file open through application teardown.
"""

from datetime import datetime
import faulthandler
import logging
import os
from pathlib import Path
import platform
import subprocess
import threading


LOG = logging.getLogger('photobooth.kiosk_v2.diagnostics')


def source_head(root):
    """Read only the local checkout, and tolerate Git not being installed."""
    try:
        result = subprocess.run(
            ['git', '-C', str(root), 'rev-parse', '--short=12', 'HEAD'],
            capture_output=True, text=True, timeout=2, check=True,
        )
        return result.stdout.strip() or 'unknown'
    except (OSError, subprocess.SubprocessError):
        return 'unknown'


class DiagnosticSession:
    def __init__(self, root):
        root = Path(root)
        folder = root / 'data' / 'diagnostics'
        folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        self.path = folder / f'portrait-v2-{stamp}-{os.getpid()}.log'
        self.stream = self.path.open('a', encoding='utf-8', buffering=1)
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
        from photobooth.delivery_timing import LOG as delivery_log
        self._delivery_log = delivery_log
        self._delivery_log.addHandler(self.handler)
        self._native_logger = None
        self._namespace = logging.getLogger('photobooth.kiosk_v2')
        self._previous_level = self._namespace.level
        self._previous_thread_hook = threading.excepthook
        self._fatal_was_enabled = faulthandler.is_enabled()
        self._owns_fatal_handler = False
        self._closed = False
        self._namespace.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.handler)
        # Respect an explicit existing handler, e.g. python -X faulthandler.
        if not self._fatal_was_enabled:
            try:
                faulthandler.enable(file=self.stream, all_threads=True)
                self._owns_fatal_handler = True
            except (OSError, RuntimeError):
                LOG.warning('Native fatal handler unavailable', exc_info=True)
        self._thread_hook = self._thread_failed
        threading.excepthook = self._thread_hook
        self.head = source_head(root)
        LOG.info('Session start HEAD=%s Python=%s OS=%s', self.head, platform.python_version(), platform.system())
        LOG.info('Native fatal tracebacks=%s destination=%s', faulthandler.is_enabled(),
                 'this file' if self._owns_fatal_handler else 'existing handler')

    def _thread_failed(self, args):
        LOG.error('Unhandled worker exception thread=%s', args.thread.name if args.thread else 'unknown',
                  exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
        self._previous_thread_hook(args)

    def __enter__(self):
        return self

    def attach_kivy_logger(self):
        """MIXED mode keeps native logs off root; retain them in this session too."""
        logger = logging.getLogger('kivy')
        if not logger.propagate and self.handler not in logger.handlers:
            logger.addHandler(self.handler)
            self._native_logger = logger

    def __exit__(self, kind, value, trace):
        if kind is not None:
            LOG.error('Application exited with an exception', exc_info=(kind, value, trace))
        self.close()
        return False

    def close(self):
        if self._closed:
            return
        self._closed = True
        LOG.info('Session end')
        if threading.excepthook is self._thread_hook:
            threading.excepthook = self._previous_thread_hook
        if self._owns_fatal_handler:
            faulthandler.disable()
        logging.getLogger().removeHandler(self.handler)
        self._delivery_log.removeHandler(self.handler)
        if self._native_logger is not None:
            self._native_logger.removeHandler(self.handler)
        self.handler.close()
        self.stream.close()
        self._namespace.setLevel(self._previous_level)
