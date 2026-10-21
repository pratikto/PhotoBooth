"""FEAT-021 pixel-art rendering for the isolated Meong Fly Kivy demo.

The five-panel owner mockup defines color/layout, not a screenshot to paste over
nonfunctional hotspots. Pillow generates actual art/controls at 360 x 720.
The logo is a DISPLAY-ONLY crop of the already approved repo asset.
"""
from collections import deque
from functools import lru_cache
from math import cos, pi, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw

W, H = 360, 720
NAVY = (5, 12, 47)
PANEL = (11, 21, 67)
OUTLINE = (87, 73, 154)
INK = (7, 13, 38)
WHITE = (248, 248, 255)
CYAN = (88, 209, 255)
PINK = (255, 85, 171)
GOLD = (255, 220, 120)
PURPLE = (179, 133, 255)

# Hit regions share precisely the painting coordinate system (top origin).
ACTIONS = {
    "start": {"game": (35, 542, 290, 55), "photo": (35, 612, 290, 55)},
    "scan": {"validate": (45, 540, 270, 53), "back": (64, 627, 232, 48)},
    "game": {"pause": (15, 18, 48, 46)},
    "won": {"continue": (34, 563, 292, 62)},
    "lost": {"continue": (34, 565, 292, 62)},
    "tutorial": {"tutorial_done": (35, 644, 290, 55)},
    "layouts": {},  # Populated from layout_hitboxes after declaration.
}
from .meong_fly_photo_handoff import layout_hitboxes
ACTIONS["layouts"] = layout_hitboxes()
DEMO_ENTRY = (45, 478, 270, 46)

# Built-in 5x7 bitmap characters avoid a dependence on installed Windows fonts.
GLYPHS = {
 "A":("01110","10001","10001","11111","10001","10001","10001"),
 "B":("11110","10001","10001","11110","10001","10001","11110"),
 "C":("01111","10000","10000","10000","10000","10000","01111"),
 "D":("11110","10001","10001","10001","10001","10001","11110"),
 "E":("11111","10000","10000","11110","10000","10000","11111"),
 "F":("11111","10000","10000","11110","10000","10000","10000"),
 "G":("01111","10000","10000","10111","10001","10001","01111"),
 "H":("10001","10001","10001","11111","10001","10001","10001"),
 "I":("11111","00100","00100","00100","00100","00100","11111"),
 "J":("00111","00010","00010","00010","10010","10010","01100"),
 "K":("10001","10010","10100","11000","10100","10010","10001"),
 "L":("10000","10000","10000","10000","10000","10000","11111"),
 "M":("10001","11011","10101","10101","10001","10001","10001"),
 "N":("10001","11001","10101","10011","10001","10001","10001"),
 "O":("01110","10001","10001","10001","10001","10001","01110"),
 "P":("11110","10001","10001","11110","10000","10000","10000"),
 "Q":("01110","10001","10001","10001","10101","10010","01101"),
 "R":("11110","10001","10001","11110","10100","10010","10001"),
 "S":("01111","10000","10000","01110","00001","00001","11110"),
 "T":("11111","00100","00100","00100","00100","00100","00100"),
 "U":("10001","10001","10001","10001","10001","10001","01110"),
 "V":("10001","10001","10001","10001","10001","01010","00100"),
 "W":("10001","10001","10001","10101","10101","10101","01010"),
 "X":("10001","10001","01010","00100","01010","10001","10001"),
 "Y":("10001","10001","01010","00100","00100","00100","00100"),
 "Z":("11111","00001","00010","00100","01000","10000","11111"),
 "0":("01110","10011","10101","10101","10101","11001","01110"),
 "1":("00100","01100","00100","00100","00100","00100","01110"),
 "2":("01110","10001","00001","00010","00100","01000","11111"),
 "3":("11110","00001","00001","01110","00001","00001","11110"),
 "4":("00010","00110","01010","10010","11111","00010","00010"),
 "5":("11111","10000","11110","00001","00001","10001","01110"),
 "6":("01110","10000","10000","11110","10001","10001","01110"),
 "7":("11111","00001","00010","00100","01000","01000","01000"),
 "8":("01110","10001","10001","01110","10001","10001","01110"),
 "9":("01110","10001","10001","01111","00001","00001","01110"),
 " ":("00000",)*7,
 "&":("01100","10010","10100","01000","10101","10010","01101"),
 "!":("00100","00100","00100","00100","00100","00000","00100"),
 "-":("00000","00000","00000","11111","00000","00000","00000"),
 ".":("00000","00000","00000","00000","00000","01100","01100"),
 ":":("00000","01100","01100","00000","01100","01100","00000"),
 "/":("00001","00001","00010","00100","01000","10000","10000"),
 "?":("01110","10001","00001","00110","00100","00000","00100"),
 "(":("00010","00100","01000","01000","01000","00100","00010"),
 ")":("01000","00100","00010","00010","00010","00100","01000"),
 "+":("00000","00100","00100","11111","00100","00100","00000"),
}


