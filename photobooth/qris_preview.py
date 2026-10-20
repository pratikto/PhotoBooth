"""Standalone QRIS sandbox checkout preview. Run: python -m photobooth.qris_preview

Opt-in only: does not replace the existing DEMO payment screen.
Set MEONG_QRIS_API_URL, MEONG_QRIS_BOOTH_ID and MEONG_QRIS_BOOTH_TOKEN.
"""
import io
import os
import threading
from urllib.parse import urlsplit

import requests
from PIL import Image as PILImage
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from photobooth.qris_kiosk_client import QrisKioskClient


def download_sandbox_qr(url, *, timeout=8):
    """Accept only a QR image hosted by the official sandbox API."""
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname != "api.sandbox.midtrans.com"
            or parsed.username or parsed.password or parsed.fragment):
        raise ValueError("Untrusted QR image URL")
    response = requests.get(url, timeout=timeout, allow_redirects=False)
    response.raise_for_status()
    if len(response.content) > 512 * 1024:
        raise ValueError("QR image too large")
    with PILImage.open(io.BytesIO(response.content)) as picture:
        if picture.width > 2048 or picture.height > 2048:
            raise ValueError("QR image dimensions too large")
        image = picture.convert("RGBA")
        output = io.BytesIO()
        image.save(output, format="png")
    output.seek(0)
    return output.read()


class QrisPreview(App):
    def build(self):
        self.order_id = None
        self.pending = False
        self.client = None
        root = BoxLayout(orientation="vertical", padding=16, spacing=8)
        root.add_widget(Label(text="MEONG PHOTOBOOTH - QRIS SANDBOX PREVIEW",
                              size_hint_y=None, height=42))
        root.add_widget(Label(text="Uji coba saja. Tidak memulai kamera / mencetak foto.",
                              size_hint_y=None, height=30))
        self.quantity = TextInput(text="1", multiline=False, input_filter="int",
                                  hint_text="Jumlah cetak template_a",
                                  size_hint_y=None, height=48)
        root.add_widget(self.quantity)
        self.create_button = Button(text="BUAT QRIS SANDBOX", size_hint_y=None, height=54)
        self.create_button.bind(on_release=lambda *_: self.create())
        root.add_widget(self.create_button)
        self.qr = Image(allow_stretch=True)
        root.add_widget(self.qr)
        self.message = Label(text="Siap untuk membuat order.", size_hint_y=None, height=56)
        root.add_widget(self.message)
        self.check_button = Button(text="CEK STATUS PEMBAYARAN", size_hint_y=None, height=54)
        self.check_button.bind(on_release=lambda *_: self.check())
        root.add_widget(self.check_button)
        self.claim_button = Button(text="KLAIM SESI (SANDBOX)", size_hint_y=None, height=54)
        self.claim_button.bind(on_release=lambda *_: self.claim())
        root.add_widget(self.claim_button)
        return root

    def _client(self):
        if self.client is None:
            self.client = QrisKioskClient(
                os.environ["MEONG_QRIS_API_URL"],
                os.environ["MEONG_QRIS_BOOTH_ID"],
                os.environ["MEONG_QRIS_BOOTH_TOKEN"],
                allow_local_http=os.environ.get("MEONG_QRIS_LOCAL_PREVIEW") == "1",
            )
        return self.client

    def _work(self, job, success):
        if self.pending:
            return
        self.pending = True
        self.create_button.disabled = True
        self.check_button.disabled = True
        self.claim_button.disabled = True

        def run():
            try:
                result, error = job(), None
            except Exception as exc:
                result, error = None, str(exc)

            def finish(_dt):
                self.pending = False
                self.create_button.disabled = False
                self.check_button.disabled = False
                self.claim_button.disabled = False
                if error:
                    self.message.text = "Gagal: " + error[:140]
                else:
                    success(result)
            Clock.schedule_once(finish, 0)

        threading.Thread(target=run, daemon=True).start()

    def create(self):
        try:
            count = int(self.quantity.text)
            if not 1 <= count <= 10:
                raise ValueError
        except ValueError:
            self.message.text = "Jumlah cetak harus 1-10."
            return

        def job():
            order = self._client().create_order({"template_a": count})
            qr = download_sandbox_qr(order["qr_url"])
            return order, qr

        def success(result):
            order, png = result
            self.order_id = order["order_id"]
            self.qr.texture = CoreImage(io.BytesIO(png), ext="png").texture
            self.message.text = "Menunggu pembayaran: " + self.order_id[:20]
        self._work(job, success)

    def check(self):
        if not self.order_id:
            self.message.text = "Buat order terlebih dahulu."
            return
        self._work(lambda: self._client().status(self.order_id),
                   lambda data: setattr(self.message, "text",
                                        "Status terverifikasi backend: " + data["state"]))

    def claim(self):
        if not self.order_id:
            self.message.text = "Buat order terlebih dahulu."
            return

        def job():
            status = self._client().status(self.order_id)
            if status["state"] != "PAID":
                return False
            return self._client().claim(self.order_id)

        self._work(job, lambda ok: setattr(
            self.message, "text", "Sesi berhasil diklaim sekali." if ok
            else "Belum PAID atau sudah diklaim. Tidak ada sesi diberikan."))


if __name__ == "__main__":
    QrisPreview().run()
