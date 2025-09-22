# -*- coding: utf-8 -*-
import os, struct

# ===== Javaの定数をそのまま移植 =====

OFS_LONG = 4
OFS_CHAR = 1

# Header offsets
HEADER_INFORMATION_FILE_SIZE      = 0
HEADER_INFORMATION_LMENU_MAX      = HEADER_INFORMATION_FILE_SIZE + OFS_LONG          # +4
HEADER_INFORMATION_MMENU_MAX      = HEADER_INFORMATION_LMENU_MAX + OFS_CHAR          # +5
HEADER_INFORMATION_WIDTH          = HEADER_INFORMATION_MMENU_MAX + OFS_CHAR          # +6
HEADER_INFORMATION_HEIGHT         = HEADER_INFORMATION_WIDTH + OFS_CHAR              # +7
HEADER_INFORMATION_SMENU_NUM      = HEADER_INFORMATION_HEIGHT + OFS_CHAR             # +8
HEADER_INFORMATION_ITEM_CELL_NUM  = HEADER_INFORMATION_SMENU_NUM + OFS_LONG          # +12
HEADER_INFORMATION_ITEM_FRM_NUM   = HEADER_INFORMATION_ITEM_CELL_NUM + OFS_LONG      # +16
HEADER_INFORMATION_ITEM_INFO_NUM  = HEADER_INFORMATION_ITEM_FRM_NUM + OFS_LONG       # +20
HEADER_INFORMATION_SUB_CODE_INFO_NUM = HEADER_INFORMATION_ITEM_INFO_NUM + OFS_LONG   # +24
HEADER_INFORMATION_SUB_SMENU_NUM  = HEADER_INFORMATION_SUB_CODE_INFO_NUM + OFS_LONG  # +28
HEADER_INFORMATION_SUB_ITEM_CELL_NUM = HEADER_INFORMATION_SUB_SMENU_NUM + OFS_LONG   # +32
HEADER_INFORMATION_SUB_ITEM_FRM_NUM  = HEADER_INFORMATION_SUB_ITEM_CELL_NUM + OFS_LONG # +36
# HEADER_INFORMATION_SIZE = 40 （使わない）

# Java と同じく「基本情報」ブロックのサイズを追従して算出
# 40 + 20*(5 + 5 + 12 + 8 + 8 + 1 + 14) = 1100
BASE_INFORMATION_LM = 4 + 1 + 1 + 2 + 4 * 8
BASE_INFORMATION_SM = BASE_INFORMATION_LM + (16 + 4) * 5
BASE_INFORMATION_BF = BASE_INFORMATION_SM + (16 + 4) * 5
BASE_INFORMATION_OF = BASE_INFORMATION_BF + (16 + 4) * 12
BASE_INFORMATION_CO = BASE_INFORMATION_OF + (16 + 4) * 8
BASE_INFORMATION_II = BASE_INFORMATION_CO + (16 + 4) * 8
BASE_INFORMATION_MS = BASE_INFORMATION_II + (16 + 4) * 1
LMENU_INFORMATION = BASE_INFORMATION_MS + (16 + 4) * 14

# ↑ Javaでは：LMENU_INFORMATION = BASE_INFORMATION_MS + (16+4)*14
# ここは正確に合せたい場合、上の展開をそのまま使うか、値をログで出して固定化してもOK

# 構造体サイズ（Javaそのまま）
LMENU_INFORMATION_SIZE = 1 + 1 + 1 + 1 + (16 + 4) * 5
MMENU_INFORMATION_SIZE = 1 + 3 + (16 + 4) * 2 + 4 + 4
SMENU_INFORMATION_SIZE = 1 + 1 + 2 + 4 + 4 + 16 + 4 + 4
ITEM_CELL_INFORMATION_SIZE  = 1 + 1 + 1 + 1 + 2 * 16 + 1 + 1 + 2 + 4 + 4 + 4
ITEM_FRAME_INFORMATION_SIZE = 1 + 1 + 1 + 1 + 16 + 4 + 2 * 32 + 1 + 1 + 2 + 2 * 8 + 1 + 1 + 2 + 2 * 8 + 1 + 1 + 2 + 2 * 32 + 1 + 1 + 2 + 4
ITEM_INFORMATION_SIZE       = (
    4 + 1 + 1 + 1 + 1  # code, flags, dmy
    + 4 + 4             # prices
    + (2 * 32)          # name
    + 1 + 1 + 1 + 1     # menuAtt, sub flags, dmy
    + 4 + 4 + 4         # sub addr, cmdNo, set addr
    + 1 + 3             # info + dmy
    + 16                # infoImg file name(16 bytes)
    + 4                 # infoImg addr
    + (2 * 128)         # infoComment
)
# Java定義と一致する 376 バイト


def _be_u32(b, off):  # Big-endian uint32 → Python int
    return struct.unpack_from(">I", b, off)[0]

def _be_i32(b, off):  # Big-endian int32
    return struct.unpack_from(">i", b, off)[0]

