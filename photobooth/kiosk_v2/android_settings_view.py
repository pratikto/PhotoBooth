"""Touch-only setup at the same safe header-hold entry used by GUI v2."""
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from .theme import text_label, ArcadeButton
from .android_settings import save_settings


class MobileSettingsPanel:
    def __init__(self, app):
        self.app=app
        self._disposed=False
        self.popup=None

    def open(self):
        app=self.app
        values=dict(app.mobile_settings)
        layout=BoxLayout(orientation='vertical',spacing=dp(8),padding=dp(8))
        scroll=ScrollView(do_scroll_x=False)
        body=BoxLayout(orientation='vertical',spacing=dp(6),size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))
        scroll.add_widget(body);layout.add_widget(scroll)
        fields={}
        captions={'camera_facing':'Kamera: 0 depan / 1 belakang', 'print_enabled':'Cetak otomatis USB OTG',
                  'usb_vendor':'USB VID (heksadesimal)', 'usb_product':'USB PID (heksadesimal)',
                  'print_width':'Lebar cetak (dot)', 'dither':'Dithering',
                  'sandbox_enabled':'QRIS Sandbox', 'api_url':'URL backend HTTPS',
                  'booth_id':'Booth ID', 'booth_token':'Token booth (bukan Server Key)',
                  'audio_enabled':'Musik dan efek suara', 'face_enabled':'Undangan deteksi wajah',
                  'palm_enabled':'Shutter telapak tangan', 'video_enabled':'Video iklan',
                  'drive_enabled':'Upload Drive di background', 'web_app_url':'URL deployment Apps Script',
                  'upload_token':'Token upload Drive'}
        for key,value in values.items():
            body.add_widget(text_label(captions[key],size=14,height=30))
            if type(value) is bool:
                field=CheckBox(active=value,size_hint_y=None,height=dp(44))
            elif key in {'camera_facing','print_width','dither'}:
                choices={'camera_facing':('0','1'),'print_width':('576','384'),
                         'dither':('floyd-steinberg','bayer','threshold')}
                field=Spinner(text=str(value),values=choices[key],size_hint_y=None,height=dp(48))
            else:
                field=TextInput(text=(f'{value:04x}' if key in {'usb_vendor','usb_product'} else str(value)),
                                multiline=False,password=key in {'booth_token','upload_token'},size_hint_y=None,height=dp(48))
            fields[key]=field;body.add_widget(field)
        message=text_label('Simpan lalu tutup dan buka aplikasi untuk menerapkan.\nPesanan dan foto tetap disimpan.',size=13,height=72)
        layout.add_widget(message)
        def save():
            if self._disposed or app._suspended or app._closed:
                return
            try:
                data={}
                for key,value in values.items():
                    field=fields[key]
                    data[key]=(field.active if type(value) is bool else
                               int(field.text,16) if key in {'usb_vendor','usb_product'} else
                               int(field.text) if type(value) is int else field.text)
                save_settings(app.private_root,data)
                message.text='Tersimpan. Tutup lalu buka aplikasi.\nTidak ada foto atau cetak yang diulang.'
            except (ValueError,OSError):
                message.text='Belum disimpan. Periksa isian.\nProfil pembayaran aktif harus diselesaikan dulu.'
        def health():
            self.close()
            app._open_mobile_health()
        for title,callback in (('STATUS PERANGKAT',health),
                               ('IZINKAN USB PRINTER',lambda:setattr(message,'text',app._request_usb_permission())),
                               ('SIMPAN PENGATURAN',save),('TUTUP',self.close)):
            button=ArcadeButton(title,height=48)
            button.bind(on_release=lambda _button, callback=callback:callback())
            layout.add_widget(button)
        self.popup=Popup(title='PENGATURAN ANDROID',content=layout,size_hint=(.96,.96),auto_dismiss=False)
        self.popup.bind(on_dismiss=lambda *_:self._closed())
        self.popup.open()

    def _closed(self):
        self._disposed=True
        self.app._operator_closed(self)

    def close(self):
        if self.popup:
            self.popup.dismiss()
