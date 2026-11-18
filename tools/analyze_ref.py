# -*- coding: utf-8 -*-
"""
把立绘拆成一个个姿势，并测量它到底是不是「整数倍像素画」。

输出：
  extract_compare.png   原姿势 / 压到 40x56 的效果 / 现在游戏里的贴图
  extract_single.png    单独压好的 40x56 一帧

用法： python analyze_ref.py
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ref_design.png")


def main():
    im = Image.open(SRC).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    bg = a[2, 2]
    diff = np.abs(a - bg).sum(axis=2)
    mask = diff > 40

    print(f"画布 {im.size[0]}x{im.size[1]}，背景色 RGB{tuple(int(v) for v in bg)}")
    print(f"内容占比 {mask.mean()*100:.1f}%")

    # ---- 1. 是不是整数倍放大的像素画？----
    # 做法：按 k 分块取均值再还原，误差应随 k 单调上升；若在某个 k 明显下凹，说明是 k 倍像素画
    big = mask[:, 40:372]
    ys = np.where(big.any(axis=1))[0]
    sub = a[ys[0]:ys[-1] + 1, 40:372].astype(np.float32)
    print("\n按 k 分块压缩再还原的平均误差（越小说明越贴合 k 倍像素格）")
    prev = None
    for k in range(2, 9):
        h, w, _ = sub.shape
        h2, w2 = h // k * k, w // k * k
        c = sub[:h2, :w2].reshape(h2 // k, k, w2 // k, k, 3)
        up = np.repeat(np.repeat(c.mean(axis=(1, 3)), k, axis=0), k, axis=1)
        mae = float(np.abs(up - sub[:h2, :w2]).mean())
        print(f"  k={k}: {mae:5.2f}" + ("  ← 与上一个相同，无凹陷" if prev and abs(mae - prev) < 1.2 else ""))
        prev = mae

    # ---- 2. 颜色有多「平」----
    px = a[ys[0]:ys[-1] + 1, 40:372][big[ys[0]:ys[-1] + 1]]
    colors, counts = np.unique(px.reshape(-1, 3), axis=0, return_counts=True)
    order = np.argsort(-counts)
    top16 = counts[order[:16]].sum() / counts.sum()
    print(f"\n这块大图里的独立颜色数：{len(colors)}")
    print(f"出现最多的 16 种颜色合计占比：{top16*100:.1f}%")

    cur = Image.open(os.path.join(HERE, "..", "Content", "NPCs", "Aurora.png")).convert("RGBA")
    f0 = np.array(cur.crop((0, 0, 40, 56)))
    vis = f0[f0[:, :, 3] > 0][:, :3]
    cc, cn = np.unique(vis, axis=0, return_counts=True)
    t16 = np.sort(cn)[::-1][:16].sum() / cn.sum()
    print(f"对比：现在这帧 40x56 贴图有 {len(cc)} 色，最多的 16 色占 {t16*100:.1f}%")

    # ---- 3. 拆出各个姿势（先按列切，再按行切）----
    def split_cols(m, thr=2, gap=6):
        cs = m.sum(axis=0)
        out, x, W = [], 0, len(cs)
        while x < W:
            if cs[x] <= thr:
                x += 1
                continue
            s = x
            last = x
            while x < W:
                if cs[x] > thr:
                    last = x
                elif x - last > gap:
                    break
                x += 1
            out.append((s, last + 1))
        return out

    def split_rows(m, x0, x1, thr=2, gap=4):
        rs = m[:, x0:x1].sum(axis=1)
        out, y, H = [], 0, len(rs)
        while y < H:
            if rs[y] <= thr:
                y += 1
                continue
            s = y
            last = y
            while y < H:
                if rs[y] > thr:
                    last = y
                elif y - last > gap:
                    break
                y += 1
            out.append((s, last + 1))
        return out

    boxes = []
    for (x0, x1) in split_cols(mask):
        for (y0, y1) in split_rows(mask, x0, x1):
            if (x1 - x0) * (y1 - y0) > 3000:
                boxes.append((x0, y0, x1, y1))

    print(f"\n拆出 {len(boxes)} 个姿势：")
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        print(f"  #{i}: {x1-x0}x{y1-y0}  @({x0},{y0})")

    # ---- 4. 把第 2 个姿势（侧身站姿）压成 40x56 ----
    if len(boxes) < 2:
        return
    x0, y0, x1, y1 = boxes[1]
    crop = a[y0:y1, x0:x1].astype(np.uint8)
    m = mask[y0:y1, x0:x1]
    rgba = np.dstack([crop, (m * 255).astype(np.uint8)])
    src = Image.fromarray(rgba, "RGBA")

    scale = 54 / src.height if src.height > 54 else 1
    tw = max(1, round(src.width * scale))
    small = src.resize((tw, 54), Image.LANCZOS)
    # 颜色量化：把几千种渐变压到 12 色，像素画才立得住
    rgb = small.convert("RGB")
    q = rgb.quantize(colors=12, method=Image.MEDIANCUT).convert("RGB")
    small = Image.fromarray(np.dstack([np.array(q), np.array(small)[:, :, 3]]), "RGBA")
    small.save(os.path.join(HERE, "extract_single.png"))

    frame = Image.new("RGBA", (40, 56), (0, 0, 0, 0))
    frame.paste(small, ((40 - small.width) // 2, 55 - small.height), small)
    frame = frame.resize((40 * 8, 56 * 8), Image.NEAREST)

    orig = src.resize((src.width * 2, src.height * 2), Image.LANCZOS)
    cur_f = cur.crop((0, 0, 40, 56)).resize((40 * 8, 56 * 8), Image.NEAREST)

    pad = 14
    W = orig.width + frame.width + cur_f.width + pad * 4
    H = max(orig.height, frame.height, cur_f.height) + pad * 2
    out = Image.new("RGBA", (W, H), (74, 96, 72, 255))
    x = pad
    for img in (orig, frame, cur_f):
        out.paste(img, (x, (H - img.height) // 2), img)
        x += img.width + pad
    out.save(os.path.join(HERE, "extract_compare.png"))
    print("\n已输出 extract_compare.png（左：原姿势 / 中：压到 40x56 / 右：现在的贴图）")


if __name__ == "__main__":
    main()
