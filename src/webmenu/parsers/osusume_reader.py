import os
import csv


def _read_frameinf(path: str) -> dict:
    frames = {}
    if not os.path.isfile(path):
        return frames

    current = None
    with open(path, "r", encoding="shift_jis", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith(";"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1].strip()
                continue
            if current and current.lower().startswith("frame") and "=" in line:
                key, value = line.split("=", 1)
                frames.setdefault(current, {})[key.strip()] = value.strip()

    result = {}
    for data in frames.values():
        code = data.get("itemcode")
        if not code:
            continue
        try:
            code_str = str(int(code))
        except ValueError:
            code_str = code.strip()
        if not code_str:
            continue
        result[code_str] = {
            "itemcode": code_str,
            "tanka": data.get("tanka"),
            "text1": data.get("text1str"),
            "show": data.get("show"),
        }
    return result


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
                frames = _read_frameinf(frame_path)
                cells = _read_itemcells(cells_path)

                images = [fname for fname in os.listdir(entry_dir)
                          if fname.lower().endswith((".jpg", ".jpeg", ".png"))]
                background = images[0] if images else ""
                if background:
                    background = f"osusume_images/{l_name}/{m_name}/{v_name}/{background}"

                entry = {
                    "l_index": l_idx,
                    "m_index": m_idx,
                    "variant": v_idx,
                    "background": background,
                    "cells": cells,
                    "frames": frames,
                    "dir": entry_dir,
                }
                entries.append(entry)

    return {"root": root, "entries": entries}
