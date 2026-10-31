"""Private, native-dot recovery receipt; no preview, spool file or new token."""
import re

from PIL import Image, ImageDraw, ImageFont
import qrcode


INSTRUCTIONS = (
    'Pembayaran sudah diterima.',
    'Simpan tiket sampai sesi selesai.',
    'Jika aplikasi terputus:',
    'Pilih SCAN QR TIKET DI KAMERA.',
    'Tunjukkan QR ini ke kamera booth.',
    'Lanjutkan pesanan yang sama.',
    'Tidak perlu membayar ulang.',
    'Tiket ini rahasia. Jangan dibagikan.',
    'Bukan QR pembayaran atau refund.',
    'Berlaku 24 jam sejak pesanan dibuat.',
)


def render_recovery_receipt(ticket, order, width=576):
    """Reuse original QR encoder/native-dot rule, with the original capability."""
    if width not in (384, 576):
        raise ValueError('Use a 384 or 576 dot receipt printer')
    parts=ticket.split(':') if isinstance(ticket,str) else []
    if (len(parts)!=4 or parts[0]!='MEONG-RECOVERY-V1'
            or re.fullmatch(r'PB[0-9]{3,8}',parts[1]) is None
            or re.fullmatch(r'[a-f0-9]{32}',parts[2]) is None
            or re.fullmatch(r'[A-Za-z0-9_-]{43}',parts[3]) is None
            or order.get('mode')!='sandbox' or order.get('state')!='PAID'
            or order.get('checkout_key')!=parts[2] or order.get('booth_id')!=parts[1]
            or type(order.get('amount')) is not int or order['amount']<=0):
        raise ValueError('Original paid Sandbox receipt required')
    code=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4,box_size=1)
    code.add_data(ticket);code.make(fit=True)
    code.box_size=(width-32)//len(code.get_matrix())
    if code.box_size<3:raise ValueError('Receipt QR is too dense')
    qr=code.make_image(fill_color='black',back_color='white').convert('1')
    size=16 if width==384 else 20
    try:font=ImageFont.truetype('DejaVuSans.ttf',size)
    except OSError:font=ImageFont.load_default(size=size)
    lines=['MEONG PHOTOBOOTH','TIKET PEMULIHAN - SANDBOX',
           'PEMBAYARAN UJI DITERIMA',
           f"{parts[1]} / {parts[2][-8:]}",
           'Rp'+f"{order['amount']:,}".replace(',','.')]
    step=size+10;top=16+len(lines)*step
    image=Image.new('1',(width,top+qr.height+24+len(INSTRUCTIONS)*step+16),1)
    draw=ImageDraw.Draw(image)
    def line(text,y):draw.text((width/2,y),text,anchor='mt',font=font,fill=0)
    for index,text in enumerate(lines):line(text,16+index*step)
    image.paste(qr,((width-qr.width)//2,top))
    for index,text in enumerate(INSTRUCTIONS):line(text,top+qr.height+24+index*step)
    return image
