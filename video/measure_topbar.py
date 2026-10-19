#!/usr/bin/env python3
"""Measure the height of the Chrome for Testing infobar on a captured frame.

Reads a PNG, samples the mean color of horizontal strips from the top, and
returns the first row where the color is dark (the page), i.e. the height of
the browser infobar strip above the page content.
Usage: python3 video/measure_topbar.py frame.png [width]
Prints the bar height in pixels (0 if the top is already dark).
"""
import subprocess
import sys


def strip_rgb(png, w, y, h=2):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", png,
         "-vf", "crop=%d:%d:0:%d,scale=1:1" % (w, h, y), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True).stdout
    return tuple(out[:3]) if len(out) >= 3 else (255, 255, 255)


def main():
    png = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 1920
    bar = 0
    for y in range(0, 96, 2):
        r, g, b = strip_rgb(png, w, y)
        dark = r < 80 and g < 80 and b < 80
        if dark:
            bar = y
            break
    else:
        bar = 0
    print(bar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
