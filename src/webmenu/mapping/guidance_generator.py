import os
import json
import re
import csv

def run_guidance_process(target_web_content_dir):
    """
    指定された web_content ディレクトリを走査し、
    folder_guidance.json と folder_list.csv を出力する
    """
    small_dir = os.path.join(target_web_content_dir, "small")
    json_output = os.path.join(target_web_content_dir, "folder_guidance.json")
    csv_output = os.path.join(target_web_content_dir, "folder_list.csv")

    if not os.path.exists(small_dir):
        print(f"Error: {small_dir} not found.")
        return

    results = []
    folders = sorted(os.listdir(small_dir))

    # --- Step 1: スキャン処理 ---
    for folder_name in folders:
        folder_path = os.path.join(small_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        json_path = os.path.join(folder_path, "page-1.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                small_index = data.get("page_meta", {}).get("small_index")
                grid_items = data.get("grid_items", [])
                image_path = grid_items[0].get("image", "") if grid_items else ""

                # 画像パスから大中小コードを抽出
                match = re.search(r'images/(\d+)/(\d+)/(\d+)/', image_path.replace('\\', '/'))
                if match:
                    l, m, s = match.group(1), match.group(2), match.group(3)
                    cat_code = f"{l}{m}{s}"
                else:
                    l = m = s = cat_code = "unknown"

                entry = {
                    "id": small_index,
                    "folder": folder_name,
                    "category_code": cat_code,
                    "hierarchy": {"large": l, "middle": m, "small": s},
                    "json_file": "page-1.json"
                }
                results.append(entry)
            except Exception as e:
                print(f"Warning: Failed to read {folder_name} ({e})")

    # --- Step 2: JSON 出力 ---
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Generated: {json_output}")

    # --- Step 3: CSV (Excel用) 出力 ---
    # Python 3.8標準のcsvモジュールを使用（BOM付きUTF-8でExcel対応）
    with open(csv_output, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "フォルダ名", "分類コード", "大分類", "中分類", "小分類", "元ファイル"])
        for item in results:
            writer.writerow([
                item["id"], item["folder"], item["category_code"],
                item["hierarchy"]["large"], item["hierarchy"]["middle"],
                item["hierarchy"]["small"], item["json_file"]
            ])
    print(f"Generated: {csv_output}")

if __name__ == "__main__":
    # 直接実行する場合のテスト用
    import sys
    if len(sys.argv) > 1:
        run_guidance_process(sys.argv[1])
    else:
        print("Usage: python guidance_generator.py <path_to_web_content>")