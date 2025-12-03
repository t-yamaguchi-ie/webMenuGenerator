import os, glob

def parse_ini_text(text:str):
    # NOTE: PoCではシンプルなINIローダ（重複キーは配列化）
    data = {"sections":{}}
    cur = None
    for line in text.splitlines():
        line=line.strip()
        if not line or line.startswith((';','#')):
            continue
        if line.startswith('[') and line.endswith(']'):
            cur = line[1:-1].strip()
            data["sections"].setdefault(cur,{})
        elif '=' in line and cur:
            k,v = line.split('=',1)
            k=k.strip(); v=v.strip()
            sect = data["sections"][cur]
            if k in sect:
                # 重複キー→配列化
                if isinstance(sect[k], list):
                    sect[k].append(v)
                else:
                    sect[k] = [sect[k], v]
            else:
                sect[k]=v
    return data

def load_all_ini(config_dir:str):
    bundle = {}
    pattern = os.path.join(config_dir, "*.ini")
    
    language_ini_path = os.path.join(config_dir, "language.ini")
    encoding = "utf-8" if os.path.exists(language_ini_path) else "shift_jis"
    
    for path in glob.glob(pattern):
        with open(path, "r", encoding=encoding, errors="ignore") as f:
            text = f.read()
        bundle[os.path.basename(path)] = parse_ini_text(text)
    return bundle
