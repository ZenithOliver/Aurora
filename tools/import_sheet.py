# -*- coding: utf-8 -*-
"""
把你自己画的图转换成游戏能用的贴图。

支持的输入：
  1) 整张贴图（竖向 25 帧，或 5x5 网格）——任意整数倍尺寸，比如 80x2800、160x5600
  2) 一个文件夹，里面是 25 张按顺序命名的 PNG（00.png / 01.png ...）

输出：
  Content/NPCs/Aurora.png      游戏用贴图（40 x 1400）
  Content/NPCs/Aurora_Head.png 地图/房屋头像（40x40，可选）
  tools/preview_4x.png         4 倍预览，用来肉眼检查

用法：
  python import_sheet.py 我的图.png
  python import_sheet.py ./frames
  python import_sheet.py 我的图.png --head-crop 8,2,32,30 --out Aurora.png
"""
import os
import sys
from PIL import Image

FRAME_W, FRAME_H = 40, 56
DEFAULT_FRAMES = 25


def load_input(path, frames):
    """读入输入，统一返回 (sheet, 来源说明)。"""
    if os.path.isdir(path):
        files = sorted(f for f in os.listdir(path) if f.lower().endswith(".png"))
        if len(files) != frames:
            raise SystemExit(f"文件夹里有 {len(files)} 张 PNG，需要 {frames} 张（每帧一张）")
        imgs = [Image.open(os.path.join(path, f)).convert("RGBA") for f in files]
        sizes = {im.size for im in imgs}
        if len(sizes) != 1:
            raise SystemExit(f"这 25 张图尺寸不一致：{sorted(sizes)}，必须全部同尺寸")
        w, h = imgs[0].size
        sheet = Image.new("RGBA", (w, h * frames), (0, 0, 0, 0))
        for i, im in enumerate(imgs):
            sheet.paste(im, (0, i * h))
        return sheet, f"文件夹（每帧 {w}x{h}）"

    img = Image.open(path).convert("RGBA")
    return img, f"单张图 {img.size[0]}x{img.size[1]}"


def to_game_sheet(img, frames):
    """把任意尺寸的图规整成 40x56 / 帧、竖向排列。"""
    w, h = img.size

    # 情况 A：已经是 5x5 网格（每帧 40x56）
    if w % FRAME_W == 0 and h % FRAME_H == 0 and (w // FRAME_W) * (h // FRAME_H) == frames:
        cols, rows = w // FRAME_W, h // FRAME_H
        if cols * rows == frames:
            out = Image.new("RGBA", (FRAME_W, FRAME_H * frames), (0, 0, 0, 0))
            for r in range(rows):
                for c in range(cols):
                    i = r * cols + c
                    frame = img.crop((c * FRAME_W, r * FRAME_H, (c + 1) * FRAME_W, (r + 1) * FRAME_H))
                    out.paste(frame, (0, i * FRAME_H))
            return out, f"识别为 {cols}x{rows} 网格"

    # 情况 B：竖向单列
    if h % frames != 0:
        raise SystemExit(
            f"高度 {h} 不能被 {frames} 整除。\n"
            f"竖向排列时高度必须是 {frames} 的整数倍，例如 {FRAME_H * frames}（1x）或 {FRAME_H * frames * 2}（2x）。")
    fh = h // frames
    fw = w
    if fw == FRAME_W and fh == FRAME_H:
        return img, "尺寸已经是 40x56 / 帧，直接使用"

    scale = min(FRAME_W / fw, FRAME_H / fh)
    nw, nh = max(1, round(fw * scale)), max(1, round(fh * scale))
    out = Image.new("RGBA", (FRAME_W, FRAME_H * frames), (0, 0, 0, 0))
    for i in range(frames):
        frame = img.crop((0, i * fh, fw, (i + 1) * fh))
        # 最近邻缩放，保住像素边缘（不要用双线性，会糊）
        frame = frame.resize((nw, nh), Image.NEAREST)
        x = (FRAME_W - nw) // 2
        y = FRAME_H - nh          # 底对齐：脚贴住帧底
        out.paste(frame, (x, i * FRAME_H + y), frame)
    return out, f"每帧 {fw}x{fh} → 缩放到 {nw}x{nh} 并底对齐"


def make_head(sheet, crop):
    x0, y0, x1, y1 = crop
    f0 = sheet.crop((0, 0, FRAME_W, FRAME_H))
    head = f0.crop((x0, y0, x1, y1))
    s = min(40 / head.size[0], 40 / head.size[1])
    head = head.resize((max(1, round(head.size[0] * s)), max(1, round(head.size[1] * s))), Image.NEAREST)
    canvas = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    canvas.paste(head, ((40 - head.size[0]) // 2, (40 - head.size[1]) // 2), head)
    return canvas


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    frames = DEFAULT_FRAMES
    out_name = "Aurora.png"
    head_crop = (8, 2, 32, 30)
    do_head = True

    if "--frames" in args:
        i = args.index("--frames")
        frames = int(args[i + 1])
        del args[i:i + 2]
    if "--out" in args:
        i = args.index("--out")
        out_name = args[i + 1]
        del args[i:i + 2]
    if "--head-crop" in args:
        i = args.index("--head-crop")
        head_crop = tuple(int(v) for v in args[i + 1].split(","))
        del args[i:i + 2]
    if "--no-head" in args:
        do_head = False
        args.remove("--no-head")

    src = args[0]
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)

    img, desc = load_input(src, frames)
    print(f"输入：{desc}")
    sheet, how = to_game_sheet(img, frames)
    print(f"处理：{how}")
    print(f"输出：{sheet.size[0]}x{sheet.size[1]}（每帧 {FRAME_W}x{FRAME_H}，共 {frames} 帧）")

    os.makedirs(os.path.join(root, "Content", "NPCs"), exist_ok=True)
    sheet_path = os.path.join(root, "Content", "NPCs", out_name)
    sheet.save(sheet_path)
    print(f"  贴图 -> {sheet_path}")

    if do_head:
        head_path = os.path.join(root, "Content", "NPCs",
                                 os.path.splitext(out_name)[0] + "_Head.png")
        make_head(sheet, head_crop).save(head_path)
        print(f"  头像 -> {head_path}（裁切框 {head_crop}）")

    # 4 倍预览
    prev = Image.new("RGBA", (FRAME_W * 4 * 5 + 48, FRAME_H * 4 * 5 + 48), (74, 96, 72, 255))
    for i in range(frames):
        f = sheet.crop((0, i * FRAME_H, FRAME_W, (i + 1) * FRAME_H))
        big = f.resize((FRAME_W * 4, FRAME_H * 4), Image.NEAREST)
        prev.paste(big, (8 + (i % 5) * (FRAME_W * 4 + 8), 8 + (i // 5) * (FRAME_H * 4 + 8)), big)
    prev_path = os.path.join(here, "preview_4x.png")
    prev.save(prev_path)
    print(f"  预览 -> {prev_path}")

    print("\n下一步：python sheet_check.py          # 检查边距/贴边问题")


if __name__ == "__main__":
    main()
