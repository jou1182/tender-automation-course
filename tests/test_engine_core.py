# -*- coding: utf-8 -*-
"""Unit tests for engine_core pure functions (dedup logic = heart of the system).

Covers Arabic normalization, cell cleaning, and identity building.
Run:  python tests\test_engine_core.py   (or pytest tests/)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import math
from engine_core import normalize_arabic, clean_cell, is_valid_tender_id, build_tender_identity

# Arabic constants
ALEF_HAMZA   = "أحمد"          # 'Ahmad' with hamza alef
ALEF_PLAIN   = "احمد"          # 'Ahmad' plain alef
WITH_TASHKEEL = "مَد"                # meem+fatha+dal
NO_TASHKEEL   = "مد"
WITH_TATWEEL  = "مــد"          # meem+tatweel+tatweel+dal
COL_ID     = "رقم المنافسة"   # tender number
COL_TITLE  = "اسم المنافسة"   # tender title
COL_OWNER  = "المالك"                                   # owner
COL_TYPE   = "نوع الأعمال"          # business type
COL_SECTOR = "القطاع"                                   # sector

PASS = []
FAIL = []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS  " if cond else "  FAIL  ") + name + ("  " + detail if detail and not cond else ""))

# ── normalize_arabic ──────────────────────────────────────────
check("hamza alef unified to plain alef", normalize_arabic(ALEF_HAMZA) == ALEF_PLAIN)
check("tashkeel stripped",                normalize_arabic(WITH_TASHKEEL) == NO_TASHKEEL)
check("tatweel removed",                  normalize_arabic(WITH_TATWEEL) == NO_TASHKEEL)
check("whitespace trimmed",               normalize_arabic("  x  ") == "x")
check("non-string input coerced",         normalize_arabic(123) == "123")
check("alef madda unified",               normalize_arabic("آل") == "ال")
check("alef hamza-below unified",         normalize_arabic("إلى") == "الى")

# ── clean_cell ────────────────────────────────────────────────
check("NaN -> default",        clean_cell(float("nan")) == "N/A")
check("None -> default",       clean_cell(None) == "N/A")
check("'nan' string -> default", clean_cell("nan") == "N/A")
check("'NaT' string -> default", clean_cell("NaT") == "N/A")
check("empty string -> default", clean_cell("   ") == "N/A")
check("custom default",        clean_cell("", default="") == "")
check("value passes through trimmed", clean_cell("  ABC-1  ") == "ABC-1")
check("number passes through", clean_cell(42) == "42")

# ── is_valid_tender_id ────────────────────────────────────────
check("valid id -> True",   is_valid_tender_id("T-2026-001") is True)
check("nan -> False",       is_valid_tender_id(float("nan")) is False)
check("empty -> False",     is_valid_tender_id("") is False)
check("'none' -> False",    is_valid_tender_id("None") is False)

# ── build_tender_identity ─────────────────────────────────────
row_with_id = {COL_ID: "12345", COL_TITLE: "t", COL_OWNER: "o", COL_TYPE: "b", COL_SECTOR: "s"}
check("explicit id wins", build_tender_identity(row_with_id) == "12345")

row_a = {COL_ID: "", COL_TITLE: ALEF_HAMZA, COL_OWNER: "own", COL_TYPE: "typ", COL_SECTOR: "sec"}
row_b = {COL_ID: "", COL_TITLE: ALEF_PLAIN, COL_OWNER: "own", COL_TYPE: "typ", COL_SECTOR: "sec"}
ida, idb = build_tender_identity(row_a), build_tender_identity(row_b)
check("AUTO- prefix + 16 hex", ida.startswith("AUTO-") and len(ida) == 21)
check("stable: same row -> same id", build_tender_identity(row_a) == ida)
check("normalization invariance: hamza vs plain alef -> SAME id (anti-duplicate)", ida == idb, f"{ida} vs {idb}")

row_c = dict(row_a); row_c[COL_TITLE] = "different title"
check("different title -> different id", build_tender_identity(row_c) != ida)

row_nan = {COL_ID: float("nan"), COL_TITLE: "t", COL_OWNER: "o", COL_TYPE: "b", COL_SECTOR: "s"}
check("nan id falls back to AUTO-", build_tender_identity(row_nan).startswith("AUTO-"))

print("\n" + "=" * 50)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} passed")
sys.exit(1 if FAIL else 0)