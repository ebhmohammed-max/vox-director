#!/usr/bin/env python3
"""Layered photo-stack animation using Vox Director's local motion Layer engine.

The generated editorial plates are cropped into separate photo cards, then moved as
independent layers. A red thread draws across the board while an animated steel/brass
map pin travels to each new card. Uses scripts/motion.py Layer for easing, rotation,
alpha, shadows, and compositing; ffmpeg handles encoding and audio mux.
"""
from __future__ import annotations
import json
import math
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = HERE.parents[2]
BUILD = HERE / "_stack_render"
CONFIG = HERE / "beats.json"
OUT = HERE / "atlas_understory_photo_stack_motion_sample_v2.mp4"
POSTER = HERE / "poster_photo_stack_v2.jpg"
W, H, FPS = 1920, 1080, 24
DURATION = 39.32
CARD_W, CARD_H = 900, 555
PAPER = (232, 222, 201)
RED = (147, 36, 31)
INK = (37, 40, 38)

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# Central 16:9 crops isolate each generated 3D image plate from its editorial frame.
CROPS = {
    "A01": (235, 45, 1455, 730),
    "A02": (220, 65, 1420, 740),
    "A03": (190, 95, 1390, 770),
    "A04": (330, 65, 1530, 740),
    "A05": (220, 105, 1420, 780),
    "A06": (160, 75, 1420, 785),
}


def f(path, size):
    if not Path(path).exists():
        raise FileNotFoundError(f"Font unavailable: {path}")
    return ImageFont.truetype(path, size)


def ragged_mask(w, h, seed, rough=10):
    rng = random.Random(seed)
    pts = []
    for x in range(0, w, 24): pts.append((x, max(0, rng.randint(-rough, rough))))
    for y in range(0, h, 24): pts.append((min(w, w + rng.randint(-rough, rough)), y))
    for x in range(w, 0, -24): pts.append((x, min(h, h + rng.randint(-rough, rough))))
    for y in range(h, 0, -24): pts.append((max(0, rng.randint(-rough, rough)), y))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    return mask


def create_card(beat, out_path):
    image_path = Path(beat["keyframe_path"])
    if not image_path.is_absolute():
        image_path = REPO / image_path
    src = Image.open(image_path).convert("RGB")
    crop = src.crop(CROPS[beat["id"]])
    photo_w, photo_h = CARD_W - 36, 472
    crop = ImageOps.fit(crop, (photo_w, photo_h), method=Image.Resampling.LANCZOS)
    crop = ImageEnhance.Contrast(crop).enhance(1.04)
    crop = ImageEnhance.Color(crop).enhance(0.96)

    card = Image.new("RGBA", (CARD_W, CARD_H), (239, 230, 208, 255))
    card.alpha_composite(crop.convert("RGBA"), (18, 16))
    d = ImageDraw.Draw(card, "RGBA")
    d.line((20, 503, CARD_W - 20, 503), fill=(75, 65, 51, 110), width=1)
    d.text((22, 516), f"{beat['id']}   /   {beat['title_en']}",
           font=f(FONT_MONO, 16), fill=(61, 56, 48, 240))
    d.text((CARD_W - 22, 519), "ILLUSTRATIVE PLATE", font=f(FONT_MONO, 10),
           fill=(93, 76, 57, 185), anchor="ra")
    card.putalpha(ragged_mask(CARD_W, CARD_H, int(beat["id"][1:]) * 13, rough=8))
    card.save(out_path)
    return out_path


# Pillow helper import is kept local to the repo's motion engine for animation.
sys.path.insert(0, str(REPO / "scripts"))
from motion import Layer, ease  # noqa: E402


