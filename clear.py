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

def should_keep(path, rel):
    """Check if a file or directory should be kept."""
    # Check if this exact path is in KEEP
    if rel in KEEP:
        return True

    # Check if this is a directory that contains kept files
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_rel = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
                if file_rel in KEEP:
                    return True

    return False

def clean():
    # First, remove everything that's not kept
    for entry in os.listdir(PROJECT_ROOT):
        path = os.path.join(PROJECT_ROOT, entry)
        rel = os.path.relpath(path, PROJECT_ROOT)

        # Skip hidden files/dirs (.git, .venv, __pycache__ etc.)
        if entry.startswith("."):
            continue

        # Check if we should keep this
        if should_keep(path, rel):
            continue

        if os.path.isfile(path):
            os.remove(path)
            print(f"removed file: {rel}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"removed dir:  {rel}")

    # Ensure required dirs exist
    for d in ["literature", "tools"]:
        os.makedirs(os.path.join(PROJECT_ROOT, d), exist_ok=True)

    print("\nDone. Project reverted to initial state.")

if __name__ == "__main__":
    clean()