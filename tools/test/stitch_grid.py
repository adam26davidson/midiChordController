#!/usr/bin/env python3
"""Stitch multiple images into a grid with frame labels. No project dependencies required."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def stitch_grid(
    frame_paths: list[Path],
    output_path: Path,
    cols: int = 0,
) -> None:
    if not frame_paths:
        print("No frames to stitch", file=sys.stderr)
        sys.exit(1)

    frames = [Image.open(p) for p in frame_paths]
    n = len(frames)
    fw, fh = frames[0].size

    # Auto-calculate columns if not specified
    if cols <= 0:
        if n <= 4:
            cols = 2
        elif n <= 9:
            cols = 3
        else:
            cols = 4
    rows = (n + cols - 1) // cols

    label_height = 24
    cell_h = fh + label_height
    grid = Image.new("RGB", (cols * fw, rows * cell_h), (0, 0, 0))
    draw = ImageDraw.Draw(grid)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except OSError:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except OSError:
            font = ImageFont.load_default()

    for i, frame in enumerate(frames):
        row, col = divmod(i, cols)
        x = col * fw
        y = row * cell_h
        # Draw label
        label = f"Frame {i + 1}/{n}"
        draw.text((x + 4, y + 2), label, fill=(200, 200, 200), font=font)
        # Paste frame below label
        grid.paste(frame, (x, y + label_height))

    grid.save(output_path)
    print(f"Grid saved to {output_path} ({cols}x{rows}, {n} frames)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stitch frames into a grid")
    parser.add_argument("frame_dir", help="Directory containing frame_XX.png files")
    parser.add_argument("--output", "-o", default=None, help="Output path (default: <frame_dir>/grid.png)")
    parser.add_argument("--cols", type=int, default=0, help="Number of columns (default: auto)")
    args = parser.parse_args()

    frame_dir = Path(args.frame_dir)
    frame_paths = sorted(frame_dir.glob("frame_*.png"))
    output = Path(args.output) if args.output else frame_dir / "grid.png"

    stitch_grid(frame_paths, output, cols=args.cols)
