import os
import csv
from typing import List, Dict


def read_datas(datas: str):

    readers = {
        "iteminfoLang": (_read_item_info_language, {"iteminfolang.csv"}),
    }

    result = {key: {} for key in readers}

    if not os.path.isdir(datas):
        return result

    for name in os.listdir(datas):
        path = os.path.join(datas, name)

        if os.path.isfile(path):
            lower = name.lower()
            for key, (reader, filenames) in readers.items():
                if lower in filenames:
                    result[key]["default"] = reader(path)
            continue

        if os.path.isdir(path):
            lang = name

            for fname in os.listdir(path):
                fpath = os.path.join(path, fname)
                if not os.path.isfile(fpath):
                    continue

                lower = fname.lower()
                for key, (reader, filenames) in readers.items():
                    if lower in filenames:
                        result[key][lang] = reader(fpath)

    return result


def _read_item_info_language(path: str) -> List[Dict]:
    items = []

    if not os.path.isfile(path):
        return items

    try:
        with open(path, "r", encoding="utf-8", errors="strict") as f:
            sample = f.read(1024)
            if not sample:
                return items

            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
            reader = csv.reader(f, dialect)

            for row_idx, row in enumerate(reader):
                if not row:
                    continue

                if row[0].startswith("#") or row[0] == "ItemCode":
                    continue

                if len(row) < 2:
                    continue

                raw_name = row[1] if row[1] is not None else ""

                try:
                    item_code = int(row[0])
                except ValueError:
                    continue

                items.append({
                    "item_code": item_code,
                    "name": raw_name,
                })

    except Exception as e:
        print(f"エラー:CSVファイルの読み取りに失敗 | パス：{path} | 例外：{str(e)}")
        return items

    return items
