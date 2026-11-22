#!/usr/bin/env python3
"""Copy the shipped front-page image to the output directory.

The poster itself is drawn ahead of time by gen_poster.py and shipped
in this repository as entry.png. This entrypoint only copies those
bytes, so every run writes exactly the same file.
"""
import os
import shutil
import sys
from pathlib import Path


def main():
    # The shipped image sits beside this file in the repository root.
    source = Path(__file__).resolve().parent / "entry.png"
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output_dir / "entry.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
