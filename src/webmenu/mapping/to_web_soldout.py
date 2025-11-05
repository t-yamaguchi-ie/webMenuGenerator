
import re


def make_soldout_json(ini_bundle):
    soldout_settings = (
        ini_bundle
        .get("menu.ini", {})
        .get("sections", {})
        .get("soldout", {})
    )
    
    frm_btn_images = {}
    cell_btn_images = {}
    
    frm_pattern = re.compile(r"^FrmBtnImgName(\d*)$")
    cell_pattern = re.compile(r"^CellBtnImgName(\d*)$")
    
    for key, filename in soldout_settings.items():
        frm_match = frm_pattern.match(key)
        if frm_match:
            index = frm_match.group(1)
            index = index if index else "1"
            frm_btn_images[index] = filename
            continue
        
        cell_match = cell_pattern.match(key)
        if cell_match:
            index = cell_match.group(1)
            index = index if index else "1"
            cell_btn_images[index] = filename
            continue

    return {
        "backImage": soldout_settings.get("BackImgName", ""),
        "frm_btn_images": frm_btn_images,
        "cell_btn_images": cell_btn_images
    }