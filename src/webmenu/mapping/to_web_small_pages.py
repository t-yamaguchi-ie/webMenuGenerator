from ..core.ids import page_relpath, small_id
from ..parsers import menudb_reader as mreader
from typing import List, Dict, Tuple

ABS_COLS = 40
ABS_ROWS = 20

_FIXED_LAYOUT_PRESETS: Dict[int, Tuple[int, int]] = {
    1: (1, 1),
    2: (2, 1),
    3: (3, 1),
    4: (2, 2),
    6: (3, 2),
    8: (4, 2),
    9: (3, 3),
    10: (5, 2),
    12: (4, 3),
    24: (6, 4),
}


def _split_dimension(total: int, parts: int) -> List[int]:
    if parts <= 0:
        return []
    base = total // parts
    remainder = total - base * parts
    spans = [base] * parts
    idx = 0
    while remainder > 0 and idx < len(spans):
        spans[idx] += 1
        remainder -= 1
        idx += 1
    return spans


def _expand_cells(cell: List[int], span: List[int]) -> List[Tuple[int, int]]:
    x0, y0 = cell
    width, height = span
    coords = []
    for dy in range(height):
        for dx in range(width):
            coords.append((x0 + dx, y0 + dy))
    return coords


def _is_visible_flag(value) -> bool:
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return True
        try:
            return int(stripped) != 0
        except ValueError:
            return stripped.lower() in {"true", "on", "yes"}
    return True


def _build_fixed_layout(entry: Dict, info_by_code: Dict[str, Dict]) -> Tuple[List[Dict], Dict]:
    layout_id = entry.get("layout")
    if layout_id not in _FIXED_LAYOUT_PRESETS:
        return [], {}

    cols, rows = _FIXED_LAYOUT_PRESETS[layout_id]
    total_positions = cols * rows
    col_spans = _split_dimension(ABS_COLS, cols)
    row_spans = _split_dimension(ABS_ROWS, rows)

    plan = []
    y = 1
    for r in range(rows):
        x = 1
        span_y = row_spans[r]
        for c in range(cols):
            span_x = col_spans[c]
            plan.append({
                "cell": [x, y],
                "span": [span_x, span_y],
            })
            x += span_x
        y += span_y

    frames_meta = entry.get("frames") or {}
    frame_images = entry.get("frame_images") or {}
    multi_lang_images = entry.get("multi_lang_images") or {}
    slots = entry.get("frame_slots") or []

    items: List[Dict] = []
    cells_map: Dict[str, List[Tuple[int, int]]] = {}
    for idx, slot in enumerate(slots):
        if idx >= len(plan) or len(items) >= total_positions:
            break
        pos = plan[idx]
        code = str(slot.get("itemcode") or "").strip()
        if not code:
            continue
        if not _is_visible_flag(slot.get("show")):
            continue
        frame_idx = slot.get("frame_index")
        product_info = info_by_code.get(code) or {}
        product_detail = dict(product_info) if isinstance(product_info, dict) else {"code": code}
        osusume_meta = frames_meta.get(code, {})

        cell = pos["cell"][:]
        span = pos["span"][:]
        coords = _expand_cells(cell, span)
        image_path = frame_images.get(frame_idx, "") if frame_idx else ""
        multi_lang_image_paths = {
            lang: imgs.get(frame_idx, "")
            for lang, imgs in multi_lang_images.items()
        }

        item = {
            "product_code": code,
            "cell": cell,
            "span": span,
            "process": 0,
            "image": image_path,
            "multi_lang_images": multi_lang_image_paths,
            "product_detail": product_detail,
            "cells_path": "",
            "osusume": osusume_meta,
        }
        items.append(item)
        cells_map[code] = coords

    return items, cells_map


def _build_iteminfo_map(menudb: Dict):
    meta = menudb.get("meta", {})
    base = meta.get("base")
    stride = meta.get("stride", mreader.ITEM_INFORMATION_SIZE)
    infos = menudb.get("item_infos", [])
    if base is None:
        return {}, 0, 0
    mapping = {}
    for info in infos:
        idx = info.get("index", 0)
        addr = base + stride * idx
        mapping[addr] = info
    return mapping, base, stride


