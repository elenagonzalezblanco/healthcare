"""Deriva la marca ELEVALOS de los PNG originales, sin reconstruir el dibujo."""
import argparse
from pathlib import Path

from PIL import Image


def build(source: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    wordmark = Image.open(source / "elevalos-wordmark-original.png").convert("RGB")
    mask = wordmark.point(lambda value: value)
    mask = Image.eval(mask.convert("L"), lambda value: 255 if value < 180 else 0)
    left, top, right, bottom = mask.getbbox()
    padding = 18
    wordmark = wordmark.crop((max(0, left - padding), max(0, top - padding),
                              min(wordmark.width, right + padding),
                              min(wordmark.height, bottom + padding)))
    for width in (320, 640):
        resized = wordmark.resize((width, round(width * wordmark.height / wordmark.width)),
                                  Image.Resampling.LANCZOS)
        resized.quantize(colors=128).save(output / f"elevalos-wordmark-{width}.png", optimize=True)
        resized.save(output / f"elevalos-wordmark-{width}.webp", quality=92, method=6)
    anagram = Image.open(source / "elevalos-anagram-original.png").convert("RGB")
    mask = Image.eval(anagram.convert("L"), lambda value: 255 if value > 110 else 0)
    left, top, right, bottom = mask.getbbox()
    side = min(anagram.width, max(right - left, bottom - top) + 100)
    center_x, center_y = (left + right) // 2, (top + bottom) // 2
    left = max(0, min(anagram.width - side, center_x - side // 2))
    top = max(0, min(anagram.height - side, center_y - side // 2))
    anagram = anagram.crop((left, top, left + side, top + side))
    for size in (16, 32, 48, 64, 180, 192, 512):
        resized = anagram.resize((size, size), Image.Resampling.LANCZOS)
        resized.quantize(colors=96).save(output / f"elevalos-icon-{size}.png", optimize=True)
    anagram.resize((256, 256), Image.Resampling.LANCZOS).save(
        output / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    canvas = Image.new("RGB", (1200, 630), (254, 254, 251))
    wordmark.thumbnail((960, 320), Image.Resampling.LANCZOS)
    canvas.paste(wordmark, ((1200 - wordmark.width) // 2, (630 - wordmark.height) // 2))
    canvas.quantize(colors=128).save(output / "elevalos-social.png", optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.source_dir, args.output_dir)
