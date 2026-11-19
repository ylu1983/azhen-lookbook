#!/usr/bin/env python3
"""Regenerate intermediate WebPs; optional asset tooling requires Pillow.

The existing 1080px files are the best sources retained in this repository.
Never overwrite them or the existing 480px versions during this operation.
The normal static-site build does not require Pillow.
"""
from pathlib import Path

from PIL import Image


ASSETS = Path(__file__).resolve().parents[1] / 'docs/assets'


def main():
    for source in sorted(ASSETS.glob('outfit-*-large.webp')):
        with Image.open(source) as photo:
            photo.resize((640, 800), Image.Resampling.LANCZOS).save(
                source.with_name(source.name.replace('-large', '-medium')),
                'WEBP', quality=90, method=6,
            )


if __name__ == '__main__':
    main()
