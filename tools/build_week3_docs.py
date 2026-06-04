# -*- coding: utf-8 -*-
"""Regenerate week-3 Word deliverables in the current 18-module project scope.

This wrapper keeps the generated documents aligned with 项目要求.txt:
- SRS / 需求分析: generated from the local SRS template copy under 03_需求分析.
- HLD / 系统设计: updated in place under 04_系统设计.

The original template directory under 交付物/巩固式解密模板 is never modified.
"""
from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    build_srs = load_module("build_srs_v2", TOOLS_DIR / "build_srs_v2.py")
    build_hld = load_module("build_hld_docx_from_md", TOOLS_DIR / "build_hld_docx_from_md.py")

    build_srs.main()
    build_hld.build()
    print("Done. Week-3 SRS and HLD deliverables are aligned to the 18-module SmartPark scope.")


if __name__ == "__main__":
    main()
