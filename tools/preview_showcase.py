# -*- coding: utf-8 -*-
"""
拼一张展示图：挑几帧放大 + 头像 + 物品 + 增益 + mod 图标。
纯粹用来看，不参与 mod 打包。

用法： python preview_showcase.py
"""
import os
from PIL import Image, ImageDraw

SHEET = "../Content/NPCs/Aurora.png"
HEAD = "../Content/NPCs/Aurora_Head.png"
ITEM = "../Content/Projectiles/ArcaneBolt.png"
BOLT = "../Content/Projectiles/ArcaneBolt.png"
ICON = "../icon.png"

PICK = [0, 3, 9, 16, 18, 21]   # 站立 / 行走 / 抬手 / 坐 / 攻击
LABELS = ["idle", "walk", "walk2", "raise", "sit", "cast"]
SCALE = 5
BG = (46, 54, 48, 255)
PANEL = (62, 76, 66, 255)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    sheet = Image.open(SHEET).convert("RGBA")
    fh = sheet.size[1] // 25
    cells = []
    for i in PICK:
        f = sheet.crop((0, i * fh, sheet.size[0], (i + 1) * fh))
        cells.append(f.resize((f.size[0] * SCALE, f.size[1] * SCALE), Image.NEAREST))

    cw, ch = cells[0].size
    gap = 10
    icon_h = 96
    W = gap + len(cells) * (cw + gap)
    H = gap + ch + gap + icon_h + gap
    img = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(img)

    for k, c in enumerate(cells):
        x = gap + k * (cw + gap)
        y = gap
        d.rectangle((x - 2, y - 2, x + cw + 1, y + ch + 1), fill=PANEL)
        img.paste(c, (x, y), c)

    # 下方图标条
    y0 = gap + ch + gap
    x = gap
    for path, s in ((HEAD, 3), (BOLT, 4), (ICON, 1)):
        im = Image.open(path).convert("RGBA")
        im = im.resize((im.size[0] * s, im.size[1] * s), Image.NEAREST)
        d.rectangle((x - 2, y0 - 2, x + im.size[0] + 1, y0 + im.size[1] + 1), fill=PANEL)
        img.paste(im, (x, y0), im)
        x += im.size[0] + gap + 6

    out = os.path.join(here, "showcase.png")
    img.save(out)
    print(out, img.size)


if __name__ == "__main__":
    main()
