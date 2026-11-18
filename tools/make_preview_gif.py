# -*- coding: utf-8 -*-
"""
把 25 帧贴图拼成一个循环 GIF，用来在不启动游戏的情况下看动画效果。

用法： python make_preview_gif.py
输出： tools/preview_anim.gif
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "..", "Content", "NPCs", "Aurora.png")
OUT = os.path.join(HERE, "preview_anim.gif")

FW, FH = 40, 56
SCALE = 4


def seq():
    """模拟游戏里的使用节奏：站立 → 走路 → 坐 → 抬手 → 说话 → 眨眼 → 施法。"""
    s = []
    s += [0] * 6                       # 站着
    s += list(range(2, 16))            # 走一圈（14 帧）
    s += [0] * 2
    s += [18] * 8                      # 坐下
    s += [0] * 2
    s += [16, 17] * 3                  # 抬手
    s += [19] * 6                      # 说话
    s += [0] * 2
    s += [20] + [0] * 4                # 眨一下
    s += [21] * 4 + [22] * 4           # 施法
    s += [0] * 4
    return s


def main():
    sheet = Image.open(SHEET).convert("RGBA")
    frames = []
    for i in seq():
        f = sheet.crop((0, i * FH, FW, (i + 1) * FH))
        f = f.resize((FW * SCALE, FH * SCALE), Image.NEAREST)
        bg = Image.new("RGBA", f.size, (74, 96, 72, 255))
        bg.alpha_composite(f)
        frames.append(bg.convert("P", palette=Image.ADAPTIVE, colors=64))

    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=90, loop=0, optimize=False)
    print(f"{OUT}  ({len(frames)} 帧)")


if __name__ == "__main__":
    main()