def pixel_text(draw, value, center_x, top, scale=2, fill=WHITE,
               shadow=None, spacing=1):
    """Centered non-antialiased retro glyphs."""
    value = str(value).upper()
    step = (5 + spacing) * scale
    x0 = round(center_x - (len(value) * step - spacing * scale) / 2)
    for k, letter in enumerate(value):
        bitmap = GLYPHS.get(letter, GLYPHS["?"])
        for iy, line in enumerate(bitmap):
            for ix, bit in enumerate(line):
                if bit == "1":
                    x = x0 + k * step + ix * scale
                    y = top + iy * scale
                    if shadow:
                        draw.rectangle((x+scale,y+scale,x+2*scale-1,y+2*scale-1),
                                       fill=shadow)
                    draw.rectangle((x,y,x+scale-1,y+scale-1),fill=fill)


def panel(draw, bbox, fill=PANEL, border=OUTLINE, thickness=3):
    x0,y0,x1,y1=bbox
    draw.rectangle((x0+5,y0,x1-5,y1),fill=border)
    draw.rectangle((x0,y0+5,x1,y1-5),fill=border)
    draw.rectangle((x0+thickness+5,y0+thickness,x1-thickness-5,y1-thickness),
                   fill=fill)
    draw.rectangle((x0+thickness,y0+thickness+5,x1-thickness,y1-thickness-5),
                   fill=fill)


def button(draw, xywh, label, kind="pink", text_scale=2):
    x,y,w,h=xywh
    bg=PINK if kind=="pink" else CYAN if kind=="cyan" else (27,38,86)
    edge=(255,155,212) if kind=="pink" else (178,245,255) if kind=="cyan" else (159,160,205)
    dark=(100,17,87) if kind=="pink" else (16,87,132) if kind=="cyan" else (15,19,49)
    panel(draw,(x,y+4,x+w,y+h+4),dark,dark,1)
    panel(draw,(x,y,x+w,y+h-2),bg,edge,3)
    pixel_text(draw,label,x+w/2,y+(h-7*text_scale)/2-2,
               scale=text_scale,fill=INK if kind!="dark" else WHITE)


def stars(draw, seed=21):
    rng=Random(seed)
    for iy in range(H):
        draw.line((0,iy,W,iy),fill=(4,9+round(5*iy/H),39+round(23*iy/H)))
    for i in range(145):
        x,y=rng.randrange(W),rng.randrange(H)
        c=rng.choice([(96,89,196),(175,134,255),(255,181,128),
                      (121,210,255),(253,230,146)])
        if i%7==0:
            draw.line((x-3,y,x+3,y),fill=c,width=1)
            draw.line((x,y-4,x,y+4),fill=c,width=1)
            draw.point((x-1,y-1),fill=WHITE)
        elif i%13==0:
            draw.rectangle((x-2,y-2,x+2,y+2),fill=(29,59,137))
            draw.rectangle((x-1,y-1,x+1,y+1),fill=c)
        else:
            draw.rectangle((x,y,x+int(i%3==0),y+int(i%3==0)),fill=c)


