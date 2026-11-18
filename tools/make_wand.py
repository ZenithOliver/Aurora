# -*- coding: utf-8 -*-
"""
画「阿罗拉的魔杖」的物品贴图（32x32）和玩家版弹幕贴图（16x16）。

配色沿用角色：杖身深紫 #4a345b、亮部 #6a4f7f、缎带 #d5a1be、杖头白光。

用法： python make_wand.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUT = (23, 17, 37)
WOOD = (74, 52, 91)
WOOD_D = (48, 34, 62)
WOOD_L = (110, 82, 132)
GRIP = (58, 42, 72)
PINK = (213, 161, 190)
PINK_L = (240, 208, 223)
GLOW = (236, 228, 250)
WHITE = (255, 255, 255)


def px(d, x, y, c):
    d.point((x, y), fill=c)


def thick_line(d, x0, y0, x1, y1, color, width=2):
    """整数步进的粗线，保证像素边缘硬。"""
    n = max(abs(x1 - x0), abs(y1 - y0))
    for i in range(n + 1):
        t = i / max(1, n)
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        for dx in range(width):
            for dy in range(width):
                px(d, x + dx, y + dy, color)


def build_wand():
    """32x32：细长深紫杖身 + 粉色握把缠带 + 杖头大四角星（不加糊光晕）。"""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 杖身：左下 → 右上，1px 芯 + 1px 暗边
    n = 14
    for i in range(n + 1):
        x = 9 + round(13 * i / n)
        y = 27 - round(14 * i / n)
        px(d, x, y, WOOD)
        px(d, x + 1, y, WOOD_D)
        if i % 4 == 0:
            px(d, x, y, WOOD_L)

    # 握把：深色 + 两道粉带 + 末端结点
    thick_line(d, 9, 27, 11, 25, GRIP, 2)
    px(d, 10, 26, PINK)
    px(d, 11, 25, PINK_L)
    px(d, 9, 27, PINK)
    px(d, 8, 28, OUT)

    # 杖头四角星（臂长 4，中心 2x2 白，外缘淡紫）
    cx, cy = 24, 9
    for i in range(1, 5):
        for (dx, dy) in [(0, -i), (0, i), (-i, 0), (i, 0)]:
            px(d, cx + dx, cy + dy, WHITE if i <= 3 else GLOW)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            px(d, cx + dx, cy + dy, WHITE)
    for (dx, dy) in [(-1, -1), (1, -1), (-1, 1), (1, 1), (-2, -2), (2, 2)]:
        px(d, cx + dx, cy + dy, GLOW)

    # 星屑
    px(d, 30, 5, (238, 232, 250))
    px(d, 18, 22, (238, 232, 250))
    return img

def build_bolt():
    """16x16：白色四角星 + 紧致光晕。"""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    # 光晕不做圆盘，改做四向光斑，看起来才是"星芒"而不是"灰饼"
    glow = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i, a in ((7, 35), (6, 55), (5, 85), (4, 120)):
        for (dx, dy) in [(0, -i), (0, i), (-i, 0), (i, 0)]:
            gd.point((8 + dx, 8 + dy), fill=(255, 255, 255, a))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)
    for (dx, dy) in [(0, -5), (0, 5), (-5, 0), (5, 0)]:
        px(d, 8 + dx, 8 + dy, (232, 224, 250))
    for (dx, dy) in [(0, -4), (0, 4), (-4, 0), (4, 0), (0, -3), (0, 3), (-3, 0), (3, 0)]:
        px(d, 8 + dx, 8 + dy, (245, 240, 255))
    for (dx, dy) in [(0, -2), (0, 2), (-2, 0), (2, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]:
        px(d, 8 + dx, 8 + dy, WHITE)
    return img

def main():
    wand = build_wand()
    os.makedirs(os.path.join(ROOT, "Content", "Items"), exist_ok=True)
    wand.save(os.path.join(ROOT, "Content", "Items", "AuroraWand.png"))
    build_bolt().save(os.path.join(ROOT, "Content", "Projectiles", "AuroraWandBolt.png"))

    # 预览：物品 8 倍 + 弹幕 12 倍
    prev = Image.new("RGBA", (32 * 8 + 16 * 12 + 48, 32 * 8 + 16), (60, 52, 66, 255))
    prev.paste(wand.resize((32 * 8, 32 * 8), Image.NEAREST), (16, 8), wand.resize((32 * 8, 32 * 8), Image.NEAREST))
    b = build_bolt().resize((16 * 12, 16 * 12), Image.NEAREST)
    prev.paste(b, (32 * 8 + 32, 8), b)
    prev.save(os.path.join(HERE, "wand_preview.png"))
    print("ok")


if __name__ == "__main__":
    main()
