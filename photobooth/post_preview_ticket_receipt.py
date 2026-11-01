"""In-memory original post-preview Recovery Ticket receipt (not legacy PAID-first).

No plaintext/QR bitmap is saved to disk, logged or transferred to the backend.
Physical paper receipt is distinct from successful transport submission.
"""
import textwrap

from PIL import Image, ImageDraw, ImageFont
import qrcode


def render_post_preview_receipt(ticket, *, booth_id, amount, width=576):
    """Render exact protected Recovery Ticket payload using the original raster path.

    Call only after a trusted PAID entitlement and private original ticket offer.
    """
    if (not isinstance(ticket, str) or not isinstance(booth_id, str)
            or not ticket.startswith("MEONG:RECOVERY:1:"+booth_id+":")
            or type(amount) is not int or amount <= 0
            or type(width) is not int or width not in (384,576)):
        raise ValueError("Original paid receipt profile required")
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                      border=4, box_size=1)
    qr.add_data(ticket)
    qr.make(fit=True)
    modules=len(qr.get_matrix())
    box=(width-32)//modules
    if box < 3:
        raise ValueError("Original ticket QR exceeds receipt density")
    qr.box_size=box
    image=qr.make_image(fill_color="black",back_color="white").convert("1")
    try:
        font=ImageFont.truetype("DejaVuSans.ttf", 17 if width==576 else 13)
    except OSError:
        font=ImageFont.load_default()
    rows=[
        "MEONG PHOTOBOOTH",
        "TIKET PEMULIHAN - UJI",
        booth_id+" / Rp"+f"{amount:,}".replace(",","."),
        "SIMPAN TIKET INI!",
        "Untuk memulihkan sesi yang terputus.",
        "Tanpa tiket, sesi privat tidak dapat dibuka.",
        "BUKAN QR PEMBAYARAN / DOWNLOAD",
    ]
    rows.extend(textwrap.wrap(ticket, width=39 if width==576 else 29,
                             break_long_words=True, break_on_hyphens=False))
    step=25 if width==576 else 20
    top=10+4*step
    canvas=Image.new("1",(width,top+image.height+(len(rows)-4)*step+22),1)
    pen=ImageDraw.Draw(canvas)
    def line(value,y):
        pen.text((width/2,y),value,anchor="mt",font=font,fill=0)
    for i,value in enumerate(rows[:4]):line(value,10+i*step)
    canvas.paste(image,((width-image.width)//2,top))
    for i,value in enumerate(rows[4:]):line(value,top+image.height+10+i*step)
    return canvas
