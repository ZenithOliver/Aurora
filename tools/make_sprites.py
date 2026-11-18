# -*- coding: utf-8 -*-
"""
「阿罗拉」城镇 NPC 贴图生成器（40x56 / 25 帧）。

配色取自 tools/ref_design.png（立绘）：
  外描边 #191025 / 裙子 #4a345b · #6a4f7f / 蝶结与内耳 #d5a1be / 发色 #f1e9f0

比例（Q 版大头，从脚底向上推）：
  靴 49-54 / 腿 45-48 / 裙 27-44 / 头 14-26 / 耳 3-12

帧序：0 站 / 1 跳 / 2-15 走 / 16-17 抬手 / 18 坐 / 19 说话 / 20 眨眼 / 21-24 攻击
"""
import os
import math
from PIL import Image, ImageDraw

W, H = 40, 56
FRAMES = 25
CX = 20

# ---------- 立绘取色 ----------
OUT = (23, 17, 37)
HAIR = (240, 236, 246)
HAIR_D = (198, 188, 214)
HAIR_S = (146, 136, 168)
SKIN = (250, 220, 208)
SKIN_D = (214, 172, 166)
DRESS = (74, 52, 91)
DRESS_D = (52, 35, 67)
DRESS_L = (106, 79, 127)
MAUVE = (144, 97, 144)
PINK = (213, 161, 190)
PINK_L = (239, 205, 221)
LENS = (226, 166, 192)
LENS_D = (176, 112, 146)
BOOT = (48, 35, 64)
BOOT_L = (86, 62, 108)
TAIL = (247, 242, 245)
EYE = (42, 31, 54)
MOUTH = (172, 110, 112)
STAR = (246, 214, 128)

# ---------- 纵向基准 ----------
HEAD_TOP = 14          # 头顶（发际线）
HEAD_H = 13
BODY_TOP = HEAD_TOP + HEAD_H   # 27 肩线
HEM = 44               # 裙摆底
HIP = 45


