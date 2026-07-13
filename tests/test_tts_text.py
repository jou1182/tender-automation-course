# -*- coding: utf-8 -*-
"""Unit tests for tts_text.py (extracted TTS text-processing)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tts_text import _num_to_ar, _tts_prepare, _transliterate, _apply_pronunciation, _split_for_tts

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS  " if cond else "  FAIL  ") + name + ("  [" + detail + "]" if detail and not cond else ""))

# ── _num_to_ar (Egyptian Arabic) ─────────────────────────────
check("0 -> sifr",        _num_to_ar(0) == "صفر")
check("5 -> khamsa",      _num_to_ar(5) == "خمسة")
check("25 -> khamsa we 3eshrin", _num_to_ar(25) == "خمسة وعشرين", _num_to_ar(25))
check("100 -> meyya",     _num_to_ar(100) == "مية")
check("200 -> metein",    _num_to_ar(200) == "ميتين")
check("1000 -> alf",      _num_to_ar(1000) == "ألف")
check("2000 -> alfein",   _num_to_ar(2000) == "ألفين")
check("negative handled", _num_to_ar(-3).startswith("ناقص"))
check("million mentioned", "مليون" in _num_to_ar(1_500_000))
check("billion mentioned", "مليار" in _num_to_ar(2_000_000_000))
check("deterministic",    _num_to_ar(347) == _num_to_ar(347))

# ── _tts_prepare ─────────────────────────────────────────────
r = _tts_prepare("الموعد 2026-07-05")
check("ISO date -> month name, no digits", ("يوليو" in r) and not any(c.isdigit() for c in r), r)
r = _tts_prepare("نسبة الإنجاز 85%")
check("percent -> bilmeyya", "بالمية" in r, r)
r = _tts_prepare("القيمة ١٥ ريال")
check("Arabic-Indic digits converted", "خمستاشر" in r, r)
r = _tts_prepare("المبلغ 1,500,000 ريال")
check("thousand separators handled", "مليون" in r, r)
r = _tts_prepare("**عنوان** مع `كود` و #وسم")
check("markdown stripped", not any(ch in r for ch in "*`#"), r)
long_text = "جملة طويلة جداً، " * 100
check("550-char cap enforced", len(_tts_prepare(long_text)) <= 551)

# ── _transliterate / _apply_pronunciation ────────────────────
check("transliterate returns arabic-ish", _transliterate("ok") != "ok")
r = _apply_pronunciation("النظام Excel جاهز")
check("english word converted", "Excel" not in r, r)

# ── _split_for_tts ───────────────────────────────────────────
check("short text -> 1 part",  len(_split_for_tts("جملة واحدة.")) == 1)
long5 = "الجملة الأولى هنا. الجملة الثانية هنا. الجملة الثالثة هنا. الجملة الرابعة هنا. الجملة الخامسة هنا."
parts = _split_for_tts(long5)
check("5 sentences -> 2 parts", len(parts) == 2, str(len(parts)))
check("no content lost", "".join(parts).replace(" ", "") == long5.replace(" ", ""))

print("\n" + "=" * 50)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} passed")
sys.exit(1 if FAIL else 0)