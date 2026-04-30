#!/usr/bin/env python3
"""
HeroSmash v1.7 — Placeholder Sprite Generator
Genera PNG+JSON per i 16 hero senza sprite reali.
Formato: 8 colonne × 7 righe, 128×192 px per frame.

Uso:
  python3 tools/generate_placeholder_sprites.py [heroes_json] [output_dir]
"""
import json, sys, math, os
from PIL import Image, ImageDraw, ImageFilter

FRAME_W, FRAME_H = 128, 192
COLS, ROWS = 8, 7
SHEET_W = FRAME_W * COLS   # 1024
SHEET_H = FRAME_H * ROWS   # 1344

ANIM_DEFS = [
    ("idle",    0, 4,  7,  True),
    ("attack",  1, 4,  14, False),
    ("skill",   2, 6,  10, False),
    ("hit",     3, 2,  12, False),
    ("death",   4, 6,  8,  False),
    ("victory", 5, 4,  8,  True),
    ("intro",   6, 4,  10, False),
]

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lighten(rgb, factor=1.4):
    return tuple(min(255, int(c * factor)) for c in rgb)

def darken(rgb, factor=0.6):
    return tuple(max(0, int(c * factor)) for c in rgb)

def with_alpha(rgb, a):
    return rgb + (a,)

