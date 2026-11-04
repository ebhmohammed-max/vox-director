#!/usr/bin/env python3
"""Render the six approved-source-boundary collage plates as a short motion sample.

Motion is produced by the Vox Director repo's local Ken Burns fallback in
scripts/kenburns.py; captions, audio mux, and final encoding are local ffmpeg.
"""
from __future__ import annotations
import json
import os
import random
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CONFIG = HERE / "beats.json"
OUT = HERE / "atlas_understory_3d_collage_sample_v1.mp4"
BUILD = HERE / "_render"
W, H = 1920, 1080
FPS = 25

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path, size):
    if not Path(path).exists():
        raise FileNotFoundError(f"Required font not found: {path}")
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    lines, current = [], ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if not current or draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_caption(beat, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x, y, cw, ch = 68, 820, W - 136, 210
    # Slightly irregular paper edge, kept subtle so the type remains crisp.
    rng = random.Random(str(beat["id"]))
    top = [(x, y + rng.randint(0, 4))]
    for xx in range(x + 35, x + cw, 35):
        top.append((xx, y + rng.randint(-2, 4)))
    top.extend([(x + cw, y + 2), (x + cw, y + ch), (x, y + ch)])
    ImageDraw.Draw(shadow).polygon([(px + 6, py + 9) for px, py in top], fill=(0, 0, 0, 105))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(top, fill=(239, 230, 209, 247), outline=(64, 54, 43, 145), width=2)
    d.rectangle((x, y + 1, x + 11, y + ch - 1), fill=(157, 42, 36, 255))
    d.text((x + 38, y + 21), beat.get("kicker", "VOICEOVER / DRAFT").upper(),
           font=font(FONT_MONO, 17), fill=(132, 49, 37, 245))
    d.line((x + 38, y + 51, x + cw - 34, y + 51), fill=(67, 58, 47, 105), width=1)
    bodyf = font(FONT_REG, 34)
    lines = wrap(d, beat["narration"], bodyf, cw - 82)
    line_h = 42
    if len(lines) > 2:
        bodyf = font(FONT_REG, 30)
        lines = wrap(d, beat["narration"], bodyf, cw - 82)
        line_h = 37
    yy = y + 66
    for line in lines[:3]:
        d.text((x + 38, yy), line, font=bodyf, fill=(30, 34, 32, 255))
        yy += line_h
    d.text((x + 38, y + ch - 24),
           "AI-GENERATED ATMOSPHERE + EDITORIAL GRAPHICS  ·  NOT FIELD EVIDENCE",
           font=font(FONT_MONO, 12), fill=(82, 69, 55, 205))
    img.save(path)
    return path


def run():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required. Add it to PATH before rendering.")
    doc = json.loads(CONFIG.read_text(encoding="utf-8"))
    beats = doc["beats"]
    if len(beats) != 6:
        raise ValueError("This review cut expects exactly the six Batch 0 anchors.")
    audio = (HERE / doc["audio_path"]).resolve()
    if not audio.exists():
        raise FileNotFoundError(f"Narration not found: {audio}")
    BUILD.mkdir(parents=True, exist_ok=True)

    # Run the repository's local still-to-motion fallback on the supplied keyframes.
    subprocess.run(["python3", str(REPO / "scripts" / "kenburns.py"), str(HERE)], check=True)
    clip_paths = [HERE / "clips" / f"clip_{b['id']}.mp4" for b in beats]
    missing = [str(p) for p in clip_paths if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing Ken Burns clip(s): " + ", ".join(missing))

    concat_list = BUILD / "clips.txt"
    concat_list.write_text("".join(f"file '{p.resolve()}'\n" for p in clip_paths), encoding="utf-8")
    silent = BUILD / "base_silent.mp4"
    subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-an", "-c:v", "copy", str(silent)], check=True)

    total = sum(float(b.get("dur", 6.5533)) for b in beats)
    cap_paths = []
    for i, beat in enumerate(beats):
        cap_paths.append(make_caption(beat, BUILD / f"caption_{i:02d}.png"))

    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent), "-i", str(audio)]
    for path in cap_paths:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{total:.3f}", "-i", str(path)]

    chain = []
    previous = "[0:v]"
    cursor = 0.0
    for i, beat in enumerate(beats):
        duration = float(beat.get("dur", 6.5533))
        end = cursor + duration
        out = f"[v{i + 1}]"
        input_idx = i + 2
        chain.append(
            f"{previous}[{input_idx}:v]overlay=0:0:"
            f"enable='between(t,{cursor:.3f},{end:.3f})'{out}"
        )
        previous = out
        cursor = end
    fade_out = max(total - 0.85, 0)
    chain.append(
        f"{previous}fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out:.3f}:d=0.8,"
        "format=yuv420p[v]"
    )
    audio_fade = f"afade=t=in:st=0:d=0.3,afade=t=out:st={fade_out:.3f}:d=0.8"
    cmd += ["-filter_complex", ";".join(chain), "-map", "[v]", "-map", "1:a:0",
            "-af", audio_fade, "-t", f"{total:.3f}", "-shortest",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(OUT)]
    subprocess.run(cmd, check=True)
    print(f"Rendered: {OUT} ({OUT.stat().st_size:,} bytes; {total:.2f}s; {W}x{H}; {FPS} fps)")


if __name__ == "__main__":
    run()
