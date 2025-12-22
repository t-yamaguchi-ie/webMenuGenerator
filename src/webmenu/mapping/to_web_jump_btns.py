from .to_web_categories import _get_image_path

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
            
            jump_btn = _get_image_path(free_dir, osusume_dir, value, has_osusume=True, multi_lang_dirs=[])
            buttons[idx]["image"] = jump_btn

    return {
        "jumpmenu": {
            "buttons": list(buttons.values())
        }
    }