class Fighter:
    def __init__(self, color_hex, name):
        self.color = hex_to_rgb(color_hex)
        self.light = lighten(self.color, 1.5)
        self.dark  = darken(self.color, 0.5)
        self.name  = name
        r, g, b = self.color
        self.bulky = (r + g + b) < 380

    def draw_frame(self, draw, cx, cy, pose):
        head_r  = 18
        torso_h = 46
        torso_w = 30 if self.bulky else 24
        leg_h   = 38
        arm_len = 28
        arm_w   = 10 if self.bulky else 8

        lean    = pose.get('lean',  0)
        la      = pose.get('la',   -25)
        ra      = pose.get('ra',    25)
        ll      = pose.get('ll',   -10)
        rl      = pose.get('rl',    10)
        bob     = pose.get('bob',    0)
        glow    = pose.get('glow',   0)
        alpha   = int(pose.get('alpha', 255))
        squash  = pose.get('squash', 1.0)

        cy_adj    = cy + bob
        torso_top = cy_adj - leg_h - torso_h * squash
        lean_rad  = math.radians(lean)
        head_cx   = cx + math.sin(lean_rad) * torso_h * 0.6
        head_cy   = torso_top - head_r

        def pt(jx, jy, angle_deg, length):
            a = math.radians(angle_deg)
            return (jx + math.sin(a) * length, jy - math.cos(a) * length)

        # Shadow
        draw.ellipse([cx-24, cy_adj-6, cx+24, cy_adj+5], fill=(0,0,0,70))

        # Glow
        if glow > 0:
            ga = int(55 * glow)
            gs = int(18 * glow)
            draw.ellipse([head_cx-head_r-gs, head_cy-head_r-gs,
                          head_cx+head_r+gs, head_cy+head_r+gs], fill=with_alpha(self.light, ga))
            draw.ellipse([cx-torso_w-gs, torso_top-gs,
                          cx+torso_w+gs, cy_adj+gs], fill=with_alpha(self.light, ga//2))

        # Legs
        lh = (cx - torso_w//2 + 3, cy_adj - leg_h * squash)
        rh = (cx + torso_w//2 - 3, cy_adj - leg_h * squash)
        lf = pt(lh[0], lh[1], ll, leg_h * squash)
        rf = pt(rh[0], rh[1], rl, leg_h * squash)
        draw.line([lh, lf], fill=self.dark + (alpha,), width=11 if self.bulky else 9)
        draw.line([rh, rf], fill=self.dark + (alpha,), width=11 if self.bulky else 9)
        # Knee caps
        lk = pt(lh[0], lh[1], ll, leg_h * squash * 0.5)
        rk = pt(rh[0], rh[1], rl, leg_h * squash * 0.5)
        draw.ellipse([lk[0]-5,lk[1]-5,lk[0]+5,lk[1]+5], fill=self.color+(alpha,))
        draw.ellipse([rk[0]-5,rk[1]-5,rk[0]+5,rk[1]+5], fill=self.color+(alpha,))

        # Torso
        draw.rounded_rectangle(
            [cx-torso_w, torso_top, cx+torso_w, cy_adj-leg_h*squash],
            radius=7, fill=self.color+(alpha,)
        )
        # Belt line detail
        mid_y = (torso_top + cy_adj - leg_h*squash) / 2
        draw.line([(cx-torso_w, mid_y), (cx+torso_w, mid_y)], fill=self.dark+(alpha,), width=2)

        # Arms
        ls = (cx - torso_w + 5, torso_top + 10)
        rs = (cx + torso_w - 5, torso_top + 10)
        lh2 = pt(ls[0], ls[1], la, arm_len)
        rh2 = pt(rs[0], rs[1], ra, arm_len)
        draw.line([ls, lh2], fill=self.color+(alpha,), width=arm_w)
        draw.line([rs, rh2], fill=self.color+(alpha,), width=arm_w)
        draw.ellipse([lh2[0]-7,lh2[1]-7,lh2[0]+7,lh2[1]+7], fill=self.light+(alpha,))
        draw.ellipse([rh2[0]-7,rh2[1]-7,rh2[0]+7,rh2[1]+7], fill=self.light+(alpha,))

        # Head
        draw.ellipse([head_cx-head_r, head_cy-head_r,
                      head_cx+head_r, head_cy+head_r],
                     fill=self.light+(alpha,), outline=self.dark+(alpha,), width=2)
        ey = head_cy - 2
        draw.ellipse([head_cx-8,ey-3,head_cx-2,ey+3], fill=(15,8,25,alpha))
        draw.ellipse([head_cx+2, ey-3,head_cx+8, ey+3], fill=(15,8,25,alpha))


def get_poses(anim_name, fi, total):
    t = fi / max(1, total - 1)

    if anim_name == 'idle':
        bob = math.sin(fi * math.pi * 0.67) * 3
        return {'la': -22+bob, 'ra': 22-bob, 'bob': bob}

    elif anim_name == 'attack':
        if fi == 0: return {'lean':-10,'la':-80,'ra':-40,'ll':-15,'rl':5,'bob':2}
        if fi == 1: return {'lean':-15,'la':-105,'ra':-65,'bob':0}
        if fi == 2: return {'lean':22,'la':65,'ra':85,'ll':5,'rl':20,'bob':-5}
        return    {'lean':5,'la':10,'ra':38,'bob':0}

    elif anim_name == 'skill':
        if fi <= 1: return {'lean':-5,'la':-115,'ra':-108,'bob':-2,'glow':fi*0.45}
        if fi == 2: return {'lean':0,'la':-158,'ra':-148,'bob':-6,'glow':1.0}
        if fi == 3: return {'lean':28,'la':82,'ra':102,'bob':-8,'glow':0.85}
        if fi == 4: return {'lean':14,'la':48,'ra':68,'bob':-2,'glow':0.35}
        return         {'lean':0,'la':-20,'ra':20,'bob':0,'glow':0.12}

    elif anim_name == 'hit':
        if fi == 0: return {'lean':-28,'la':-55,'ra':-25,'ll':6,'rl':-6,'bob':7}
        return {'lean':-14,'la':-45,'ra':-16,'bob':2}

    elif anim_name == 'death':
        squash = max(0.28, 1.0 - t * 0.72)
        alpha  = max(55, int(255 * (1.0 - t * 0.78)))
        return {'lean':t*78,'la':-38+t*58,'ra':38-t*18,
                'll':30*t,'rl':-18*t,'bob':t*32,'squash':squash,'alpha':alpha}

    elif anim_name == 'victory':
        bob = math.sin(fi * math.pi * 0.67) * 5
        arm = -118 - math.sin(fi * math.pi * 0.67) * 14
        return {'la':arm,'ra':33+bob*0.4,'ll':-14,'rl':9,'bob':bob,'glow':0.25+0.18*math.sin(fi)}

    elif anim_name == 'intro':
        swing = math.sin(fi * math.pi * 0.67) * 22
        arm   = -swing * 0.5
        bob   = abs(math.sin(fi * math.pi * 0.67)) * 2
        return {'lean':5,'la':arm-14,'ra':-arm+14,'ll':swing-10,'rl':-swing+10,'bob':bob}

    return {}


def generate_sprite_sheet(hero_id, color_hex, out_dir):
    sheet = Image.new('RGBA', (SHEET_W, SHEET_H), (0,0,0,0))
    fighter = Fighter(color_hex, hero_id)

    for anim_name, row, frames, fps, loop in ANIM_DEFS:
        for fi in range(frames):
            ox = fi * FRAME_W
            oy = row * FRAME_H
            frame_img  = Image.new('RGBA', (FRAME_W, FRAME_H), (0,0,0,0))
            frame_draw = ImageDraw.Draw(frame_img)
            pose = get_poses(anim_name, fi, frames)
            fighter.draw_frame(frame_draw, FRAME_W//2, FRAME_H-12, pose)
            if pose.get('glow',0) > 0.5:
                blurred = frame_img.filter(ImageFilter.GaussianBlur(3))
                frame_img = Image.alpha_composite(blurred, frame_img)
            sheet.paste(frame_img, (ox, oy), frame_img)

    png_path = os.path.join(out_dir, f'{hero_id}.png')
    sheet.save(png_path, 'PNG')

    manifest = {
        "meta": {
            "hero":   hero_id,
            "image":  f"assets/sprites/{hero_id}.png",
            "frameW": FRAME_W,
            "frameH": FRAME_H,
            "sheetW": SHEET_W,
            "sheetH": SHEET_H,
            "source": "generated"
        },
        "animations": {}
    }
    for anim_name, row, frames, fps, loop in ANIM_DEFS:
        manifest["animations"][anim_name] = {"row":row,"frames":frames,"fps":fps,"loop":loop}

    json_path = os.path.join(out_dir, f'{hero_id}.json')
    with open(json_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return png_path, json_path


def main():
    heroes_json = sys.argv[1] if len(sys.argv)>1 else 'data/heroes.json'
    out_dir     = sys.argv[2] if len(sys.argv)>2 else 'assets/sprites'
    os.makedirs(out_dir, exist_ok=True)
    with open(heroes_json) as f:
        heroes = json.load(f)
    for h in heroes:
        png, jsn = generate_sprite_sheet(h['id'], h['color'], out_dir)
        print(f"  ✓  {h['id']:20s}  {h['color']}  →  {os.path.basename(png)}")
    print(f"\nGenerati {len(heroes)} sprite sheets in {out_dir}/")

if __name__ == '__main__':
    main()
