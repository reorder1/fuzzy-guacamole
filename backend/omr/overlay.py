from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


def build_overlay(image_path: str, answers: Iterable[str]) -> Path:
    base = Image.open(image_path).convert('RGB')
    draw = ImageDraw.Draw(base, 'RGBA')
    width, height = base.size
    font = ImageFont.load_default()

    columns = 10
    rows = (len(list(answers)) + columns - 1) // columns or 1
    cell_w = width / columns
    cell_h = height / rows
    for idx, answer in enumerate(answers):
        row = idx // columns
        col = idx % columns
        x0 = col * cell_w
        y0 = row * cell_h
        draw.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], outline=(255, 0, 0, 128), width=2)
        draw.text((x0 + 5, y0 + 5), str(answer), fill=(0, 0, 0), font=font)

    overlay_path = Path(image_path).with_suffix('.overlay.png')
    base.save(overlay_path)
    return overlay_path
