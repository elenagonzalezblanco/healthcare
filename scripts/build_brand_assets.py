"""Deriva la marca ELEVALOS de los PNG originales, sin reconstruir el dibujo."""
import argparse
from pathlib import Path

from PIL import Image


def transparent_wordmark(image: Image.Image) -> Image.Image:
    background = (254, 254, 251)
    foregrounds = ((31, 59, 49), (185, 151, 88))
    result = Image.new("RGBA", image.size)
    pixels = []
    for pixel in image.convert("RGB").getdata():
        # Recover edge coverage against the original cream matte, not a white cutoff.
        candidates = []
        for foreground in foregrounds:
            vector = tuple(bg - fg for bg, fg in zip(background, foreground))
            alpha = max(0, min(1, sum((bg - value) * delta for bg, value, delta
                                     in zip(background, pixel, vector))
                               / sum(delta * delta for delta in vector)))
            residual = sum((value - (bg - alpha * delta)) ** 2
                           for value, bg, delta in zip(pixel, background, vector))
            candidates.append((residual, alpha))
        _, alpha = min(candidates)
        if alpha < 0.045:
            pixels.append((0, 0, 0, 0))
        elif alpha > 0.96:
            pixels.append((*pixel, 255))
        else:
            color = tuple(round(max(0, min(255, (value - (1 - alpha) * bg) / alpha)))
                          for value, bg in zip(pixel, background))
            pixels.append((*color, round(alpha * 255)))
    result.putdata(pixels)
    return result


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
    wordmark = transparent_wordmark(wordmark)
    for width in (320, 640):
        resized = wordmark.resize((width, round(width * wordmark.height / wordmark.width)),
                                  Image.Resampling.LANCZOS)
        resized.save(output / f"elevalos-wordmark-{width}.png", optimize=True)
        resized.save(output / f"elevalos-wordmark-{width}.webp", lossless=True, method=6)
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
    canvas.paste(wordmark, ((1200 - wordmark.width) // 2, (630 - wordmark.height) // 2), wordmark)
    canvas.quantize(colors=128).save(output / "elevalos-social.png", optimize=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.source_dir, args.output_dir)
