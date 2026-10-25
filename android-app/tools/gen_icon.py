#!/usr/bin/env python3
"""Generate the trial app launcher icon (no external deps: pure-Python PNG writer)."""
import os
import struct
import zlib

SS = 4  # supersampling factor


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def inside_circle(x, y, cx, cy, r):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def inside_triangle(x, y, p1, p2, p3):
    def sign(a, b, c):
        return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])

    d1, d2, d3 = sign((x, y), p1, p2), sign((x, y), p2, p3), sign((x, y), p3, p1)
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)


def inside_round_rect(x, y, x0, y0, x1, y1, r):
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def shade(x, y, size):
    """Return RGBA for a normalized coordinate in [0, size)."""
    u, v = x / size, y / size
    top, bottom = (0x18, 0x24, 0x46), (0x0A, 0x0F, 0x1E)
    color = lerp(top, bottom, min(max(v, 0.0), 1.0))
    alpha = 255

    # rounded-square mask
    if not inside_round_rect(u, v, 0.02, 0.02, 0.98, 0.98, 0.22):
        return (0, 0, 0, 0)

    # outer glow ring
    if inside_circle(u, v, 0.5, 0.5, 0.40) and not inside_circle(u, v, 0.5, 0.5, 0.365):
        t = 1.0 - abs(((u - 0.5) ** 2 + (v - 0.5) ** 2) ** 0.5 - 0.3825) / 0.02
        color = lerp(color, (0x4F, 0x8C, 0xFF), 0.35 + 0.55 * max(0.0, min(1.0, t)))

    # inner disc
    if inside_circle(u, v, 0.5, 0.5, 0.355):
        color = lerp(color, (0x11, 0x1A, 0x30), 0.85)

    # shield outline (chevron "V")
    bolt = [
        ((0.535, 0.245), (0.365, 0.545), (0.475, 0.545)),
        ((0.465, 0.765), (0.650, 0.445), (0.530, 0.445)),
    ]
    for tri in bolt:
        if inside_triangle(u, v, *tri):
            color = (0x35, 0xD0, 0xBA) if v < 0.52 else (0x4F, 0x8C, 0xFF)

    # core dot
    if inside_circle(u, v, 0.5, 0.5, 0.075):
        color = (0xEC, 0xF1, 0xFF)

    return (color[0], color[1], color[2], alpha)


def render(size):
    rows = []
    for y in range(size):
        row = bytearray()
        row.append(0)  # filter type
        for x in range(size):
            acc = [0, 0, 0, 0]
            for sy in range(SS):
                for sx in range(SS):
                    px = shade(x + (sx + 0.5) / SS, y + (sy + 0.5) / SS, size)
                    for i in range(4):
                        acc[i] += px[i]
            n = SS * SS
            row.extend(int(round(c / n)) for c in acc)
        rows.append(bytes(row))
    return b"".join(rows)


def write_png(path, size):
    raw = render(size)
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(png)


DENSITIES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "src", "main", "res")
    for folder, px in DENSITIES.items():
        write_png(os.path.join(root, folder, "ic_launcher.png"), px)
        print("wrote", folder, px)
    write_png(os.path.join(root, "mipmap-xxxhdpi", "ic_launcher_round.png"), 192)
