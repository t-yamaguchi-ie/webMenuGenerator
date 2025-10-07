from ..core.ids import page_relpath, small_id
from ..parsers import menudb_reader as mreader


def _build_iteminfo_map(menudb: dict):
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

    # item_info ブロックの先頭(base)から逆算して item_cell/item_frame ブロックの開始位置を得る
    item_frame_size = mreader.ITEM_FRAME_INFORMATION_SIZE * counts.get("ItemFrmNum", 0)
    item_cell_size = mreader.ITEM_CELL_INFORMATION_SIZE * counts.get("ItemCellNum", 0)
    item_cell_base = info_base - item_frame_size - item_cell_size

    smenu_offset_index = {sm.get("offset"): idx for idx, sm in enumerate(smenus)}

    pages = {}
    cell_files = {}
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
                if code not in aggregates:
                    aggregates[code] = {
                        "product_code": code,
                        "minX": cell.get("cellX", 0),
                        "maxX": cell.get("cellX", 0),
                        "minY": cell.get("cellY", 0),
                        "maxY": cell.get("cellY", 0),
                        "process": cell.get("process", 0),
                        "info": info,
                        "cells": set(),
                    }
                else:
                    agg = aggregates[code]
                    x = cell.get("cellX", 0)
                    y = cell.get("cellY", 0)
                    agg["minX"] = min(agg["minX"], x)
                    agg["maxX"] = max(agg["maxX"], x)
                    agg["minY"] = min(agg["minY"], y)
                    agg["maxY"] = max(agg["maxY"], y)
                aggregates[code]["cells"].add((cell.get("cellX", 0), cell.get("cellY", 0)))

            grid_items = []
            cells_map = {}
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

            grid_items.sort(key=lambda gi: (gi["cell"][1], gi["cell"][0]))

            if not grid_items:
                continue

            sid = small_id(mm.get("l_index", 0), mm.get("index", 0), sm.get("index", 0))

            if cells_map:
                rel_cells_path = f"small/{sid}/cells.json"
                cell_files[rel_cells_path] = {
                    "cells": cells_map
                }
                for item in grid_items:
                    item["cells_path"] = rel_cells_path
            else:
                for item in grid_items:
                    item["cells_path"] = ""

            back_img = sm.get("backImg", "")
            if back_img:
                back_img = f"free_images/{back_img}"
            if sm.get("showType", 0) == 6:
                layout_type = "recommended"
            elif sm.get("showType", 0) == 0:
                layout_type = "free"
            else:
                layout_type = "grid"

            payload = {
                "schema_version": schema_version,
                "layout_type": layout_type,
                "background": back_img,
                "grid_items": grid_items,
                "page_meta": {
                    "small_index": sm.get("index", 0),
                    "sequence": seq + 1,
                    "total_in_group": sm_count,
                    "show_type": sm.get("showType", 0),
                    "layout_type": layout_type,
                    "cm_flag": sm.get("cmFlg", 0),
                    "item_num": sm.get("itemNum", 0),
                    "back_color": sm.get("backColor", 0),
                    "source_offset": sm.get("offset", 0),
                }
            }
            pages[page_relpath(sid, 1)] = payload

    return pages, cell_files