def planet(draw,x,y,r,tint=(176,77,192)):
    outline=(47,27,101)
    draw.ellipse((x-r-3,y-r-3,x+r+3,y+r+3),fill=outline)
    draw.ellipse((x-r,y-r,x+r,y+r),fill=tint)
    draw.ellipse((x-r*.63,y-r*.76,x+r*.14,y-r*.1),fill=(230,125,225))
    draw.arc((x-r*1.5,y-r*.55,x+r*1.5,y+r*.58),15,170,
             fill=(253,126,194),width=5)
    draw.arc((x-r*1.5,y-r*.55,x+r*1.5,y+r*.58),180,360,
             fill=(254,102,181),width=5)
    draw.line((x-r*.75,y+r*.3,x+r*.6,y+r*.3),fill=(114,57,163),width=3)


def galaxy(draw,x,y,r):
    for j,c in enumerate(((23,24,88),(45,32,119),(73,42,162),(121,69,192))):
        rr=r-j*10
        draw.arc((x-rr,y-rr*.62,x+rr,y+rr*.62),45+j*20,310+j*15,fill=c,width=4)
    draw.ellipse((x-8,y-7,x+8,y+7),fill=(188,105,244))
    draw.ellipse((x-2,y-2,x+2,y+2),fill=(244,204,255))


def earth(draw,cx,cy,r):
    draw.ellipse((cx-r-5,cy-r-5,cx+r+5,cy+r+5),fill=(13,102,208))
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(44,157,231))
    land=(92,190,138)
    draw.polygon([(cx-r*.9,cy-r*.12),(cx-r*.55,cy-r*.36),
                  (cx-r*.28,cy-r*.13),(cx-r*.25,cy+r*.3),
                  (cx-r*.62,cy+r*.43)],fill=land)
    draw.polygon([(cx+r*.13,cy-r*.75),(cx+r*.55,cy-r*.68),
                  (cx+r*.83,cy-r*.21),(cx+r*.31,cy-r*.05),
                  (cx+r*.19,cy+r*.42)],fill=land)
    draw.arc((cx-r*.91,cy-r*.88,cx+r*.91,cy+r*.88),188,350,
             fill=(176,239,255),width=4)


def asteroid(draw,x,y,r,base=(113,104,160),seed=9):
    rng=Random(seed)
    points=[]
    for j in range(12):
        theta=j*2*pi/12
        rr=r*(.83+rng.random()*.25)
        points.append((int(x+rr*cos(theta)),int(y+rr*sin(theta))))
    draw.polygon([(a+3,b+3) for a,b in points],fill=(5,8,35))
    draw.polygon(points,fill=(25,31,72))
    inner=[(int(x+(a-x)*.88),int(y+(b-y)*.88)) for a,b in points]
    draw.polygon(inner,fill=base)
    draw.polygon([(x-r*.65,y-r*.42),(x-r*.3,y-r*.68),
                  (x+r*.16,y-r*.56),(x-r*.18,y-r*.25)],fill=(181,161,199))
    for dx,dy,sz in ((-.37,-.10,.25),(.35,.18,.18),(.04,-.52,.12)):
        k=r*sz
        q=(x+r*dx-k,y+r*dy-k,x+r*dx+k,y+r*dy+k)
        draw.ellipse(q,fill=(48,48,92),outline=(37,33,76),width=2)
        draw.arc(q,175,280,fill=(205,173,206),width=1)


def rainbow(draw,x0,y0,length=105,width=7):
    shades=((255,95,164),(255,172,103),(255,229,131),
            (106,224,177),(92,206,255))
    for n,color in enumerate(shades):
        points=[]
        for u in range(0,length+2,4):
            yy=y0+n*width+round(4*sin(u*.13))
            points.append((int(x0-u),int(yy)))
        draw.line(points,fill=color,width=width)


