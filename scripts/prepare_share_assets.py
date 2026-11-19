#!/usr/bin/env python3
"""Optional media preparation; normal builds use the committed output.

Requires Pillow and --font pointing to a Traditional Chinese font file.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / 'docs/assets'


def prepare(font_path):
    logo = Image.open(ASSETS / 'shop-logo-badge.png').convert('RGBA')
    logo.thumbnail((520, 180), Image.Resampling.LANCZOS)
    for number in range(1, 28):
        preview = Image.new('RGB', (1200, 630), '#f7f4ed')
        preview.paste(logo, (64, (630 - logo.height) // 2), logo)
        photo = Image.open(ASSETS / f'outfit-{number:02d}-large.webp').convert('RGB')
        photo.thumbnail((504, 630), Image.Resampling.LANCZOS)
        preview.paste(photo, (648 + (504 - photo.width) // 2, (630 - photo.height) // 2))
        preview.save(ASSETS / f'share-{number:02d}.jpg', quality=88, optimize=True)

    icon = Image.new('RGB', (256, 256), '#6d6648')
    draw = ImageDraw.Draw(icon)
    draw.text((128, 128), '蓁', font=ImageFont.truetype(font_path, 182), fill='white', anchor='mm')
    icon.resize((32, 32), Image.Resampling.LANCZOS).save(ASSETS / 'favicon-32.png')
    icon.resize((180, 180), Image.Resampling.LANCZOS).save(ASSETS / 'apple-touch-icon.png')
    icon.save(ASSETS / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', required=True)
    prepare(parser.parse_args().font)