def new_frame():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def px(d, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        d.point((x, y), fill=c)


def rect(d, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(d, x, y, c)


def hline(d, x0, x1, y, c):
    for x in range(x0, x1 + 1):
        px(d, x, y, c)


def vline(d, x, y0, y1, c):
    for y in range(y0, y1 + 1):
        px(d, x, y, c)


# ---------- 部件 ----------

def draw_ears(d, base_y, twitch=0, droop=0):
    """两只细长兔耳：base_y 为耳根，向上生长 10px。"""
    for side in (-1, 1):
        bx = CX + side * 3
        tipx = CX + side * 6 + twitch * side
        tipy = base_y - 10 + droop
        span = max(1, base_y - tipy)
        for i in range(span + 1):
            t = i / span
            x = round(bx + (tipx - bx) * t)
            y = base_y - i
            px(d, x, y, HAIR)
            px(d, x + 1, y, HAIR)
            px(d, x + 1, y, HAIR_D)
            if 2 <= i <= 7:
                px(d, x, y, PINK)
                if i == 4:
                    px(d, x, y, PINK_L)


def draw_back_hair(d, top, bottom, sway=0):
    """垂在身后、从裙侧露出的长发。"""
    for y in range(top, bottom + 1):
        t = (y - top) / max(1, (bottom - top))
        half = 4 + int(round(t * 2))
        hline(d, CX - half + sway, CX + half + sway, y, HAIR)
        px(d, CX - half + sway, y, HAIR_D)
        px(d, CX + half + sway, y, HAIR_D)
        if y % 5 == 0:
            px(d, CX - half + 1 + sway, y, HAIR_S)


def draw_tail(d, x, y):
    """白色绒球尾巴。"""
    rect(d, x, y, x + 2, y + 2, TAIL)
    px(d, x + 1, y, (255, 255, 255))
    px(d, x + 2, y + 2, HAIR_D)
    px(d, x, y + 2, HAIR_D)


def draw_legs(d, hip, ldx=0, rdx=0, lift=0, sit=False):
    if sit:
        # 坐在地上：大腿向前（画面右侧）伸，靴子垂下
        rect(d, CX - 4, hip - 2, CX + 3, hip - 1, SKIN)
        hline(d, CX - 4, CX + 3, hip - 1, SKIN_D)
        rect(d, CX + 3, hip - 1, CX + 5, hip + 2, BOOT)
        hline(d, CX + 3, CX + 5, hip - 1, BOOT_L)
        hline(d, CX + 3, CX + 6, hip + 2, BOOT)
        return
    # 左腿（长靴盖住大部分腿）
    rect(d, CX - 3 + ldx, hip - 4, CX - 1 + ldx, hip - 2, SKIN)
    rect(d, CX - 3 + ldx, hip - 1, CX - 1 + ldx, hip + 5, BOOT)
    hline(d, CX - 3 + ldx, CX - 1 + ldx, hip - 1, BOOT_L)
    hline(d, CX - 4 + ldx, CX - 1 + ldx, hip + 5, BOOT)
    # 右腿
    rect(d, CX + 1 + rdx, hip - 4 - lift, CX + 3 + rdx, hip - 2 - lift, SKIN)
    rect(d, CX + 1 + rdx, hip - 1 - lift, CX + 3 + rdx, hip + 5 - lift, BOOT)
    hline(d, CX + 1 + rdx, CX + 3 + rdx, hip - 1 - lift, BOOT_L)
    hline(d, CX + 1 + rdx, CX + 4 + rdx, hip + 5 - lift, BOOT)


def draw_dress(d, top, hem):
    """深紫连衣裙：收腰 + 荷叶边裙摆 + 腰间粉缎带 + 胸前浅色内衬。"""
    waist = top + 6
    for y in range(top, hem + 1):
        if y <= waist:
            half = 3
        else:
            t = (y - waist) / max(1.0, (hem - waist))
            half = 3 + int(round(t * 4))
        hline(d, CX - half, CX + half, y, DRESS)
        px(d, CX + half, y, DRESS_D)
        if y % 2 == 0:
            px(d, CX - half, y, DRESS_L)
    # 胸前浅色内衬（立绘的白/粉胸口）
    hline(d, CX - 2, CX + 1, top, PINK_L)
    rect(d, CX - 2, top + 1, CX + 1, top + 2, PINK_L)
    hline(d, CX - 2, CX + 1, top + 3, PINK)
    px(d, CX, top + 1, PINK)
    px(d, CX - 1, top + 1, PINK)
    # 腰间缎带
    hline(d, CX - 3, CX + 3, waist, PINK)
    hline(d, CX - 2, CX + 2, waist + 1, MAUVE)
    px(d, CX, waist, PINK_L)
    # 裙摆荷叶边
    hline(d, CX - 7, CX + 7, hem, DRESS_L)
    for x in range(CX - 7, CX + 8, 2):
        px(d, x, hem + 1, DRESS_L)


def draw_arm(d, top, side, pose="idle"):
    x = CX + side * 4
    if pose == "idle":
        vline(d, x, top + 1, top + 8, SKIN)
        px(d, x, top + 9, SKIN_D)
    elif pose == "raise":
        vline(d, x + side, top - 1, top + 3, SKIN)
        px(d, x + side * 2, top - 2, SKIN)
    elif pose == "cast":
        # 手只负责握杖，光效交给魔杖杖头
        vline(d, x + side, top, top + 4, SKIN)
        px(d, x + side, top + 5, SKIN_D)


def draw_head(d, top, face="normal"):
    """头：11 宽，脸 9 宽。靠明度差把脸从头发里分出来。"""
    # 头发外轮廓（比脸宽 1px）
    rect(d, CX - 5, top, CX + 5, top + 12, HAIR)
    hline(d, CX - 5, CX + 5, top + 12, HAIR_D)
    # 脸
    rect(d, CX - 4, top + 2, CX + 4, top + 11, SKIN)
    # 下巴
    hline(d, CX - 3, CX + 3, top + 11, SKIN_D)
    px(d, CX - 4, top + 12, HAIR)
    px(d, CX + 4, top + 12, HAIR)
    # 刘海 + 额头阴影
    hline(d, CX - 5, CX + 5, top, HAIR)
    hline(d, CX - 5, CX + 5, top + 1, HAIR)
    hline(d, CX - 5, CX + 5, top + 2, HAIR_D)
    hline(d, CX - 4, CX - 2, top + 3, HAIR)
    hline(d, CX + 2, CX + 4, top + 3, HAIR)
    px(d, CX, top + 3, HAIR_S)
    # 右侧压暗 + 左侧高光
    vline(d, CX + 5, top + 1, top + 12, HAIR_D)
    px(d, CX - 4, top + 1, (255, 255, 255))
    px(d, CX - 3, top + 1, (255, 255, 255))
    # 鬓发（垂过下巴）
    vline(d, CX - 5, top + 3, top + 13, HAIR)
    vline(d, CX + 5, top + 3, top + 13, HAIR_D)
    # 眼镜：粉镜片 + 藕紫下框（别用近黑，会变成一条眼罩）
    gy = top + 6
    for lx in (CX - 4, CX + 1):
        hline(d, lx, lx + 2, gy, LENS)
        px(d, lx + 2, gy, LENS_D)
        px(d, lx, gy + 1, LENS)
        px(d, lx + 1, gy + 1, LENS_D)
        px(d, lx + 2, gy + 1, MAUVE)
        hline(d, lx, lx + 2, gy + 1, MAUVE)
        px(d, lx, gy + 1, LENS)
        px(d, lx, gy, (255, 255, 255))
    # 镜桥
    hline(d, CX - 1, CX, gy, MAUVE)
    # 腮红
    px(d, CX - 3, top + 9, (238, 168, 176))
    px(d, CX + 3, top + 9, (238, 168, 176))
    # 嘴
    if face == "talk":
        rect(d, CX - 1, top + 9, CX, top + 10, MOUTH)
    else:
        hline(d, CX - 1, CX, top + 9, MOUTH)
    # 眨眼
    if face == "blink":
        hline(d, CX - 4, CX + 2, gy + 1, LENS_D)
        px(d, CX - 3, gy + 1, EYE)
        px(d, CX + 2, gy + 1, EYE)


def draw_bow(d, x, y):
    """侧头的粉色蝴蝶结。"""
    rect(d, x, y, x + 1, y + 1, PINK)
    rect(d, x + 3, y, x + 4, y + 1, PINK)
    px(d, x, y, PINK_L)
    px(d, x + 4, y, PINK_L)
    hline(d, x, x + 4, y + 2, MAUVE)
    hline(d, x + 1, x + 3, y + 2, PINK_L)
    rect(d, x + 2, y + 3, x + 3, y + 4, PINK)
    px(d, x + 2, y + 4, MAUVE)


def draw_wand(d, top):
    """魔杖：斜向上三格杖身 + 杖头白光。"""
    x0, y0 = CX + 5, top + 1
    for i in range(3):
        px(d, x0 + i, y0 - i, (122, 94, 76))
    tipx, tipy = x0 + 3, y0 - 3
    px(d, tipx, tipy, (255, 255, 255))
    px(d, tipx + 1, tipy, PINK_L)
    px(d, tipx, tipy - 1, PINK_L)
    px(d, tipx + 1, tipy - 1, (236, 230, 252))
    px(d, tipx + 2, tipy, (255, 255, 255))


def draw_frame(p):
    img = new_frame()
    d = ImageDraw.Draw(img)
    bob = p.get("bob", 0)
    sit = p.get("sit", False)

    if sit:
        head_top = HEAD_TOP + 8
        body_top = head_top + HEAD_H
        hem = HEM + 4
        hip = HIP + 4
    else:
        head_top = HEAD_TOP + bob
        body_top = head_top + HEAD_H
        hem = HEM + bob
        hip = HIP + bob

    draw_back_hair(d, body_top - 6, hip - 2, p.get("sway", 0))
    if not sit:
        draw_tail(d, CX + 6, hem - 4)
    draw_legs(d, hip, p.get("ldx", 0), p.get("rdx", 0), p.get("lift", 0), sit)
    draw_dress(d, body_top, hem)
    draw_arm(d, body_top, -1, p.get("arm_l", "idle"))
    draw_arm(d, body_top, +1, p.get("arm_r", "idle"))
    if p.get("arm_r") == "cast":
        draw_wand(d, body_top)
    draw_head(d, head_top, p.get("face", "normal"))
    draw_ears(d, head_top + 1, p.get("twitch", 0), p.get("droop", 0))
    draw_bow(d, CX - 10, head_top + 2)

    shifted = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shifted.paste(img, (0, 1))
    return shifted


def add_outline(img, color=OUT):
    w, h = img.size
    a = img.split()[3].load()
    out = img.load()
    edge = []
    for y in range(h):
        for x in range(w):
            if a[x, y] > 0:
                continue
            if ((x > 0 and a[x - 1, y] > 0) or (x < w - 1 and a[x + 1, y] > 0)
                    or (y > 0 and a[x, y - 1] > 0) or (y < h - 1 and a[x, y + 1] > 0)):
                edge.append((x, y))
    for (x, y) in edge:
        out[x, y] = color + (255,)
    return img


def build_poses():
    poses = [{}]
    poses.append({"bob": -1, "ldx": 1, "rdx": -1, "arm_l": "raise", "twitch": 1})
    for half in (0, 1):
        for i in range(7):
            t = i / 7.0 * math.tau
            dx = int(round(1 * math.sin(t)))
            if half:
                dx = -dx
            bob = -1 if i in (2, 3) else 0
            poses.append({
                "ldx": dx, "rdx": -dx, "bob": bob,
                "lift": 1 if i in (5, 6) else 0,
                "twitch": 1 if i in (0, 4) else 0,
                "sway": dx,
                "arm_l": "idle",
                "arm_r": "raise" if i in (2, 3) else "idle",
            })
    poses.append({"arm_r": "raise", "twitch": 1})
    poses.append({"arm_r": "raise", "arm_l": "raise", "twitch": 1})
    poses.append({"sit": True, "face": "talk"})
    poses.append({"face": "talk"})
    poses.append({"face": "blink", "droop": 1})
    poses.append({"arm_r": "cast", "bob": -1, "face": "talk"})
    poses.append({"arm_r": "cast", "bob": -1, "face": "talk", "ldx": 1, "rdx": -1})
    poses.append({"arm_r": "cast", "bob": -1})
    poses.append({"arm_r": "cast", "bob": -1, "ldx": 1, "rdx": -1})
    assert len(poses) == FRAMES
    return poses


def build_item():
    """16x16：一瓶粉色星砂。"""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rect(d, 5, 6, 10, 13, (234, 216, 232))
    rect(d, 5, 9, 10, 13, PINK)
    rect(d, 6, 10, 9, 12, PINK_L)
    hline(d, 5, 10, 13, (198, 172, 200))
    rect(d, 7, 4, 8, 5, (210, 188, 210))
    rect(d, 7, 2, 8, 3, (150, 116, 96))
    px(d, 6, 7, (255, 255, 255))
    px(d, 6, 8, (255, 255, 255))
    px(d, 8, 10, STAR)
    px(d, 7, 12, STAR)
    px(d, 9, 12, (255, 246, 210))
    return add_outline(img)


def build_buff():
    """32x32：粉色四角星。"""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = 15
    d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(120, 78, 120, 90))
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(176, 126, 168, 150))
    pts = [(cx, cy - 10), (cx + 3, cy - 3), (cx + 10, cy), (cx + 3, cy + 3),
           (cx, cy + 10), (cx - 3, cy + 3), (cx - 10, cy), (cx - 3, cy - 3)]
    d.polygon(pts, fill=PINK_L)
    px(d, cx - 1, cy - 5, (255, 255, 255))
    px(d, cx - 2, cy - 4, (255, 255, 255))
    px(d, cx + 2, cy + 2, PINK)
    return add_outline(img)