def make_small_pages(menudb, osusume, ini_bundle, schema_version="0.1"):
    item_cells = menudb.get("item_cells", [])
    item_infos = menudb.get("item_infos", [])
    mmenus = menudb.get("mmenus", [])
    smenus = menudb.get("smenus", [])

    info_by_addr, info_base, stride = _build_iteminfo_map(menudb)
    counts = menudb.get("meta", {}).get("counts", {})
    info_by_code = {str(info.get("code")): info for info in item_infos}

    item_frame_size = mreader.ITEM_FRAME_INFORMATION_SIZE * counts.get("ItemFrmNum", 0)
    item_cell_size = mreader.ITEM_CELL_INFORMATION_SIZE * counts.get("ItemCellNum", 0)
    item_cell_base = info_base - item_frame_size - item_cell_size

    smenu_offset_index = {sm.get("offset"): idx for idx, sm in enumerate(smenus)}
    osusume_entries = []
    if isinstance(osusume, dict):
        osusume_entries = osusume.get("entries", []) or []
    osusume_map = {
        (entry.get("l_index"), entry.get("m_index"), entry.get("variant")): entry
        for entry in osusume_entries
    }

    pages = {}
    cell_files = {}

    def attach_cells(sid: str, mapping: Dict, items: List):
        if not mapping:
            for item in items:
                item["cells_path"] = ""
            return
        rel = f"small/{sid}/cells.json"
        cell_files[rel] = {"cells": mapping}
        for item in items:
            item["cells_path"] = rel

    for mm in mmenus:
        sm_addr = mm.get("sMenuAddr")
        start_idx = smenu_offset_index.get(sm_addr)
        if start_idx is None:
            continue
        sm_count = max(1, mm.get("sMenuNum", 0))

        for seq in range(sm_count):
            sm_idx = start_idx + seq
            if sm_idx >= len(smenus):
                break
            sm = smenus[sm_idx]
            show_type = sm.get("showType", 0)
            sid = small_id(mm.get("l_index", 0), mm.get("index", 0), sm.get("index", 0))

            grid_items = []
            cells_map = {}
            layout_type = "free"
            background_override = ""
            layout_mode_value = None
            layout_flag_value = None

            if show_type == 6:
                entry = osusume_map.get((mm.get("l_index", 0), mm.get("index", 0), seq + 1))
                if entry is None:
                    entry = osusume_map.get((mm.get("l_index", 0), mm.get("index", 0), 1))
                if not entry:
                    continue

                frames_meta = entry.get("frames") or {}
                frame_slots = entry.get("frame_slots") or []
                entry_cells = entry.get("cells") or {}
                frame_images = entry.get("frame_images") or {}
                multi_lang_images = entry.get("multi_lang_images") or {}
                layout_type = "recommended"
                background_override = entry.get("background", "") or ""
                layout_mode_value = entry.get("layout")
                layout_flag_value = entry.get("layout_show")
                is_fixed_layout = layout_mode_value in _FIXED_LAYOUT_PRESETS if layout_mode_value else False

                frame_index_by_code = {}
                for slot in frame_slots:
                    code_key = str(slot.get("itemcode") or "").strip()
                    if not code_key:
                        continue
                    frame_index = slot.get("frame_index")
                    if frame_index:
                        frame_index_by_code[code_key] = frame_index

                if entry_cells:
                    added_codes = set()

                    for slot in frame_slots:
                        code = str(slot.get("itemcode") or "").strip()
                        if not code or code in added_codes:
                            continue
                        coords = entry_cells.get(code) or []
                        if not coords:
                            continue
                        coords = sorted(coords, key=lambda c: (c[1], c[0]))
                        xs = [c[0] for c in coords]
                        ys = [c[1] for c in coords]
                        min_x = min(xs)
                        min_y = min(ys)
                        span_x = max(1, max(xs) - min_x + 1)
                        span_y = max(1, max(ys) - min_y + 1)
                        frame_idx = slot.get("frame_index")
                        image_path = frame_images.get(frame_idx, "") if frame_idx else ""
                        multi_lang_image_paths = {
                            lang: imgs.get(frame_idx, "")
                            for lang, imgs in multi_lang_images.items()
                        }
                        product_info = info_by_code.get(code)
                        product_detail = dict(product_info) if isinstance(product_info, dict) else {"code": code}
                        osusume_meta = frames_meta.get(code, {})
                        grid_items.append({
                            "product_code": code,
                            "cell": [min_x, min_y],
                            "span": [span_x, span_y],
                            "process": 0,
                            "image": image_path,
                            "multi_lang_images": multi_lang_image_paths,
                            "product_detail": product_detail,
                            "cells_path": "",
                            "osusume": osusume_meta,
                        })
                        if not is_fixed_layout:
                            cells_map[code] = coords
                        added_codes.add(code)

                    for code, coords in entry_cells.items():
                        if code in added_codes or not coords:
                            continue
                        coords = sorted(coords, key=lambda c: (c[1], c[0]))
                        xs = [c[0] for c in coords]
                        ys = [c[1] for c in coords]
                        min_x = min(xs)
                        min_y = min(ys)
                        span_x = max(1, max(xs) - min_x + 1)
                        span_y = max(1, max(ys) - min_y + 1)
                        frame_idx = frame_index_by_code.get(code)
                        image_path = frame_images.get(frame_idx, "") if frame_idx else ""
                        multi_lang_image_paths = {
                            lang: imgs.get(frame_idx, "")
                            for lang, imgs in multi_lang_images.items()
                        }
                        product_info = info_by_code.get(code)
                        product_detail = dict(product_info) if isinstance(product_info, dict) else {"code": code}
                        osusume_meta = frames_meta.get(code, {})
                        grid_items.append({
                            "product_code": code,
                            "cell": [min_x, min_y],
                            "span": [span_x, span_y],
                            "process": 0,
                            "image": image_path,
                            "multi_lang_images": multi_lang_image_paths,
                            "product_detail": product_detail,
                            "cells_path": "",
                            "osusume": osusume_meta,
                        })
                        if not is_fixed_layout:
                            cells_map[code] = coords
                else:
                    fixed_items, fixed_cells = _build_fixed_layout(entry, info_by_code)
                    grid_items.extend(fixed_items)
                    if layout_mode_value not in _FIXED_LAYOUT_PRESETS:
                        cells_map.update(fixed_cells)
            else:
                item_addr = sm.get("itemAddr", 0)
                item_count = sm.get("itemNum", 0)
                if not item_addr or not item_count:
                    continue
                if item_addr < item_cell_base:
                    continue

                start = (item_addr - item_cell_base) // mreader.ITEM_CELL_INFORMATION_SIZE
                end = start + item_count
                slice_cells = item_cells[start:end] if 0 <= start < len(item_cells) else []
                if not slice_cells:
                    continue

                aggregates = {}
                for cell in slice_cells:
                    addr = cell.get("itemInfoAddr", 0)
                    if not addr:
                        continue
                    info = info_by_addr.get(addr)
                    if not info and info_base and stride:
                        rel = addr - info_base
                        if rel >= 0 and rel % stride == 0:
                            idx = rel // stride
                            if 0 <= idx < len(item_infos):
                                info = item_infos[idx]
                                info_by_addr[addr] = info
                    if not info:
                        continue
                    code = str(info.get("code"))
                    agg = aggregates.setdefault(code, {
                        "product_code": code,
                        "minX": cell.get("cellX", 0),
                        "maxX": cell.get("cellX", 0),
                        "minY": cell.get("cellY", 0),
                        "maxY": cell.get("cellY", 0),
                        "process": cell.get("process", 0),
                        "info": info,
                        "cells": set(),
                    })
                    x = cell.get("cellX", 0)
                    y = cell.get("cellY", 0)
                    agg["minX"] = min(agg["minX"], x)
                    agg["maxX"] = max(agg["maxX"], x)
                    agg["minY"] = min(agg["minY"], y)
                    agg["maxY"] = max(agg["maxY"], y)
                    agg["cells"].add((x, y))

                for agg in aggregates.values():
                    min_x = agg["minX"]
                    min_y = agg["minY"]
                    span_x = max(1, agg["maxX"] - min_x + 1)
                    span_y = max(1, agg["maxY"] - min_y + 1)
                    info = agg.get("info") or {}
                    product_detail = dict(info) if isinstance(info, dict) else {}
                    img_name = product_detail.get("infoImg", "")
                    image_path = f"free_images/{img_name}" if img_name else ""
                    ordered_cells = sorted(agg.get("cells", []), key=lambda c: (c[1], c[0]))
                    cells_map[agg["product_code"]] = ordered_cells
                    grid_items.append({
                        "product_code": agg["product_code"],
                        "cell": [min_x, min_y],
                        "span": [span_x, span_y],
                        "process": agg["process"],
                        "image": image_path,
                        "product_detail": product_detail,
                        "cells_path": "",
                    })

                layout_type = "free" if show_type == 0 else "grid"

            if not grid_items:
                continue

            grid_items.sort(key=lambda gi: (gi["cell"][1], gi["cell"][0]))
            attach_cells(sid, cells_map, grid_items)

            back_img = sm.get("backImg", "")
            if back_img:
                back_img = f"free_images/{back_img}"
            if background_override:
                back_img = background_override

            payload = {
                "schema_version": schema_version,
                "layout_type": layout_type,
                "background": back_img,
                "grid_items": grid_items,
                "page_meta": {
                    "small_index": sm.get("index", 0),
                    "sequence": seq + 1,
                    "total_in_group": sm_count,
                    "show_type": show_type,
                    "layout_type": layout_type,
                    "layout_mode": layout_mode_value,
                    "layout_show": layout_flag_value,
                    "cm_flag": sm.get("cmFlg", 0),
                    "item_num": sm.get("itemNum", 0),
                    "back_color": sm.get("backColor", 0),
                    "source_offset": sm.get("offset", 0),
                }
            }
            pages[page_relpath(sid, 1)] = payload

    return pages, cell_files
