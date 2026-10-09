#!/usr/bin/env python3
"""Render Claudia's performance to preview.gif for the README.

The GIF shows her stage only: the speech bubble and the PRRRT! are terminal
text, which a pixel GIF can't draw without a font. No dependencies.

  python3 scripts/make-preview.py
"""
import importlib.machinery
import importlib.util
import os
import struct
import sys

sys.dont_write_bytecode = True  # keep __pycache__ out of the repo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "preview.gif")
SCALE = 8
BACKGROUND = (30, 30, 36)
LAST_FRAME_SECONDS = 2.5
MAX_CODE_WIDTH = 12
MAX_SUB_BLOCK = 255


def load_claudia():
    loader = importlib.machinery.SourceFileLoader("claudia", os.path.join(ROOT, "claudia"))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader("claudia", loader))
    loader.exec_module(module)
    return module


def frames(claudia):
    """[pixel rows, seconds] per frame, with identical neighbours merged into one."""
    merged = []
    for step in claudia.timeline(len(claudia.LINE)):
        pixels = claudia.stage(step)
        if merged and merged[-1][0] == pixels:
            merged[-1][1] += step.seconds
        else:
            merged.append([pixels, step.seconds])
    merged[-1][1] = LAST_FRAME_SECONDS
    return merged


def color_table(claudia):
    """Background first, then Claudia's palette, padded to a power of two."""
    colors = [BACKGROUND] + list(claudia.PALETTE.values())
    size = 2
    while size < len(colors):
        size *= 2
    index_of = {claudia.TRANSPARENT: 0}
    index_of.update({char: i + 1 for i, char in enumerate(claudia.PALETTE)})
    return colors + [(0, 0, 0)] * (size - len(colors)), index_of


def scaled_indices(pixels, index_of):
    out = bytearray()
    for row in pixels:
        line = b"".join(bytes([index_of[pixel]]) * SCALE for pixel in row)
        out += line * SCALE
    return bytes(out)


def lzw(data, min_code_size):
    """GIF's LZW: codes grow a bit wider as the table fills, with a clear code when it is full."""
    clear = 1 << min_code_size
    out = bytearray()
    buffer = bit_count = 0
    table, next_code, width = {}, 0, 0

    def emit(code):
        nonlocal buffer, bit_count
        buffer |= code << bit_count
        bit_count += width
        while bit_count >= 8:
            out.append(buffer & 0xFF)
            buffer >>= 8
            bit_count -= 8

    def reset():
        nonlocal table, next_code, width
        table = {bytes([i]): i for i in range(clear)}
        next_code, width = clear + 2, min_code_size + 1

    reset()
    emit(clear)
    word = b""
    for value in data:
        candidate = word + bytes([value])
        if candidate in table:
            word = candidate
            continue
        emit(table[word])
        table[candidate] = next_code
        next_code += 1
        if next_code > (1 << width) and width < MAX_CODE_WIDTH:
            width += 1
        if next_code == 1 << MAX_CODE_WIDTH:
            emit(clear)
            reset()
        word = bytes([value])
    emit(table[word])
    emit(clear + 1)
    if bit_count:
        out.append(buffer & 0xFF)
    return bytes(out)


def sub_blocks(data):
    chunks = [data[i:i + MAX_SUB_BLOCK] for i in range(0, len(data), MAX_SUB_BLOCK)]
    return b"".join(bytes([len(chunk)]) + chunk for chunk in chunks) + b"\x00"


def gif(frame_list, colors, index_of):
    height, width = len(frame_list[0][0]) * SCALE, len(frame_list[0][0][0]) * SCALE
    table_bits = (len(colors) - 1).bit_length()
    min_code_size = max(2, table_bits)
    out = bytearray(b"GIF89a")
    out += struct.pack("<HHBBB", width, height, 0xF0 | (table_bits - 1), 0, 0)
    out += b"".join(bytes(color) for color in colors)
    out += b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00"  # loop forever
    for pixels, seconds in frame_list:
        delay = max(2, round(seconds * 100))
        out += b"\x21\xF9\x04\x04" + struct.pack("<H", delay) + b"\x00\x00"
        out += b"\x2C" + struct.pack("<HHHHB", 0, 0, width, height, 0)
        out += bytes([min_code_size]) + sub_blocks(lzw(scaled_indices(pixels, index_of), min_code_size))
    out += b"\x3B"
    return bytes(out)


def main():
    claudia = load_claudia()
    colors, index_of = color_table(claudia)
    frame_list = frames(claudia)
    with open(OUTPUT, "wb") as file:
        file.write(gif(frame_list, colors, index_of))
    print("wrote {} ({} frames)".format(os.path.relpath(OUTPUT), len(frame_list)))


if __name__ == "__main__":
    main()
