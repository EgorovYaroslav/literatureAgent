#!/usr/bin/env python3
"""Revert project to initial state, keeping only specified files."""

import os
import shutil
import glob

KEEP = {
    "promt1.md",
    "promt2.md",
    "literature/2507.04211v1.pdf",
    "tools/scihub_tool.py",
}

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def clean():
    for entry in os.listdir(PROJECT_ROOT):
        path = os.path.join(PROJECT_ROOT, entry)
        rel = os.path.relpath(path, PROJECT_ROOT)
        if rel in KEEP:
            continue
        # skip hidden files/dirs (.git, .venv, __pycache__ etc.)
        if entry.startswith("."):
            continue
        if os.path.isfile(path):
            os.remove(path)
            print(f"removed file: {rel}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"removed dir:  {rel}")

    # ensure required dirs exist
    for d in ["literature", "tools"]:
        os.makedirs(os.path.join(PROJECT_ROOT, d), exist_ok=True)

    print("\nDone. Project reverted to initial state.")

if __name__ == "__main__":
    clean()
