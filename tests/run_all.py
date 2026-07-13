# -*- coding: utf-8 -*-
"""Pre-deploy quality gate: compiles every core module + runs all unit suites.
Deploy scripts refuse to upload when this exits non-zero. Run manually:
    .venv/Scripts/python.exe tests/run_all.py
"""
import subprocess, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from pathlib import Path

BASE = Path(__file__).parent.parent
PY = sys.executable

COMPILE = ["web_dashboard.py", "bot_daemon.py", "dashboard_templates.py",
           "admin_templates.py", "bp_engineer.py", "engine_core.py",
           "db_manager.py", "ai_assistant.py", "tts_text.py",
           "analytics_engine.py", "chat_handler.py", "pdf_report.py"]
TESTS = ["test_engine_core.py", "test_tts_text.py", "test_ai_assistant.py"]

failed = []
print("=" * 54)
print("  PRE-DEPLOY QUALITY GATE")
print("=" * 54)

files = [str(BASE / f) for f in COMPILE if (BASE / f).exists()]
r = subprocess.run([PY, "-m", "py_compile", *files], capture_output=True, text=True)
if r.returncode == 0:
    print(f"  [OK]   py_compile — {len(files)} ملفاً")
else:
    print("  [FAIL] py_compile:")
    print((r.stderr or "").strip()[:600])
    failed.append("py_compile")

for t in TESTS:
    p = BASE / "tests" / t
    if not p.exists():
        print(f"  [SKIP] {t} (غير موجود)")
        continue
    r = subprocess.run([PY, str(p)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    last = ""
    for line in reversed((r.stdout or "").strip().splitlines()):
        if "RESULT" in line:
            last = line.strip(); break
    print(f"  [{'OK' if r.returncode == 0 else 'FAIL'}]{'  ' if r.returncode == 0 else ''} {t} — {last}")
    if r.returncode != 0:
        failed.append(t)
        tail = (r.stdout or "").strip().splitlines()[-6:]
        for ln in tail:
            print("        " + ln)

print("=" * 54)
if failed:
    print("  GATE FAILED:", ", ".join(failed))
    sys.exit(1)
print("  GATE PASSED — النشر آمن")
sys.exit(0)
