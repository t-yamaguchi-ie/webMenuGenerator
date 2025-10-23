import os
import csv
import re

IMAGE_EXTS = (".jpg", ".jpeg", ".png")
FRAME_INDEX_RE = re.compile(r"(\d{2})$")
FIXED_LAYOUT_IDS = {1, 2, 3, 4, 6, 8, 9, 10, 12, 24}


def _read_frameinf(path: str):
    frames_by_section = {}
    layout_meta: dict[str, str] = {}
    if not os.path.isfile(path):
        return {}, layout_meta, []

    current = None
    with open(path, "r", encoding="shift_jis", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith(";"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1].strip()
                frames_by_section.setdefault(current, {})
                continue
            if current and "=" in line:
                key, value = line.split("=", 1)
                frames_by_section.setdefault(current, {})[key.strip()] = value.strip()

    frames_by_code = {}
    slots = []
    for section, data in frames_by_section.items():
        lower = section.lower()
        if lower == "layout":
            for key, value in data.items():
                layout_meta[key.lower()] = value
            continue
        if not lower.startswith("frame"):
            continue
        digits = "".join(ch for ch in section if ch.isdigit())
        try:
            frame_index = int(digits) if digits else 0
        except ValueError:
            frame_index = 0

        code_raw = data.get("itemcode", "").strip()
        if not code_raw:
            continue
        try:
            code = str(int(code_raw))
        except ValueError:
            code = code_raw
        if not code:
            continue

        entry = {
            "itemcode": code,
            "tanka": data.get("tanka"),
            "text1": data.get("text1str") or data.get("text1"),
            "show": data.get("show"),
            "frame_index": frame_index,
        }
        frames_by_code[code] = entry
        slots.append(entry)

    slots.sort(key=lambda e: e.get("frame_index") or 0)
    return frames_by_code, layout_meta, slots


def _scan_images(entry_dir: str, l_name: str, m_name: str, v_name: str):
    frame_images: dict[int, str] = {}
    other_images: list[str] = []

    try:
        names = sorted(os.listdir(entry_dir))
    except FileNotFoundError:
        return frame_images, other_images

    for fname in names:
        lower = fname.lower()
        if lower in {".ds_store", "thumbs.db"}:
            continue
        if not lower.endswith(IMAGE_EXTS):
            continue
        path = os.path.join(entry_dir, fname)
        if not os.path.isfile(path):
            continue

        rel = f"osusume_images/{l_name}/{m_name}/{v_name}/{fname}"
        stem = os.path.splitext(fname)[0]
        match = FRAME_INDEX_RE.search(stem)
        frame_idx = None
        if match:
            try:
                frame_idx = int(match.group(1))
            except ValueError:
                frame_idx = None

        if frame_idx:
            frame_images.setdefault(frame_idx, rel)
        else:
            other_images.append(rel)

    return frame_images, other_images


def _read_itemcells(path: str) -> dict:
    cells = {}
    if not os.path.isfile(path):
        return cells

    with open(path, "r", encoding="shift_jis", errors="ignore") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 7:
                continue
            try:
                x = int(row[4])
                y = int(row[5])
            except ValueError:
                continue
            code = row[-1].strip()
            if not code:
                continue
            try:
                code = str(int(code))
            except ValueError:
                code = code
            cells.setdefault(code, []).append((x, y))

    for coords in cells.values():
        coords.sort(key=lambda c: (c[1], c[0]))
    return cells


def read_osusume(root: str) -> dict:
    base = os.path.join(root, "smenu")
    entries = []

    if not os.path.isdir(base):
        return {"root": root, "entries": entries, "by_key": by_key}

    for l_name in sorted(os.listdir(base)):
        if not l_name.isdigit():
            continue
        l_idx = int(l_name)
        l_dir = os.path.join(base, l_name)
        if not os.path.isdir(l_dir):
            continue

        for m_name in sorted(os.listdir(l_dir)):
            if not m_name.isdigit():
                continue
            m_idx = int(m_name)
            m_dir = os.path.join(l_dir, m_name)
            if not os.path.isdir(m_dir):
                continue

            for v_name in sorted(os.listdir(m_dir)):
                if not v_name.isdigit():
                    continue
                v_idx = int(v_name)
                entry_dir = os.path.join(m_dir, v_name)
                if not os.path.isdir(entry_dir):
                    continue

                frame_path = os.path.join(entry_dir, "frameinf.ini")
                cells_path = os.path.join(entry_dir, "itemcell.csv")
                frames, layout_meta, slots = _read_frameinf(frame_path)
                cells = _read_itemcells(cells_path)
                frame_images, other_images = _scan_images(entry_dir, l_name, m_name, v_name)

                layout_id = layout_meta.get("layout") if layout_meta else None
                try:
                    layout_id = int(layout_id)
                except (TypeError, ValueError):
                    layout_id = None
                layout_show = layout_meta.get("show")

                entry_frame_images = frame_images if layout_id in FIXED_LAYOUT_IDS else {}
                background = ""
                if layout_id in FIXED_LAYOUT_IDS:
                    if other_images:
                        background = other_images[0]
                else:
                    if other_images:
                        background = other_images[0]
                    elif frame_images:
                        first_key = sorted(frame_images.keys())[0]
                        background = frame_images[first_key]
                    entry_frame_images = {}

                entry = {
                    "l_index": l_idx,
                    "m_index": m_idx,
                    "variant": v_idx,
                    "background": background,
                    "cells": cells,
                    "frames": frames,
                    "frame_slots": slots,
                    "layout": layout_id,
                    "layout_show": layout_show,
                    "frame_images": entry_frame_images,
                    "dir": entry_dir,
                }
                entries.append(entry)

    return {"root": root, "entries": entries}
