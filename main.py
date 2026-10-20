"""Launch the existing DEMO kiosk or the explicitly selected QRIS test mode."""
import os


def main():
    mode = os.environ.get('MEONG_PAYMENT_MODE', 'demo')
    if mode == 'demo':
        from photobooth.app import PhotoBoothApp
        app = PhotoBoothApp()
    elif mode in {'qris-mock', 'qris-sandbox'}:
        from photobooth.app_qris import QrisPhotoBoothApp
        app = QrisPhotoBoothApp()
    else:
        raise RuntimeError('Unknown payment mode; refusing to fall back to DEMO')
    app.run()


if __name__ == '__main__':
    main()
