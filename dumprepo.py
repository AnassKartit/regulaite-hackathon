#!/usr/bin/env python
"""
dump_repo.py – bundle this repo into a single file
   $ python dump_repo.py            # repo_bundle.txt (plain text)
   $ python dump_repo.py --zip      # repo_bundle.zip (compressed)
   $ python dump_repo.py --dry-run  # show what would be included
"""
from __future__ import annotations
import argparse, datetime as dt, os, pathlib, zipfile

# ─────────────────────────── CLI ────────────────────────────
ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".", help="Repo root (default: current dir)")
ap.add_argument("--out",  help="Explicit output file name")
ap.add_argument("--zip",  action="store_true", help="Create a ZIP instead of TXT")
ap.add_argument("--dry-run", action="store_true", help="Only list matched files")
args = ap.parse_args()

root = pathlib.Path(args.root).resolve()
if not root.is_dir():
    raise SystemExit(f"❌ No such directory: {root}")

# ────────────── inclusion / exclusion rules ────────────────
KEEP_EXT  = {".py", ".json", ".yml", ".yaml", ".bicep", ".md", ".txt", ".jsx", ".js"}
SKIP_DIR  = {".venv", "venv", "__pycache__", ".git", ".pytest_cache", "node_modules", "dist"}
SKIP_EXT  = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".zip"}
SKIP_FILES = {"package-lock.json"}

def want_file(path: pathlib.Path) -> bool:
    suff = path.suffix.lower()
    return suff in KEEP_EXT and suff not in SKIP_EXT and path.name not in SKIP_FILES

# ───────────────── gather candidate files ──────────────────
candidates: list[pathlib.Path] = []

for curr_dir, dirnames, filenames in os.walk(root):
    # prune directories we don’t want to descend into
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]

    for fname in filenames:
        fpath = pathlib.Path(curr_dir, fname)
        rel   = fpath.relative_to(root)
        if want_file(rel):
            candidates.append(fpath)

candidates.sort()

if not candidates:
    raise SystemExit("❌ Nothing matched – adjust filters?")

if args.dry_run:
    print("Would include:")
    for p in candidates:
        print("  ·", p.relative_to(root))
    print(f"\nTotal: {len(candidates)} file(s)")
    raise SystemExit()

# ───────────────────── output filename ─────────────────────
outfile = pathlib.Path(
    args.out or ("repo_bundle.zip" if args.zip else "repo_bundle.txt")
)

print(f"📦  Bundling {len(candidates)} files → {outfile}")
timestamp = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"

# ──────────────────────── write bundle ─────────────────────
if args.zip:
    with zipfile.ZipFile(outfile, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in candidates:
            zf.write(p, arcname=p.relative_to(root))
else:
    sep = "#" * 80
    with outfile.open("w", encoding="utf-8") as fh:
        fh.write(f"{sep}\n# Repository bundle generated {timestamp}\n{sep}\n\n")
        for p in candidates:
            rel = p.relative_to(root)
            fh.write(f"{sep}\n# BEGIN {rel}\n{sep}\n")
            fh.write(p.read_text(encoding="utf-8", errors="replace"))
            fh.write(f"\n{sep}\n# END {rel}\n{sep}\n\n")

print("✅  Done.")