def build_board():
    base = Image.new("RGB", (W, H), PAPER)
    noise = Image.effect_noise((W, H), 17).convert("L")
    tint = Image.new("RGB", (W, H), (247, 239, 216))
    base = Image.blend(base, ImageChops.multiply(tint, Image.merge("RGB", (noise, noise, noise))), .04)
    canvas = base.convert("RGBA")
    d = ImageDraw.Draw(canvas, "RGBA")
    # Restrained editorial map-board: decorative and explicitly non-site-specific.
    for x in range(120, W, 180): d.line((x, 105, x, 905), fill=(73, 77, 69, 20), width=1)
    for y in range(120, 920, 120): d.line((80, y, W - 80, y), fill=(73, 77, 69, 17), width=1)
    coast = [(70, 410), (155, 385), (235, 398), (325, 370), (415, 392), (510, 425),
             (602, 416), (700, 390), (790, 402), (885, 430), (980, 418), (1080, 390),
             (1185, 397), (1285, 420), (1385, 404), (1485, 382), (1590, 391), (1700, 365), (1845, 378)]
    d.line(coast, fill=(77, 91, 80, 53), width=3, joint="curve")
    for j in range(4):
        pts = [(x, y + 45 + j * 11 + int(5 * math.sin(x / 145 + j))) for x, y in coast[2:-2:2]]
        d.line(pts, fill=(77, 91, 80, 19), width=2)
    d.rectangle((42, 38, W - 42, H - 36), outline=(53, 51, 44, 70), width=2)
    d.text((76, 54), "ATLAS UNDERSTORY   /   ALEXANDRIA", font=f(FONT_MONO, 18), fill=(43, 46, 42, 235))
    d.text((W - 76, 58), "PHOTO FILE 01   ·   DRAFT", font=f(FONT_MONO, 14), fill=(99, 64, 45, 220), anchor="ra")
    d.text((W - 76, H - 62), "SCHEMATIC BACKGROUND  ·  NOT A SITE PLAN", font=f(FONT_MONO, 13), fill=(84, 73, 57, 160), anchor="ra")
    d.line((75, 89, W - 75, 89), fill=(64, 59, 48, 60), width=1)
    return canvas


def card_tracks(beats):
    finals = [(520, 356), (955, 370), (1390, 350), (600, 700), (1030, 710), (1450, 685)]
    rotations = [-4.5, 2.5, -2.0, 3.5, -3.0, 2.0]
    tracks = []
    seg = DURATION / len(beats)
    for i, beat in enumerate(beats):
        start = i * seg + .18
        park = min(start + 5.55, DURATION - .12)
        fx, fy = finals[i]
        if i % 3 == 0: off = (-650, 440)
        elif i % 3 == 1: off = (W + 650, 420)
        else: off = (fx, -650)
        center = (960 + (-35 if i % 2 else 35), 465 + (30 if i % 2 else -10))
        r0 = (-10 if i % 2 == 0 else 9)
        keys = [
            dict(t=start, x=off[0], y=off[1], s=.55, r=r0, a=0, e="out"),
            dict(t=start + .18, x=off[0], y=off[1], s=.65, r=r0, a=.9, e="out"),
            dict(t=start + 1.15, x=center[0], y=center[1], s=.82, r=rotations[i] * 1.8, a=1, e="back"),
            dict(t=max(start + 4.25, park - 1.0), x=center[0], y=center[1], s=.82, r=rotations[i], a=1, e="smooth"),
            dict(t=park, x=fx, y=fy, s=.53, r=rotations[i], a=1, e="back"),
            dict(t=DURATION + .5, x=fx, y=fy, s=.53, r=rotations[i], a=1, e="smooth"),
        ]
        tracks.append((Layer(beat["card_path"], keys, sway=.20, pulse=.0015, shadow=True), (fx, fy), .53, rotations[i], park))
    return tracks


def pin_target(track):
    layer, (cx, cy), scale, rot, _ = track
    # Pin the upper-right paper corner, offset slightly to keep the headline footer clear.
    return (cx + CARD_W * scale * .40, cy - CARD_H * scale * .42)


def curved_segment(a, b, bow=25, n=36):
    ax, ay = a; bx, by = b
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax, by - ay
    length = max(1, math.hypot(dx, dy))
    cx, cy = mx - dy / length * bow, my + dx / length * bow
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u*u*ax + 2*u*t*cx + t*t*bx, u*u*ay + 2*u*t*cy + t*t*by))
    return out


