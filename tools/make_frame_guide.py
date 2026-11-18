# -*- coding: utf-8 -*-
"""
生成一张「画图参考网格」：25 帧、每帧 40x56，放大 4 倍，带帧号、脚底线、中轴线。

它只用来当参考图层（在 Aseprite 里放到最底层，画完删掉），
不要直接在上面画——里面的洋红/青色线条会被导出进贴图。

用法： python make_frame_guide.py
输出： tools/frame_guide.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

FRAME_W, FRAME_H = 40, 56
FRAMES = 25
SCALE = 4
W, H = FRAME_W * SCALE, FRAME_H * SCALE

GUIDE_BORDER = (255, 0, 170, 130)
GUIDE_BASELINE = (0, 240, 255, 150)
GUIDE_CENTER = (40, 40, 70, 110)
GUIDE_TEXT = (255, 0, 170, 200)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    canvas = Image.new("RGBA", (W, H * FRAMES), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    f = font(18)

    for i in range(FRAMES):
        top = i * H
        bottom = top + H - 1
        # 帧边框
        d.rectangle((0, top, W - 1, bottom), outline=GUIDE_BORDER, width=1)
        # 脚底线：人物鞋底应该压在这条线上（帧底往上 2px）
        by = top + (FRAME_H - 2) * SCALE
        for x in range(0, W, 12):
            d.line((x, by, x + 6, by), fill=GUIDE_BASELINE, width=1)
        # 中轴线
        cx = W // 2
        for y in range(top, bottom, 12):
            d.line((cx, y, cx, y + 5), fill=GUIDE_CENTER, width=1)
        # 帧号 + 用途
        label = f"{i}"
        d.text((4, top + 3), label, font=f, fill=GUIDE_TEXT)

    out = os.path.join(here, "frame_guide.png")
    canvas.save(out)
    print(f"{out}  ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()
