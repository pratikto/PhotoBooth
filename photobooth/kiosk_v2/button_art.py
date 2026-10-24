"""Reuse original Meong Fly button materials with native text controls."""
from functools import lru_cache

from PIL import Image,ImageDraw
from photobooth import meong_fly_painter as painter
from photobooth.meong_fly_polish import arcade_button

KINDS={'primary':'pink','secondary':'cyan','tertiary':'dark','muted':'dark'}


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