def thread_points(points, active_index, active_progress):
    sampled = []
    for i in range(active_index):
        seg = curved_segment(points[i], points[i + 1], bow=24 if i % 2 == 0 else -20)
        sampled.extend(seg if not sampled else seg[1:])
    if active_index < len(points) - 1:
        seg = curved_segment(points[active_index], points[active_index + 1], bow=24 if active_index % 2 == 0 else -20)
        take = max(2, int(len(seg) * max(0, min(1, active_progress))))
        sampled.extend(seg[:take] if not sampled else seg[1:take])
    return sampled


def draw_thread(canvas, pts, color=(132, 33, 29, 240), width=6):
    if len(pts) < 2: return
    d = ImageDraw.Draw(canvas, "RGBA")
    coords = [(int(x), int(y)) for x, y in pts]
    d.line([(x + 2, y + 4) for x, y in coords], fill=(24, 20, 17, 80), width=width + 3, joint="curve")
    d.line(coords, fill=color, width=width, joint="curve")
    d.line([(x, y - 1) for x, y in coords], fill=(216, 117, 91, 175), width=2, joint="curve")


def draw_pin(canvas, x, y, moving=False, angle=-8, scale=1.0):
    # A real-looking editorial map pin: metal needle, raised enamel head, and tiny cast shadow.
    sw, sh = int(74 * scale), int(132 * scale)
    pin = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(pin, "RGBA")
    d.ellipse((int(sw*.33), int(sh*.73), int(sw*.70), int(sh*.90)), fill=(15, 16, 15, 90))
    d.polygon([(int(sw*.46), int(sh*.48)), (int(sw*.56), int(sh*.48)),
               (int(sw*.53), int(sh*.91)), (int(sw*.50), int(sh*.99)), (int(sw*.45), int(sh*.91))],
              fill=(177, 180, 171, 255), outline=(66, 67, 62, 230))
    d.line((int(sw*.49), int(sh*.53), int(sw*.48), int(sh*.94)), fill=(247, 245, 224, 235), width=max(1, int(2*scale)))
    r = int(sw*.31); cx, cy = sw//2, int(sh*.40)
    d.ellipse((cx-r+3, cy-r+6, cx+r+6, cy+r+8), fill=(25, 18, 16, 85))
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(150, 41, 33, 255), outline=(70, 33, 28, 255), width=max(1, int(3*scale)))
    d.ellipse((cx-int(r*.68), cy-int(r*.76), cx+int(r*.36), cy+int(r*.10)), fill=(205, 70, 54, 255))
    d.ellipse((cx-int(r*.46), cy-int(r*.58), cx-int(r*.05), cy-int(r*.17)), fill=(247, 155, 117, 235))
    if moving:
        # A tiny glint flashes on the moving metal needle during the pinning action.
        d.line((int(sw*.48), int(sh*.65), int(sw*.48), int(sh*.84)), fill=(255, 255, 235, 220), width=max(1, int(2*scale)))
    pin = pin.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    canvas.alpha_composite(pin, (int(x - pin.width/2), int(y - pin.height/2)))


def draw_caption(canvas, beat, t):
    x, y, w, h = 66, 894, W - 132, 133
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle((x+5, y+7, x+w+5, y+h+7), fill=(20, 18, 14, 95))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    layer = Image.alpha_composite(layer, shadow)
    d = ImageDraw.Draw(layer, "RGBA")
    d.rectangle((x, y, x+w, y+h), fill=(239, 230, 209, 244), outline=(57, 49, 40, 130), width=2)
    d.rectangle((x, y, x+10, y+h), fill=(153, 38, 32, 255))
    d.text((x+30, y+12), beat.get("kicker", "VOICEOVER / DRAFT").upper(),
           font=f(FONT_MONO, 14), fill=(132, 46, 36, 235))
    d.line((x+30, y+37, x+w-26, y+37), fill=(70, 62, 50, 90), width=1)
    body = f(FONT_SERIF, 28)
    text = beat["narration"]
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if not current or d.textbbox((0,0), trial, font=body)[2] <= w-70:
            current = trial
        else:
            lines.append(current); current = word
    if current: lines.append(current)
    if len(lines) > 2: body = f(FONT_SERIF, 25)
    yy = y + 48
    for line in lines[:2]:
        d.text((x+30, yy), line, font=body, fill=(31, 34, 32, 250)); yy += 33
    canvas.alpha_composite(layer)


