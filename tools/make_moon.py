# -*- coding: utf-8 -*-
"""
画「月光新月」弹幕贴图（32x32）：月牙开口朝右，方便按飞行方向旋转。

用法： python make_moon.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S = 32

BODY = (206, 188, 228)      # 月牙主体（淡紫）
BODY_D = (168, 146, 196)    # 暗部
LIGHT = (248, 244, 255)     # 亮边
GLOW = (222, 208, 246)


def crescent_mask():
    """开口朝右的细月牙。"""
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((2, 2, 30, 30), fill=255)      # 外圆 r=14
    d.ellipse((9, 1, 35, 29), fill=0)        # 挖掉右侧，留约 7px 厚
    return m


def erode(mask, px=1):
    a = np.array(mask)
    out = a.copy()
    for dy in range(-px, px + 1):
        for dx in range(-px, px + 1):
            shifted = np.roll(np.roll(a, dy, axis=0), dx, axis=1)
            out = np.minimum(out, shifted)
    return Image.fromarray(out)

def main():
    mask = crescent_mask()

    # 1) 外发光
    glow_alpha = mask.filter(ImageFilter.GaussianBlur(2.0)).point(lambda v: int(v * 0.5))
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    glow = Image.new("RGBA", (S, S), GLOW + (0,))
    glow.putalpha(glow_alpha)
    canvas = Image.alpha_composite(canvas, glow)

    # 2) 月牙主体
    body = Image.new("RGBA", (S, S), BODY + (0,))
    body.putalpha(mask)
    canvas = Image.alpha_composite(canvas, body)

    # 3) 内缘亮边：只留外圆那一侧的 2px 边
    rim = np.array(erode(mask, 1)).astype(int) - np.array(erode(mask, 3)).astype(int)
    rim_layer = Image.new("RGBA", (S, S), LIGHT + (0,))
    rim_layer.putalpha(Image.fromarray(np.clip(rim, 0, 255).astype(np.uint8)).point(lambda v: int(v * 0.9)))
    canvas = Image.alpha_composite(canvas, rim_layer)

    # 4) 星屑
    d = ImageDraw.Draw(canvas)
    for (x, y, a) in [(25, 5, 210), (28, 11, 130), (5, 27, 150)]:
        d.point((x, y), fill=(255, 255, 255, a))

    canvas.save(os.path.join(ROOT, "Content", "Projectiles", "MoonCrescent.png"))

    prev = Image.new("RGBA", (32 * 10 + 20, 32 * 10 + 20), (58, 48, 66, 255))
    big = canvas.resize((320, 320), Image.NEAREST)
    prev.paste(big, (10, 10), big)
    prev.save(os.path.join(HERE, "moon_preview.png"))
    print("ok")

if __name__ == "__main__":
    main()
