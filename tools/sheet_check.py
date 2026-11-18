# -*- coding: utf-8 -*-
"""
贴图自检 + 头像生成工具。

用法：
    python sheet_check.py                          # 检查 mod 自带的 Aurora.png
    python sheet_check.py 我的图.png                # 检查任意贴图
    python sheet_check.py 我的图.png --crop 8,1,32,29   # 顺便生成头像

检查项：
  - 高度能否被 25 整除（每个城镇 NPC 必须有 25 帧）
  - 每帧是否为正方形或接近原版比例（原版约 40x56）
  - 是否存在透明边距问题（角色顶到帧边缘会在游戏里被裁掉）
  - 生成 4x 预览图，方便肉眼检查
"""
import os
import sys
from PIL import Image

FRAMES = 25


def load(path):
    img = Image.open(path).convert("RGBA")
    return img


def check(path):
    img = load(path)
    w, h = img.size
    print(f"文件: {os.path.basename(path)}")
    print(f"尺寸: {w} x {h}")
    if h % FRAMES != 0:
        print(f"[错误] 高度 {h} 不能被 {FRAMES} 整除，每帧高度会是小数。"
              f"建议高度: {round(h / FRAMES) * FRAMES}")
        return None
    fh = h // FRAMES
    print(f"每帧: {w} x {fh}")
    if abs(w - 40) > 8 or abs(fh - 56) > 8:
        print(f"[提醒] 帧尺寸 {w}x{fh} 与原版 40x56 差得比较多，"
              f"判定框（NPC.width/height）可能需要跟着调。")

    # 逐帧边距检查
    tight = []
    for i in range(FRAMES):
        f = img.crop((0, i * fh, w, (i + 1) * fh))
        bbox = f.getbbox()
        if bbox is None:
            tight.append((i, "空帧"))
            continue
        x0, y0, x1, y1 = bbox
        if x0 == 0 or y0 == 0 or x1 == w or y1 == fh:
            tight.append((i, f"内容贴边 {bbox}"))
    if tight:
        print("[提醒] 以下帧的内容顶到了帧边缘（游戏里不会裁切，但相邻帧会视觉粘连）:")
        for i, msg in tight:
            print(f"   帧 {i}: {msg}")
    else:
        print("边距: 所有帧都有留白，OK")
    return img, fh


def make_head(img, fh, crop, out_dir):
    x0, y0, x1, y1 = crop
    f0 = img.crop((0, 0, img.size[0], fh))
    head = f0.crop((x0, y0, x1, y1))
    canvas = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    canvas.paste(head, ((40 - head.size[0]) // 2, (40 - head.size[1]) // 2), head)
    p = os.path.join(out_dir, "Aurora_Head.png")
    canvas.save(p)
    print(f"头像已生成: {p} ({head.size[0]}x{head.size[1]} 放入 40x40)")


def preview(img, fh, out_dir):
    w, h = img.size
    scale = 4
    prev = Image.new("RGBA", (w * scale + 16, h * scale + 16), (74, 96, 72, 255))
    big = img.resize((w * scale, h * scale), Image.NEAREST)
    prev.paste(big, (8, 8), big)
    p = os.path.join(out_dir, "sheet_preview_4x.png")
    prev.save(p)
    print(f"预览已生成: {p}")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    args = sys.argv[1:]
    crop = None
    if "--crop" in args:
        i = args.index("--crop")
        crop = tuple(int(v) for v in args[i + 1].split(","))
        del args[i:i + 2]
    path = args[0] if args else os.path.join(root, "Content", "NPCs", "Aurora.png")

    res = check(path)
    if res is None:
        sys.exit(1)
    img, fh = res
    out_dir = here  # 预览图放 tools/，避免混进 Content 被当成贴图
    preview(img, fh, out_dir)
    if crop:
        make_head(img, fh, crop, out_dir)
    else:
        print("（如需生成头像，加 --crop x0,y0,x1,y1；默认值 8,1,32,29）")


if __name__ == "__main__":
    main()
