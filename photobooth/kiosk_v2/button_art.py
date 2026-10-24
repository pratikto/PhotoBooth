"""Reuse the original Meong Fly button painter and glyphs on native controls."""
from functools import lru_cache
import textwrap

from PIL import Image,ImageDraw
from photobooth import meong_fly_painter as painter
from photobooth.meong_fly_polish import arcade_button

KINDS={'primary':'pink','secondary':'cyan','tertiary':'dark','muted':'dark'}
DISPLAY_TRANSLATION=str.maketrans({'−':'-','–':'-','—':'-','•':'-','…':'...','×':'X','±':'+/-'})
ICONS={'MULAI FOTO':'camera','MAIN MEONG FLY':'gamepad','AYO FOTO':'camera','UJI FOTO':'camera'}


@lru_cache(maxsize=4)
def material_pixels(variant):
    """Original complete 290×55 button, including its authored shadow."""
    image=Image.new('RGBA',(291,61))
    arcade_button(ImageDraw.Draw(image),(0,0,290,55),'',KINDS[variant],painter)
    if variant=='muted':
        # The original game has no unavailable state. Recolor only its plain
        # dark face/edge/bevel; preserve the actual authored material geometry.
        colors={(27,41,91):(69,71,100),(149,148,210):(185,191,222),
                (55,72,130):(97,102,139),(3,20,75):(45,50,84),
                (8,24,79):(50,54,88)}
        image.putdata([(*colors.get(pixel[:3],pixel[:3]),pixel[3]) for pixel in image.getdata()])
    return image


@lru_cache(maxsize=4)
def material_texture(variant):
    from photobooth.meong_fly_gui import kivy_texture
    return kivy_texture(material_pixels(variant))


def material_slices(width,height,cap=12):
    """Nine slices preserve original bevels/corners when native controls resize."""
    dx=(0,min(cap,width/2),max(width/2,width-cap),width)
    dy=(0,min(cap,height/2),max(height/2,height-cap),height)
    sx=(0,12,279,291);sy=(0,12,49,61)
    for row in range(3):
        for col in range(3):
            yield (sx[col],sy[row],sx[col+1],sy[row+1]), (dx[col],dy[row],dx[col+1],dy[row+1])


def display_text(text):
    return str(text).upper().translate(DISPLAY_TRANSLATION)


def caption_layout(text,font_size,width,height,icon=None):
    """Fit whole words/lines; never shorten a disabled action or operator label."""
    value=display_text(text)
    target=max(.8,font_size/7)
    for attempt in range(24):
        cell=max(.65,target*.94**attempt)
        icon_units=19 if icon else 0
        columns=max(1,int((max(1,width)/cell-icon_units)/6))
        lines=tuple(line for paragraph in value.splitlines() or ['']
                    for line in textwrap.wrap(paragraph,columns,break_long_words=False,
                                              break_on_hyphens=False) or [''])
        units=(max((len(line)*6-1 for line in lines),default=0)+icon_units+1,
               max(7*len(lines)+2*(len(lines)-1),10.5 if icon else 0)+1)
        if units[0]*cell<=width and units[1]*cell<=height:
            return lines,cell
    return lines,min(cell,max(1,width)/max(1,units[0]),max(1,height)/max(1,units[1]))


@lru_cache(maxsize=256)
def caption_pixels(lines,ink,icon=None):
    """Render the actual original 5×7 glyphs/icons at a reusable 2× base scale."""
    tw=max((len(line)*6-1 for line in lines),default=0)*2
    th=(7*len(lines)+2*(len(lines)-1))*2
    offset=38 if icon else 0
    height=max(th,21 if icon else 0)+2
    image=Image.new('RGBA',(max(1,tw+offset+2),max(1,height)))
    draw=ImageDraw.Draw(image)
    for index,line in enumerate(lines):
        painter.pixel_text(draw,line,offset+1+tw/2,(height-th)//2+index*18,
                           scale=2,fill=ink)
    if icon:
        draw_icon=painter._camera_icon if icon=='camera' else painter._gamepad_icon
        draw_icon(draw,1,(height-21)//2)
    return image


@lru_cache(maxsize=256)
def caption_texture(lines,ink,icon=None):
    from photobooth.meong_fly_gui import kivy_texture
    return kivy_texture(caption_pixels(lines,ink,icon))