def build_mod_icon():
    """80x80 图标：深紫底 + 粉色星。"""
    img = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 2, 77, 77), radius=14, fill=(35, 26, 46))
    d.rounded_rectangle((6, 6, 73, 73), radius=11, fill=(58, 41, 72))
    import random
    rnd = random.Random(11)
    for _ in range(46):
        x, y = rnd.randint(11, 68), rnd.randint(11, 68)
        px(d, x, y, rnd.choice([(120, 96, 132), (160, 132, 170), (86, 66, 98)]))
    cx, cy, R = 40, 40, 22
    d.polygon([(cx, cy - R), (cx + 6, cy - 6), (cx + R, cy), (cx + 6, cy + 6),
               (cx, cy + R), (cx - 6, cy + 6), (cx - R, cy), (cx - 6, cy - 6)],
              fill=PINK_L)
    px(d, cx - 3, cy - 9, (255, 255, 255))
    px(d, cx - 4, cy - 8, (255, 255, 255))
    return img


def build_bolt():
    """16x16：纯白亮光弹（投影弹幕不需要描边）。"""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = 8
    for r, a in ((7, 40), (5, 95), (3, 175)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, a))
    d.line((cx, cy - 6, cx, cy + 6), fill=(255, 255, 255, 210))
    d.line((cx - 6, cy, cx + 6, cy), fill=(255, 255, 255, 210))
    d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(255, 255, 255, 255))
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    poses = build_poses()

    sheet = Image.new("RGBA", (W, H * FRAMES), (0, 0, 0, 0))
    frames = []
    for i, p in enumerate(poses):
        f = add_outline(draw_frame(p))
        frames.append(f)
        sheet.paste(f, (0, i * H))
    sheet.save(os.path.join(root, "Content", "NPCs", "Aurora.png"))

    crop = frames[0].crop((7, 1, 33, 31))
    icon = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    icon.paste(crop, (7, 6))
    icon.save(os.path.join(root, "Content", "NPCs", "Aurora_Head.png"))

    build_bolt().save(os.path.join(root, "Content", "Projectiles", "ArcaneBolt.png"))
    build_mod_icon().save(os.path.join(root, "icon.png"))

    prev = Image.new("RGBA", (W * 4 * 5 + 48, H * 4 * 5 + 48), (74, 96, 72, 255))
    for i, f in enumerate(frames):
        big = f.resize((W * 4, H * 4), Image.NEAREST)
        x = 8 + (i % 5) * (W * 4 + 8)
        y = 8 + (i // 5) * (H * 4 + 8)
        prev.paste(big, (x, y), big)
    prev.save(os.path.join(here, "preview_4x.png"))
    print("ok")


if __name__ == "__main__":
    main()
