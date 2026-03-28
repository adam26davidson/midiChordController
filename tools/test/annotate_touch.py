#!/usr/bin/env python3
"""Overlay a touch gesture annotation onto a screenshot."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw


def annotate(
    input_path: Path,
    output_path: Path,
    from_x: int,
    from_y: int,
    to_x: int,
    to_y: int,
) -> None:
    img = Image.open(input_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    is_tap = from_x == to_x and from_y == to_y
    color = (255, 50, 50, 200)

    if is_tap:
        # Draw a crosshair + circle for tap
        r = 12
        draw.ellipse(
            [from_x - r, from_y - r, from_x + r, from_y + r],
            outline=color,
            width=3,
        )
        cross = 18
        draw.line([from_x - cross, from_y, from_x + cross, from_y], fill=color, width=2)
        draw.line([from_x, from_y - cross, from_x, from_y + cross], fill=color, width=2)
    else:
        # Draw line with arrow and start/end dots
        draw.line([from_x, from_y, to_x, to_y], fill=color, width=3)

        # Start dot (green)
        r = 6
        start_color = (50, 255, 50, 200)
        draw.ellipse(
            [from_x - r, from_y - r, from_x + r, from_y + r],
            fill=start_color,
            outline=start_color,
        )

        # End dot (red)
        draw.ellipse(
            [to_x - r, to_y - r, to_x + r, to_y + r],
            fill=color,
            outline=color,
        )

        # Arrowhead
        import math
        angle = math.atan2(to_y - from_y, to_x - from_x)
        arrow_len = 14
        arrow_angle = 0.5
        ax1 = to_x - arrow_len * math.cos(angle - arrow_angle)
        ay1 = to_y - arrow_len * math.sin(angle - arrow_angle)
        ax2 = to_x - arrow_len * math.cos(angle + arrow_angle)
        ay2 = to_y - arrow_len * math.sin(angle + arrow_angle)
        draw.polygon(
            [(to_x, to_y), (ax1, ay1), (ax2, ay2)],
            fill=color,
        )

    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path)


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: annotate_touch.py <input> <output> <from_x> <from_y> <to_x> <to_y>")
        sys.exit(1)

    annotate(
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
        int(sys.argv[5]),
        int(sys.argv[6]),
    )