def _u16_name(b, off, chars):
    """UTF-16（BOMなし）→ Javaと同じくUTF-16（BE前提）で読む。NUL2byte終端まで。"""
    raw = b[off: off + chars*2]
    # 00 00 を見つけて切る
    end = 0
    while end + 1 < len(raw):
        if raw[end] == 0x00 and raw[end+1] == 0x00:
            break
        end += 2
    raw = raw[:end]
    try:
        return raw.decode("utf-16-be", "ignore").strip()
    except:
        return ""


def _sjis_filename(b, off, size=16):
    """Shift_JIS（NULパディング）をJava実装相当のtrim付きで読み取る。"""
    raw = b[off: off + size]
    if not raw:
        return ""
    raw = raw.tobytes() if hasattr(raw, 'tobytes') else bytes(raw)
    raw = raw.split(b'\x00', 1)[0]
    try:
        return raw.decode('shift_jis', 'ignore').strip()
    except UnicodeDecodeError:
        return raw.decode('latin-1', 'ignore').strip()

def read_menudb(path: str) -> dict:
    with open(path, "rb") as f:
        buf = f.read()

    # ===== ヘッダの件数をJavaと同じ方法で読む（BE相当） =====
    L = buf[HEADER_INFORMATION_LMENU_MAX]
    M = buf[HEADER_INFORMATION_MMENU_MAX]
    SMenuNum    = _be_u32(buf, HEADER_INFORMATION_SMENU_NUM)
    ItemCellNum = _be_u32(buf, HEADER_INFORMATION_ITEM_CELL_NUM)
    ItemFrmNum  = _be_u32(buf, HEADER_INFORMATION_ITEM_FRM_NUM)
    ItemInfoNum = _be_u32(buf, HEADER_INFORMATION_ITEM_INFO_NUM)

    buf_view = memoryview(buf)

    # ===== 大分類 (LMENU) =====
    lmenus = []
    lmenu_base = LMENU_INFORMATION
    for i in range(L):
        off = lmenu_base + LMENU_INFORMATION_SIZE * i
        if off + LMENU_INFORMATION_SIZE > len(buf):
            break
        lmenus.append({
            "index": i + 1,
            "offset": off,
            "property": buf_view[off],
            "freeFlg": buf_view[off + 1],
            "scrToFrmNo": buf_view[off + 2],
            "scrBtnImg": _sjis_filename(buf_view, off + 4),
            "scrBtnImgAddr": _be_u32(buf_view, off + 20),
            "lmFrmBackImg": _sjis_filename(buf_view, off + 24),
            "lmFrmBackImgAddr": _be_u32(buf_view, off + 40),
            "frmOffBtnImg": _sjis_filename(buf_view, off + 44),
            "frmOffBtnImgAddr": _be_u32(buf_view, off + 60),
            "frmOnBtnImg": _sjis_filename(buf_view, off + 64),
            "frmOnBtnImgAddr": _be_u32(buf_view, off + 80),
            "mmFrmBackImg": _sjis_filename(buf_view, off + 84),
            "mmFrmBackImgAddr": _be_u32(buf_view, off + 100),
        })

    mmenu_base = lmenu_base + LMENU_INFORMATION_SIZE * L
    mmenus = []
    total_m = L * M
    for idx in range(total_m):
        off = mmenu_base + MMENU_INFORMATION_SIZE * idx
        if off + MMENU_INFORMATION_SIZE > len(buf):
            break
        li, mi = divmod(idx, M)
        mmenus.append({
            "l_index": li + 1,
            "index": mi + 1,
            "offset": off,
            "property": buf_view[off],
            "btnOnImg": _sjis_filename(buf_view, off + 4),
            "btnOnImgAddr": _be_u32(buf_view, off + 20),
            "btnOffImg": _sjis_filename(buf_view, off + 24),
            "btnOffImgAddr": _be_u32(buf_view, off + 40),
            "sMenuNum": _be_u32(buf_view, off + 44),
            "sMenuAddr": _be_u32(buf_view, off + 48),
        })

    smenu_base = mmenu_base + MMENU_INFORMATION_SIZE * L * M
    smenus = []
    for si in range(SMenuNum):
        off = smenu_base + SMENU_INFORMATION_SIZE * si
        if off + SMENU_INFORMATION_SIZE > len(buf):
            break
        smenus.append({
            "index": si + 1,
            "offset": off,
            "showType": buf_view[off],
            "cmFlg": buf_view[off + 1],
            "itemNum": _be_u32(buf_view, off + 4),
            "backColor": _be_u32(buf_view, off + 8),
            "backImg": _sjis_filename(buf_view, off + 12),
            "backImgAddr": _be_u32(buf_view, off + 28),
            "itemAddr": _be_u32(buf_view, off + 32),
        })

    item_cell_base = smenu_base + SMENU_INFORMATION_SIZE * SMenuNum
    item_cells = []
    for ci in range(ItemCellNum):
        off = item_cell_base + ITEM_CELL_INFORMATION_SIZE * ci
        if off + ITEM_CELL_INFORMATION_SIZE > len(buf):
            break
        item_cells.append({
            "index": ci + 1,
            "offset": off,
            "process": buf_view[off],
            "cellX": buf_view[off + 1],
            "cellY": buf_view[off + 2],
            "text": _u16_name(buf, off + 4, 14),
            "fontSize": buf_view[off + 36],
            "textFrame": buf_view[off + 37],
            "option": _be_u32(buf_view, off + 44),
            "itemInfoAddr": _be_u32(buf_view, off + 48),
        })

    item_frame_base = item_cell_base + ITEM_CELL_INFORMATION_SIZE * ItemCellNum
    item_frames = []
    for fi in range(ItemFrmNum):
        off = item_frame_base + ITEM_FRAME_INFORMATION_SIZE * fi
        if off + ITEM_FRAME_INFORMATION_SIZE > len(buf):
            break
        item_frames.append({
            "index": fi + 1,
            "offset": off,
            "process": buf_view[off],
            "cellX": buf_view[off + 1],
            "cellY": buf_view[off + 2],
            "itemImg": _sjis_filename(buf_view, off + 4),
            "itemImgAddr": _be_u32(buf_view, off + 20),
            "nameText": _u16_name(buf, off + 24, 32),
            "nameFontSize": buf_view[off + 88],
            "nameTextColor": buf_view[off + 89],
            "priceText": _u16_name(buf, off + 92, 8),
            "priceFontSize": buf_view[off + 100],
            "priceTextColor": buf_view[off + 101],
            "taxPriceText": _u16_name(buf, off + 104, 8),
            "taxPriceFontSize": buf_view[off + 112],
            "taxPriceTextColor": buf_view[off + 113],
            "infoText": _u16_name(buf, off + 116, 32),
            "infoFontSize": buf_view[off + 180],
            "infoTextColor": buf_view[off + 181],
            "itemInfoAddr": _be_u32(buf_view, off + 184),
        })

    # ===== Javaの式そのままで ITEM_INFO 配列の先頭(base) =====
    base = (
        LMENU_INFORMATION
        + LMENU_INFORMATION_SIZE * L
        + MMENU_INFORMATION_SIZE * L * M
        + SMENU_INFORMATION_SIZE * SMenuNum
        + ITEM_CELL_INFORMATION_SIZE * ItemCellNum
        + ITEM_FRAME_INFORMATION_SIZE * ItemFrmNum
    )

    item_infos = []
    for i in range(ItemInfoNum):
        off = base + ITEM_INFORMATION_SIZE * i
        if off + ITEM_INFORMATION_SIZE > len(buf):
            break

        code = _be_i32(buf, off)
        free_flg = buf_view[off + 4]
        sold_out_flg = buf_view[off + 5]
        min_item_num = buf_view[off + 6]
        no_tax_price = _be_i32(buf, off + 8)
        tax_price = _be_i32(buf, off + 12)
        name = buf_view[off + 16: off + 16 + 64].tobytes().decode('utf-16-be', 'ignore').split('\x00', 1)[0].strip()

        menu_att = buf_view[off + 80]
        sub_menu_flg = buf_view[off + 81]
        sub_set_num = buf_view[off + 82]
        sub_menu_addr = _be_u32(buf_view, off + 84)
        cmd_no = _be_u32(buf_view, off + 88)
        set_item_addr = _be_u32(buf_view, off + 92)
        info = buf_view[off + 93]
        info_img_raw = buf_view[off + 96: off + 96 + 16].tobytes()
        info_img = info_img_raw.split(b'\x00', 1)[0].decode('shift_jis', 'ignore').strip()
        info_img_addr = _be_u32(buf_view, off + 112)
        info_comment = _u16_name(buf, off + 116, 128)

        item_infos.append({
            "index": i,
            "code": code,
            "freeFlg": free_flg,
            "soldOutFlg": sold_out_flg,
            "minItemNum": min_item_num,
            "noTaxPrice": no_tax_price,
            "taxPrice": tax_price,
            "price": tax_price,
            "name": name,
            "menuAtt": menu_att,
            "subMenuFlg": sub_menu_flg,
            "subSetNum": sub_set_num,
            "subMenuAddr": sub_menu_addr,
            "cmdNo": cmd_no,
            "setItemAddr": set_item_addr,
            "info": info,
            "infoImg": info_img,
            "infoImgAddr": info_img_addr,
            "infoComment": info_comment,
        })


    return {
        "lmenus": lmenus,
        "mmenus": mmenus,
        "smenus": smenus,
        "item_cells": item_cells,
        "item_frames": item_frames,
        "item_infos": item_infos,
        "meta": {
            "path": os.path.abspath(path),
            "counts": {
                "L": L, "M": M,
                "SMenuNum": SMenuNum,
                "ItemCellNum": ItemCellNum,
                "ItemFrmNum": ItemFrmNum,
                "ItemInfoNum": ItemInfoNum
            },
            "base": base,
            "stride": ITEM_INFORMATION_SIZE,
            "endian": "BE",
        }
    }
