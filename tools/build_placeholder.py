# -*- coding: utf-8 -*-
"""
把两张立绘合成游戏用的 25 帧贴图。

来源：
  tools/ref_design.png  旧图：正面站姿 / 笑脸 / 坐姿 / 闭眼 / 头像稿（绿底）
  tools/ref_poses.png   新图：攻击 2 帧 + 走路 4 帧（白底 + 投影阴影）

去背景方法：从裁切框边缘做泛洪，凡是"接近白色或中性灰"的像素都算背景。
  - 白底、脚下那圈灰投影会被吃掉
  - 被深色描边围住的白发、白裙保得住（泛洪进不去）

用法： python build_placeholder.py
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OLD = os.path.join(HERE, "ref_design.png")
NEW = os.path.join(HERE, "ref_poses.png")
SIT_NEW = os.path.join(HERE, "ref_sit.png")

FW, FH = 40, 56
BODY_H = 52
FEET_Y = 54
PALETTE_SIZE = 24

OLD_POSES = {
    "front":  (458, 587, 653, 942),
    "happy":  (912, 207, 1112, 524),
    "eyescl": (1333, 215, 1504, 520),
}
OLD_HEAD = (41, 679, 372, 942)

# 新图里 6 个姿势的框（自动识别后手工校正过：攻击 2 裁掉了右边那轮月牙）
NEW_POSES = {
    "attack1": (206, 92, 526, 490),
    "attack2": (528, 138, 902, 496),
    "walk1":   (128, 616, 398, 1028),
    "walk2":   (530, 612, 886, 1050),
    "walk3":   (892, 612, 1218, 1050),
    "walk4":   (1284, 612, 1544, 1028),
}


def flood_remove_bg(rgb):
    """从边缘泛洪去掉白底和灰投影，返回 alpha。"""
    h, w, _ = rgb.shape
    c = rgb.astype(np.int16)
    white_dist = np.abs(c - 252).sum(axis=2)
    mx = c.max(axis=2)
    mn = c.min(axis=2)
    bg_like = (white_dist <= 120) | (((mx - mn) <= 34) & (mn >= 170))

    # 非背景像素直接标记为"主体"
    reach = np.zeros((h, w), dtype=bool)
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if bg_like[y, x] and not reach[y, x]:
                reach[y, x] = True
                stack.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if bg_like[y, x] and not reach[y, x]:
                reach[y, x] = True
                stack.append((y, x))

    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not reach[ny, nx] and bg_like[ny, nx]:
                reach[ny, nx] = True
                stack.append((ny, nx))

    alpha = (~reach).astype(np.uint8) * 255
    return alpha


def cut(a, box, use_flood=True, clean=True):
    x0, y0, x1, y1 = box
    rgb = a[y0:y1, x0:x1].astype(np.uint8)
    if use_flood:
        alpha = flood_remove_bg(rgb)
    else:
        bg = a[2, 2]
        d = np.abs(a[y0:y1, x0:x1].astype(np.int16) - bg).sum(axis=2)
        alpha = (d > 40).astype(np.uint8) * 255
    img = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    if clean:
        img = largest_component_only(img)
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def largest_component_only(img):
    arr = np.array(img)
    alpha = arr[:, :, 3] > 32
    h, w = alpha.shape
    seen = np.zeros_like(alpha, dtype=bool)
    best, best_n = None, 0
    for sy in range(h):
        for sx in range(w):
            if not alpha[sy, sx] or seen[sy, sx]:
                continue
            stack = [(sy, sx)]
            seen[sy, sx] = True
            comp = []
            while stack:
                y, x = stack.pop()
                comp.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and alpha[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
            if len(comp) > best_n:
                best, best_n = comp, len(comp)
    if best is None:
        return img
    keep = np.zeros_like(alpha)
    for (y, x) in best:
        keep[y, x] = True
    out = arr.copy()
    out[~keep, 3] = 0
    return Image.fromarray(out, "RGBA")


def load_sit():
    """新的坐姿图是透明背景的 RGBA，直接用 alpha 通道，阈值 128 把软边收紧。
    图里她是朝右坐在凳子上，游戏贴图基准朝左，所以镜像。"""
    img = Image.open(SIT_NEW).convert("RGBA")
    arr = np.array(img)
    alpha = (arr[:, :, 3] > 128).astype(np.uint8) * 255
    out = Image.fromarray(np.dstack([arr[:, :, :3], alpha]), "RGBA")
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    return out.transpose(Image.FLIP_LEFT_RIGHT)


def build_palette(images, size=PALETTE_SIZE):
    total_w = sum(i.width for i in images)
    total_h = max(i.height for i in images)
    canvas = Image.new("RGB", (total_w, total_h), (0, 0, 0))
    x = 0
    for img in images:
        flat = Image.new("RGB", img.size, (0, 0, 0))
        flat.paste(img, (0, 0), img)
        canvas.paste(flat, (x, 0))
        x += img.width
    return canvas.quantize(colors=size, method=Image.MEDIANCUT)


def darken_edges(frame, factor=0.55):
    arr = np.array(frame).astype(np.float32)
    alpha = arr[:, :, 3] > 0
    h, w = alpha.shape
    edge = np.zeros_like(alpha)
    for y in range(h):
        for x in range(w):
            if not alpha[y, x]:
                continue
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if ny < 0 or nx < 0 or ny >= h or nx >= w or not alpha[ny, nx]:
                    edge[y, x] = True
                    break
    arr[edge, :3] *= factor
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def fit_frame(img, palette, body_h=BODY_H):
    # 等比缩放：按 宽/高 里更紧的那个来，绝不拉伸
    scale = min(38.0 / img.width, body_h / img.height)
    w = max(1, round(img.width * scale))
    h = max(1, round(img.height * scale))
    small = img.resize((w, h), Image.LANCZOS)
    alpha = np.array(small)[:, :, 3]
    rgb = small.convert("RGB").quantize(palette=palette, dither=Image.NONE).convert("RGB")
    out = Image.fromarray(np.dstack([np.array(rgb), alpha]), "RGBA")
    frame = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    frame.paste(out, ((FW - w) // 2, FEET_Y - h), out)
    return darken_edges(frame)


def main():
    a_old = np.asarray(Image.open(OLD).convert("RGB")).astype(np.int16)
    a_new = np.asarray(Image.open(NEW).convert("RGB")).astype(np.int16)

    poses = {}
    for k, box in OLD_POSES.items():
        poses[k] = cut(a_old, box, use_flood=False)
    for k, box in NEW_POSES.items():
        poses[k] = cut(a_new, box, use_flood=True)

    poses["sit"] = load_sit()

    # 新立绘的侧身像是朝右的，而游戏贴图基准朝左，所以统一镜像
    MIRROR_WALK = True
    if MIRROR_WALK:
        for k in ('walk1', 'walk2', 'walk3', 'walk4'):
            poses[k] = poses[k].transpose(Image.FLIP_LEFT_RIGHT)

    for k, v in poses.items():
        print(f"  {k}: {v.width}x{v.height}  比例 {v.width / v.height:.2f}")

    palette = build_palette(list(poses.values()))
    frames = {k: fit_frame(v, palette) for k, v in poses.items()}
    # 坐姿单独缩到 48px 高：人坐着本来就比站着矮，避免看起来放大了一号
    frames["sit"] = fit_frame(poses["sit"], palette, body_h=48)

    walk = ["walk1", "walk2", "walk3", "walk4"]
    # 14 帧 = 每个姿势重复 2 帧，节奏比之前慢一半，避免"跺脚"
    walk_seq = [w for w in walk for _ in (0, 1)]
    walk_seq += walk_seq[:6]
    order = [("front", 0, 0), ("front", 0, -1)]
    for name in walk_seq[:14]:
        order.append((name, 0, 0))
    order += [
        ("happy", 0, 0), ("happy", 0, 0), ("sit", 0, 0), ("happy", 0, 0),
        ("eyescl", 0, 0),
        ("attack1", 0, 0), ("attack2", 0, 0), ("attack1", 0, 0), ("attack2", 0, 0),
    ]
    assert len(order) == 25

    sheet = Image.new("RGBA", (FW, FH * 25), (0, 0, 0, 0))
    for i, (name, dx, dy) in enumerate(order):
        f = frames[name]
        if dx or dy:
            moved = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
            moved.paste(f, (dx, dy))
            f = moved
        sheet.paste(f, (0, i * FH))
    sheet.save(os.path.join(ROOT, "Content", "NPCs", "Aurora.png"))

    head = cut(a_old, OLD_HEAD, use_flood=False)
    scale = 38 / max(head.size)
    head = head.resize((max(1, round(head.width * scale)), max(1, round(head.height * scale))), Image.LANCZOS)
    ha = np.array(head)[:, :, 3]
    hrgb = head.convert("RGB").quantize(palette=palette, dither=Image.NONE).convert("RGB")
    head = Image.fromarray(np.dstack([np.array(hrgb), ha]), "RGBA")
    canvas = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    canvas.paste(head, ((40 - head.width) // 2, (40 - head.height) // 2), head)
    canvas.save(os.path.join(ROOT, "Content", "NPCs", "Aurora_Head.png"))

    prev = Image.new("RGBA", (FW * 4 * 5 + 48, FH * 4 * 5 + 48), (74, 96, 72, 255))
    for i in range(25):
        f = sheet.crop((0, i * FH, FW, (i + 1) * FH)).resize((FW * 4, FH * 4), Image.NEAREST)
        prev.paste(f, (8 + (i % 5) * (FW * 4 + 8), 8 + (i // 5) * (FH * 4 + 8)), f)
    prev.save(os.path.join(HERE, "preview_4x.png"))
    print(f"\n已写入 Aurora.png（{sheet.size[0]}x{sheet.size[1]}）")


if __name__ == "__main__":
    main()