def _mask_white_border(im):
    """Only mask near-white pixels connected to an opaque image's edge."""
    rgba=im.convert("RGBA")
    if rgba.getextrema()[3][0] < 255:
        return rgba
    w,h=rgba.size
    pix=rgba.load()
    visited=bytearray(w*h)
    queue=deque()
    for x in range(w):queue.extend(((x,0),(x,h-1)))
    for y in range(h):queue.extend(((0,y),(w-1,y)))
    while queue:
        x,y=queue.pop()
        if not (0<=x<w and 0<=y<h):continue
        off=y*w+x
        if visited[off]:continue
        visited[off]=1
        rr,gg,bb,aa=pix[x,y]
        if min(rr,gg,bb)<245:continue
        pix[x,y]=(rr,gg,bb,0)
        queue.extend(((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
    return rgba


@lru_cache(maxsize=4)
def logo_parts(path):
    """Derive on-screen crops, preserving the approved source file on disk."""
    with Image.open(path) as f:
        source=_mask_white_border(f.copy())
    logo=source.crop(source.getbbox() or (0,0,*source.size))
    w,h=source.size
    body=source.crop((int(w*.35),int(h*.19),int(w*.99),int(h*.64)))
    box=body.getbbox()
    if box:body=body.crop(box)
    return logo,body


def place_art(canvas,art,x,y,w,h,opacity=255):
    art=art.copy()
    if opacity<255:
        art.putalpha(art.getchannel("A").point(lambda v:int(v*opacity/255)))
    thumb=art.copy()
    thumb.thumbnail((w,h),Image.Resampling.NEAREST)
    canvas.alpha_composite(thumb,(int(x+(w-thumb.width)/2),
                                  int(y+(h-thumb.height)/2)))


def draw_common(draw,screen):
    stars(draw,seed=12 if screen in ("start","scan") else 27)
    if screen=="start":
        planet(draw,23,38,23,(165,83,223))
        asteroid(draw,337,385,27,seed=4)
        asteroid(draw,345,71,15,seed=2)
    elif screen=="scan":
        planet(draw,324,44,42,(145,90,205))
        earth(draw,273,785,166)
        asteroid(draw,32,655,18,seed=13)
    elif screen=="game":
        planet(draw,314,594,54,(193,59,182))
        asteroid(draw,318,116,21,seed=5)
        earth(draw,44,824,130)
        galaxy(draw,278,513,58)
    elif screen=="won":
        planet(draw,53,45,21,(178,77,202))
        asteroid(draw,310,72,27,seed=3)
        for k in range(24):
            a=k*2*pi/24
            draw.line((180,312,180+140*cos(a),314+144*sin(a)),
                      fill=(31,36,94),width=3)
    elif screen=="lost":
        asteroid(draw,38,120,28,seed=1)
        asteroid(draw,312,87,33,seed=5)
        asteroid(draw,345,400,28,seed=7)


def _fake_qr(draw,x,y,pixel=6):
    """Clearly marked decoration; never pretend it validates a real QR."""
    rng=Random(18)
    for iy in range(21):
        for ix in range(21):
            if rng.random()>.50:
                px=x+ix*pixel;py=y+iy*pixel
                draw.rectangle((px,py,px+pixel-1,py+pixel-1),fill=(13,24,64))
    for x0,y0 in ((0,0),(14,0),(0,14)):
        draw.rectangle((x+x0*pixel,y+y0*pixel,
                        x+(x0+6)*pixel,y+(y0+6)*pixel),fill=(13,24,64))
        draw.rectangle((x+(x0+1)*pixel,y+(y0+1)*pixel,
                        x+(x0+5)*pixel,y+(y0+5)*pixel),fill=(244,242,255))
        draw.rectangle((x+(x0+2)*pixel,y+(y0+2)*pixel,
                        x+(x0+4)*pixel,y+(y0+4)*pixel),fill=(13,24,64))
    draw.ellipse((x+10*pixel,y+9*pixel,x+12*pixel,y+11*pixel),fill=PINK)



def _gamepad_icon(draw, x, y):
    """Tiny outlined retro controller for the pink Start CTA."""
    draw.rectangle((x, y+3, x+29, y+20), fill=INK)
    draw.rectangle((x+3, y, x+26, y+19), fill=WHITE)
    draw.rectangle((x+6, y+3, x+23, y+16), fill=(208,197,225))
    draw.rectangle((x+8, y+6, x+11, y+14), fill=INK)
    draw.rectangle((x+5, y+9, x+14, y+11), fill=INK)
    draw.rectangle((x+18, y+7, x+20, y+9), fill=PINK)
    draw.rectangle((x+22, y+11, x+24, y+13), fill=CYAN)


def _camera_icon(draw, x, y):
    """Small chunky camera icon for 'Langsung Foto'."""
    draw.rectangle((x, y+4, x+26, y+20), fill=INK)
    draw.rectangle((x+3, y+7, x+23, y+17), fill=WHITE)
    draw.rectangle((x+7, y+2, x+17, y+8), fill=INK)
    draw.ellipse((x+8, y+7, x+19, y+18), fill=(16,52,122))
    draw.ellipse((x+11, y+10, x+16, y+15), fill=CYAN)
    draw.rectangle((x+20, y+6, x+23, y+9), fill=PINK)


def _ticket_icon(draw, x, y):
    """Iconic prize ticket as seen beside the mockup win voucher."""
    draw.rectangle((x, y+3, x+27, y+23), fill=INK)
    draw.rectangle((x+3, y+5, x+24, y+20), fill=(253,158,81))
    draw.rectangle((x+7, y+7, x+20, y+18), fill=GOLD)
    draw.rectangle((x+11, y+11, x+15, y+15), fill=PINK)


def paint_static_screen(screen,logo_path):
    """Paint all five real UI backgrounds with the mockup's visual hierarchy."""
    if screen not in ACTIONS:
        raise ValueError("Invalid Meong Fly screen: "+str(screen))
    canvas=Image.new("RGBA",(W,H),(0,0,0,255))
    d=ImageDraw.Draw(canvas)
    draw_common(d,screen)
    if screen in ("tutorial", "layouts"):
        from .meong_fly_photo_handoff import photo_handoff_screen
        return photo_handoff_screen(screen, logo_path)
    if screen in ("start", "scan"):
        # Batch A: cacheable, mockup-matched surfaces with exact existing hitboxes.
        from .meong_fly_polish import paint_polished_menu
        return paint_polished_menu(screen, logo_path)
    if screen == "game":
        # Batch B: independently cached HUD/space art; live sprites stay in Kivy.
        from .meong_fly_game_art import paint_game_background
        return paint_game_background()
    logo,body=logo_parts(str(Path(logo_path)))
    if screen=="start":
        place_art(canvas,logo,26,58,308,207)
        d=ImageDraw.Draw(canvas)
        panel(d,(24,273,336,399))
        pixel_text(d,"MEONG FLY!",180,293,scale=4,fill=PURPLE,shadow=(80,30,102))
        pixel_text(d,"TERBANG DI LUAR ANGKASA",180,347,scale=2)
        pixel_text(d,"DAN HINDARI ASTEROID!",180,369,scale=2)
        panel(d,(48,414,312,513),fill=GOLD,border=(226,141,53),thickness=3)
        pixel_text(d,"MENANG & DAPAT DISKON",180,424,scale=2,fill=INK)
        pixel_text(d,"Rp 2.500",180,447,scale=4,fill=(239,54,132))
        pixel_text(d,"UNTUK PHOTOBOOTH!",180,491,scale=2,fill=INK)
        button(d,ACTIONS["start"]["game"],"MAIN GAME",text_scale=3)
        button(d,ACTIONS["start"]["photo"],"LANGSUNG FOTO",kind="cyan",text_scale=2)
        _gamepad_icon(d,60,558)
        _camera_icon(d,60,624)
        pixel_text(d,"SIMULASI - BELUM ADA DISKON",180,685,scale=1,fill=(180,179,213))
    elif screen=="scan":
        panel(d,(25,137,335,461))
        pixel_text(d,"SCAN STRUK KAFE",180,160,scale=3)
        pixel_text(d,"QR ASLI BELUM TERHUBUNG",180,199,scale=2,fill=GOLD)
        pixel_text(d,"MASUKKAN KODE DEMO DI BAWAH",180,222,scale=1)
        panel(d,(85,255,275,434),fill=(229,234,249),border=PINK)
        _fake_qr(d,117,282,6)
        pixel_text(d,"ILUSTRASI QR",180,440,scale=1,fill=GOLD)
        pixel_text(d,"KODE STRUK DEMO",180,455,scale=2)
        panel(d,(DEMO_ENTRY[0],DEMO_ENTRY[1],
                 DEMO_ENTRY[0]+DEMO_ENTRY[2],DEMO_ENTRY[1]+DEMO_ENTRY[3]),
              fill=(244,242,255))
        button(d,ACTIONS["scan"]["validate"],"VALIDASI DEMO 1X")
        button(d,ACTIONS["scan"]["back"],"KEMBALI",kind="dark")
        pixel_text(d,"DEMO-123 / BUKAN SCAN SUNGGUHAN",180,693,
                   scale=1,fill=(200,195,235))
    elif screen=="game":
        panel(d,(13,17,69,67),fill=(12,22,63),border=WHITE,thickness=2)
        pixel_text(d,"II",41,29,scale=3)
        pixel_text(d,"SCORE",181,20,scale=2)
        pixel_text(d,"TARGET",292,20,scale=2,fill=CYAN)
        pixel_text(d,"10",292,48,scale=3,fill=CYAN)
        pixel_text(d,"TAP UNTUK TERBANG!",180,669,scale=2,fill=GOLD)
        pixel_text(d,"DEMO - 1 STRUK 1 KESEMPATAN",180,695,
                   scale=1,fill=(190,181,215))
    elif screen=="won":
        pixel_text(d,"MISSION",180,104,scale=4,fill=GOLD,shadow=(187,60,90))
        pixel_text(d,"COMPLETE!",180,143,scale=4,fill=GOLD,shadow=(187,60,90))
        rainbow(d,144,311,length=130,width=6)
        place_art(canvas,body,87,232,207,154)
        d=ImageDraw.Draw(canvas)
        panel(d,(38,417,322,529),fill=GOLD,border=(226,141,53))
        pixel_text(d,"KAMU DAPAT DISKON",180,431,scale=2,fill=INK)
        pixel_text(d,"Rp 2.500",180,457,scale=4,fill=(239,54,132))
        _ticket_icon(d,50,468)
        pixel_text(d,"UNTUK PHOTOBOOTH!",180,502,scale=2,fill=INK)
        button(d,ACTIONS["won"]["continue"],"PILIH LAYOUT FOTO")
        pixel_text(d,"DEMO: BELUM TERHUBUNG",180,658,scale=2,fill=GOLD)
    elif screen=="lost":
        pixel_text(d,"GAME",180,113,scale=5,fill=(255,91,127),
                   shadow=(79,19,64))
        pixel_text(d,"OVER",180,159,scale=5,fill=(255,91,127),
                   shadow=(79,19,64))
        place_art(canvas,body,110,232,160,121,opacity=175)
        d=ImageDraw.Draw(canvas)
        panel(d,(65,380,295,461))
        pixel_text(d,"SCORE",180,390,scale=2)
        pixel_text(d,"TIDAK APA-APA!",180,481,scale=2)
        pixel_text(d,"KAMU MASIH BISA FOTO",180,504,scale=2)
        pixel_text(d,"DENGAN HARGA NORMAL",180,527,scale=2)
        button(d,ACTIONS["lost"]["continue"],"PILIH LAYOUT FOTO")
        pixel_text(d,"DEMO: BELUM TERHUBUNG",180,658,scale=2,fill=GOLD)
    return canvas.convert("RGBA")


def make_asteroid_tile(variant=0):
    """Draw transparent rocky pixel art for animated, hitbox-bound obstacles."""
    image=Image.new("RGBA",(72,72),(0,0,0,0))
    colors=((119,109,168),(148,107,131),(104,85,150))
    asteroid(ImageDraw.Draw(image),36,36,31,colors[variant%3],seed=27+variant)
    return image