def pin_state(t, targets, seg):
    idx = min(len(targets)-1, int(t / seg))
    start = idx * seg + 1.35
    end = min((idx + 1) * seg - .25, start + 3.3)
    prev = (210, 825) if idx == 0 else targets[idx - 1]
    dest = targets[idx]
    p = max(0, min(1, (t - start) / max(.01, end - start)))
    q = ease("smooth", p)
    return idx, q, (prev[0] + (dest[0]-prev[0])*q, prev[1] + (dest[1]-prev[1])*q)


def draw_frame(t, beats, tracks, board, pin_targets):
    canvas = board.copy()
    seg = DURATION / len(beats)
    # Cards arrive one-by-one, occupy the hero area, then slide into a growing photo stack.
    for layer, _, _, _, _ in tracks:
        layer.draw(canvas, t)

    idx, progress, moving_pos = pin_state(t, pin_targets, seg)
    pts = [(210, 825)] + pin_targets
    # Thread is drawn only as far as the moving needle; prior legs remain pinned.
    thread_idx = idx
    if t >= (idx + 1) * seg - .25 and idx < len(beats)-1:
        thread_idx = idx + 1; progress = 0
    route = thread_points(pts, thread_idx, progress)
    if route: draw_thread(canvas, route)

    # Stationary pin heads appear as each card is placed; the red needle moves to the next.
    for j in range(idx):
        if t >= (j + 1) * seg - .2:
            draw_pin(canvas, *pin_targets[j], moving=False, angle=-8 + (j % 3) * 5, scale=.58)
    draw_pin(canvas, *moving_pos, moving=True, angle=-8 + math.sin(t*2)*2.2, scale=.80)

    current = min(len(beats)-1, int(t / seg))
    draw_caption(canvas, beats[current], t)

    # Restrained camera push applied after the paper stack settles; all layers still move independently.
    z = 1.0 + .018 * ease("smooth", t / DURATION)
    if z > 1.001:
        cw, ch = W / z, H / z
        x0, y0 = (W-cw)/2, (H-ch)/2
        canvas = canvas.crop((int(x0), int(y0), int(x0+cw), int(y0+ch))).resize((W, H), Image.Resampling.LANCZOS)
    return canvas.convert("RGB")


def run():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg must be available on PATH")
    doc = json.loads(CONFIG.read_text(encoding="utf-8"))
    beats = doc["beats"]
    if len(beats) != 6:
        raise ValueError("Photo-stack sample expects exactly six anchor beats")
    BUILD.mkdir(parents=True, exist_ok=True)

    for beat in beats:
        beat["card_path"] = str(create_card(beat, BUILD / f"card_{beat['id']}.png"))
    tracks = card_tracks(beats)
    pin_targets = [pin_target(track) for track in tracks]
    board = build_board()

    silent = BUILD / "photo_stack_silent.mp4"
    proc = subprocess.Popen(
        [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    nframes = math.ceil(DURATION * FPS)
    for frame_no in range(nframes):
        t = frame_no / FPS
        frame = draw_frame(t, beats, tracks, board, pin_targets)
        proc.stdin.write(frame.tobytes())
        if frame_no % 240 == 0: print(f"rendered {frame_no}/{nframes}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg video encode failed")

    audio = (HERE / doc["audio_path"]).resolve()
    if not audio.exists(): raise FileNotFoundError(audio)
    fade_out = max(0, DURATION - .85)
    subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent), "-i", str(audio),
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-af", f"afade=t=in:st=0:d=0.3,afade=t=out:st={fade_out:.3f}:d=0.8",
                    "-shortest", "-movflags", "+faststart", str(OUT)], check=True)
    silent.unlink(missing_ok=True)
    subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", "3.0", "-i", str(OUT),
                    "-frames:v", "1", "-q:v", "2", str(POSTER)], check=True)
    print(f"Rendered {OUT} ({OUT.stat().st_size:,} bytes; {DURATION:.2f}s; {W}x{H}; {FPS}fps)")


if __name__ == "__main__": run()
