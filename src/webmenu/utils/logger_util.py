import logging
import os
from datetime import datetime
import configparser

# ------------------------------------------------------------
# 共通ログ作成ユーティリティ
#  - コンソール + ファイル両方へ出力
#  - ログファイル名: {name}_YYYYMMDD.log
# ------------------------------------------------------------
def setup_logger(name: str = "smenu_watcher", level: int = logging.INFO) -> logging.Logger:
    # --------------------------------------------
    # 日付文字列取得
    # --------------------------------------------
    today = datetime.now().strftime("%Y%m%d")

    # --------------------------------------------
    # ログ出力先ディレクトリ決定
    # 優先順位:
    # 1) MIS.INI の [LOG] セクション設定
    # 2) D:\WebMenu\logs
    # 3) 上記が利用不可の場合はログ無効
    # --------------------------------------------
    log_dir = None
    ini_path = r"C:\MIS\INI\MIS.INI"

    if os.path.exists(ini_path):
        try:
            config = configparser.ConfigParser()
            config.read(ini_path, encoding="cp932")
            if config.has_section("LOG"):
                base = config.get("LOG", "MIS_LOG_FOLDER", fallback=None)
                if base:
                    log_dir = os.path.join(base, "WebMenu", "logs")
        except Exception:
            log_dir = None

    if log_dir is None and os.path.isdir("D:\\"):
        log_dir = r"D:\WebMenu\logs"

    # --------------------------------------------
    # ログファイルパス作成
    # --------------------------------------------
    log_file = None
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{name}_{today}.log")

    # --------------------------------------------
    # Logger 作成
    # --------------------------------------------
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # 上位 Logger へ伝搬しない

    # 既存ハンドラがあれば再利用
    if logger.handlers:
        return logger

    # フォーマット統一
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # コンソール出力
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイル出力
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"ログファイル作成に失敗しました: {log_file}. {e}")

    return logger
