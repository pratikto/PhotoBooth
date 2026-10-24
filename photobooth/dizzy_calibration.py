"""Opt-in inverse tone response for Meong CPU Dizzy only.

Measured on uniform 96x96 gray fields at seed 42 for each native CPU variant,
0..255; inverse constructed by interpolating monotone response (Q16 storage).
These are digital dot-density tables, NOT actual printer-paper calibration.
Never substitute the author's distinct GPU Layered Dizzy LUT.
Method: https://liamappelbe.medium.com/dizzy-dithering-on-the-gpu-84f2d2c12a82
"""
from __future__ import annotations

import base64
from functools import lru_cache
import struct

CALIBRATION_ID = "meong-cpu-96x96-seed42-v1"
_Q16_LUTS = {
    "article-8": "AACDBpcHfwhPCQgKmgoxC90LfgwiDQUOoA4xD60PPRAeEfER0RKfE20UOBXYFdUW7hctGfcZzBrEG/Ic2B2wHogfeCCMIXUibyOPJHMlpyaoJ4wogylxKkgrRCxOLZAugi9HMFgxRTJsM0w0STV0NsI3IzkFOgk7/Tu9PIk9tD7VP9NAxEHPQr9Dn0SqRaZGskdeSY9KeUtaTHBNJk4jT9FPp1D5UQVTDFTXVKxV0FbpV+BYsll1WqNbiFzEXeFe1l/iYOdh2GLTY+Jk32W1ZpZny2jPaZRqZ2shbCttNG5tb0ZwE3Hcca1ym3MkdYR2m3e0ePB5H3sWfAF9KX5df6KA1oH+gumD4IQPhkuHZIh7iduKZIxSjSOO7I65j5KQy5HUkt6TmJRrlTSWN5dpmFKZJZodmyicJJ0Ynh2fKaAeoTuid6NcpIqlTaYfpxaoL6lTqiir86v6rAauWK8usNyw2bGPsqWzhrRwtaG2TbhZuVW6YLtAvDC9O74svyrAS8F2wkLDAsT2xPrF3MY9yIvJtsqzy5PMus2nzrjPfdBv0bHSu9O31I7VfNZz11fYWNmM2nDbkNyK3XPeh9934E/hJ+IN4zvkM+UI5tLmEegq6Sfqx+qS62DsLu0O7uHuwu9S8M7wX/H68d3ygfMi9M70ZfX39bD2gPdo+Hz5//8=",
    "orthogonal-4": "AAAwCoQLqAyLDXAOWQ8cEPkQuhGDElgTMRQUFboVexZRFwsY+xi8GWMa9hqcG1IcJB3THaMebB8SIC4hCyLTIssjzySnJVgm5SaQJ04o8Si2KWwq+yrCK3Us/Sy5LXguGC+vL1UwSjHYMXwyUjOKNEY1HjbfNk44PDn9OZU6GjtePMg9QT/+P+RA+EECQytEH0U4Rl1HoEgJSvpK/Ev6TRFPGFAcUQ5SXFMPVJFU81RZVa9WGVgqWRZbN1wPXdpdtV6CX+5fWmBpYWpiWGMoZGJlAWb3ZgdoyGh8aZZquWvvbHZuum8bcT1yP3N/dGd1lnasd6h49Hmie+p9rH/kfxuAU4AVgl2EC4Yyh0mIaYmYioCLu4yljeSORZCJkQuTRJRplVCWI5f4l8qYfJmdmtSbmpyUnZaepZ8RoH2gSqElovCiyKPWpdWm5KdKqf2pYar5qvCro6zvrd2u56/usAWy/rP8tPa1VbeguMe527qqu/28B74bvwHAvsA3wo/D5cRqxQLGw8axxx3J1cm4ynXLM8wozSfOtc6qz1DQ59CH0RjSmtJY0z3UBNWT1UnWDtex12/YGtmn2VjaK9sq3Cfd4t3Q3unfkeBc4Szi2+Kt42PkCeWc5UPmBOf0567ohOlF6uvqyOul7HDtNu4G7+Pvm/CG8XTyV/N79M/1//8=",
}


@lru_cache(maxsize=2)
def dizzy_cpu_lut(variant: str) -> tuple[float, ...]:
    """Return 256 monotone normalized calibration values."""
    if variant not in _Q16_LUTS:
        raise ValueError("Unsupported Dizzy CPU calibration variant.")
    raw = base64.b64decode(_Q16_LUTS[variant], validate=True)
    if len(raw) != 512:
        raise ValueError("Corrupt Dizzy CPU calibration table.")
    levels = tuple(v / 65535.0 for v in struct.unpack("<256H", raw))
    if levels[0] != 0.0 or levels[-1] != 1.0 or any(
        left > right for left, right in zip(levels, levels[1:])
    ):
        raise ValueError("Non-monotone Dizzy CPU calibration table.")
    return levels
