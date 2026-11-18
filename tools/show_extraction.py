# -*- coding: utf-8 -*-
"""
展示「识别」的三步结果，用来核对我看得对不对：
  左   = 立绘里的原始裁切（含白底与投影）
  中   = 去背景 + 只留主体 + 裁掉空白后的结果（棋盘格表示透明）
  右   = 最终写进游戏贴图的那一帧（镜像、量化、归一化到 52px 高）

用法： python show_extraction.py
输出： tools/extract_walk_preview.png
"""
import os
import importlib.util
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

spec = importlib.util.spec_from_file_location("bp", os.path.join(HERE, "build_placeholder.py"))
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

TARGET_H = 300
PAD = 14


def checker(w, h, size=8):
    img = Image.new("RGBA", (w, h), (210, 210, 210, 255))
    d = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    from PIL import ImageDraw
    dd = ImageDraw.Draw(d)
    for y in range(0, h, size):
        for x in range(0, w, size):
            if (x // size + y // size) % 2 == 0:
                dd.rectangle((x, y, x + size - 1, y + size - 1), fill=(176, 176, 176, 255))
    return Image.alpha_composite(img, d)


def fit_h(img, h=TARGET_H):
    s = h / img.height
    return img.resize((max(1, round(img.width * s)), h), Image.LANCZOS)


def main():
    a_new = np.asarray(Image.open(bp.NEW).convert("RGB")).astype(np.int16)
    img_new = Image.open(bp.NEW).convert("RGBA")

    names = ["walk1", "walk2", "walk3", "walk4"]
    boxes = {k: bp.NEW_POSES[k] for k in names}
    cuts = {k: bp.cut(a_new, boxes[k], use_flood=True) for k in names}
    mirrored = {k: cuts[k].transpose(Image.FLIP_LEFT_RIGHT) for k in names}
    palette = bp.build_palette(list(mirrored.values()))
    finals = {k: bp.fit_frame(mirrored[k], palette) for k in names}

    rows = []
    for k in names:
        x0, y0, x1, y1 = boxes[k]
        raw = img_new.crop((x0, y0, x1, y1)).convert("RGBA")
        raw = fit_h(raw)
        cut = fit_h(cuts[k])
        fin = finals[k].resize((40 * 6, 56 * 6), Image.NEAREST)
        rows.append((raw, cut, fin))

    col_w = [max(PAD * 2 + r[i].width for r in rows) for i in range(3)]
    row_h = [max(r[i].height for i in range(3)) for r in rows]
    W = sum(col_w) + PAD * 2
    H = sum(row_h) + PAD * (len(rows) + 1)
    canvas = Image.new("RGBA", (W, H), (52, 44, 60, 255))

    y = PAD
    for ri, row in enumerate(rows):
        x = PAD
        for ci, img in enumerate(row):
            if ci == 1:
                bg = checker(img.width, img.height)
                cell = Image.alpha_composite(bg, img)
                canvas.paste(cell, (x + (col_w[ci] - img.width) // 2, y), cell)
            elif ci == 0:
                cell = Image.new("RGBA", img.size, (245, 245, 245, 255))
                cell.paste(img, (0, 0), img)
                canvas.paste(cell, (x + (col_w[ci] - img.width) // 2, y), cell)
            else:
                canvas.paste(img, (x + (col_w[ci] - img.width) // 2, y), img)
            x += col_w[ci]
        y += row_h[ri] + PAD

    out = os.path.join(HERE, "extract_walk_preview.png")
    canvas.save(out)
    print(out, canvas.size)


if __name__ == "__main__":
    main()
