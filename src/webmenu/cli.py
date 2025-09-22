import argparse
from .pipeline import run_pipeline

def build_parser():
    p = argparse.ArgumentParser(prog="webmenu", description="WebMenuGenerator CLI")
    sp = p.add_subparsers(dest="cmd", required=True)

    g = sp.add_parser("generate", help="Convert legacy dumps to web_content")
    g.add_argument("--free", required=True, help="Path to 'free' directory (LZH展開済み)")
    g.add_argument("--osusume", required=True, help="Path to 'osusume' directory (LZH展開済み)")
    g.add_argument("--out", required=True, help="Output root path for builds/{ref}")
    g.add_argument("--ref", default="", help="Optional ref (YYYYMMDD-hhmmss-commit). Auto if empty.")
    g.add_argument("--schema-version", default="0.1", help="web_content schema version")
    g.add_argument("--skip-assets", action="store_true", help="Skip asset copy/optimization")
    return p

def main():
    args = build_parser().parse_args()
    if args.cmd == "generate":
        run_pipeline(args)

if __name__ == "__main__":
    main()
