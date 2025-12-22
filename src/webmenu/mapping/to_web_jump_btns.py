import re
from .to_web_categories import _get_image_path,_check_is_multi_lang

def make_jump_btns_json(free_dir:str, osusume_dir:str,ini_bundle):
    jumpmenu = (
        ini_bundle
        .get("jumpmenu.ini", {})
        .get("sections", {})
        .get("jumpmenu", {})
    )

    buttons = {}

    for key, value in jumpmenu.items():
        if key.startswith("JmpMenu") and key.endswith("No"):
            idx = int(key.replace("JmpMenu", "").replace("No", ""))
            menu_no = [int(x) for x in value.split(",")]
            
            if idx not in buttons:
                buttons[idx] = {"id": idx}
                
            buttons[idx]["menuNo"] = menu_no

        elif key.startswith("JmpMenu") and key.endswith("BtnImg"):
            idx = int(key.replace("JmpMenu", "").replace("BtnImg", ""))
            
            if idx not in buttons:
                buttons[idx] = {"id": idx}
            
            # 多言語対応画像ディレクトリ一覧を取得
            multi_lang_dirs = _check_is_multi_lang(free_dir)
            jump_btn = _get_image_path(free_dir, osusume_dir, value, has_osusume=True, multi_lang_dirs=multi_lang_dirs)
            buttons[idx]["image"] = jump_btn

    return {
        "jumpmenu": {
            "buttons": list(buttons.values())
        }
    }


def make_checkin_btns_json(free_dir:str, osusume_dir:str, ini_bundle):
    checkin_hansoku = (
        ini_bundle
        .get("menu.ini", {})
        .get("sections", {})
        .get("checkin_hansoku", {})
    )
    
    result = {
        "use": checkin_hansoku.get("UseCheckinHansoku") == "1",
        "lockScreen": checkin_hansoku.get("LockScr") == "1",
        "screens": {}
    }
    
    bg_pattern = re.compile(r"Scr(\d+)BackImgName")
    btn_pattern = re.compile(r"Scr(\d+)Btn(\d+)(Image|Type|Pos)")
    
    # 多言語対応画像ディレクトリ一覧を取得
    multi_lang_dirs = _check_is_multi_lang(free_dir)
    
    screens = {}

    for key, value in checkin_hansoku.items():
        
        bg_match = bg_pattern.match(key)
        if bg_match:
            screen_no = bg_match.group(1)
            screens.setdefault(screen_no, {})
            screens[screen_no]["background"] = _get_image_path(free_dir, osusume_dir, value, has_osusume=False, multi_lang_dirs=multi_lang_dirs)
            screens[screen_no].setdefault("buttons", [])
            continue

        btn_match = btn_pattern.match(key)
        if not btn_match:
            continue

        screen_no, btn_no, field = btn_match.groups()
        btn_no = int(btn_no)

        screens.setdefault(screen_no, {})
        screens[screen_no].setdefault("buttons", [])

        buttons = screens[screen_no]["buttons"]
        btn = next((b for b in buttons if b["id"] == btn_no), None)
        if btn is None:
            btn = {"id": btn_no}
            buttons.append(btn)

        if field == "Image":
            btn["image"] = _get_image_path(free_dir, osusume_dir, value, has_osusume=False, multi_lang_dirs=multi_lang_dirs)

        elif field == "Type":
            btn["type"] = [int(x) for x in value.split(",")]

        elif field == "Pos":
            x, y = value.split(",")
            btn["pos"] = {
                "x": int(x),
                "y": int(y)
            }

    result["screens"] = screens

    return {
        "checkin_hansoku": result
    }