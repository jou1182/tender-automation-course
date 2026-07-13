# -*- coding: utf-8 -*-
"""Unit tests for ai_assistant.py (extracted AI core) - runs WITHOUT openai installed."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import ai_assistant as ai

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS  " if cond else "  FAIL  ") + name + ("  [" + str(detail) + "]" if detail and not cond else ""))

# module imported cleanly; local venv has no openai -> disabled path
check("module imports standalone", True)
check("AI_ENABLED is bool", isinstance(ai.AI_ENABLED, bool))
check("AI_MODEL defined", ai.AI_MODEL == "gpt-4o")
check("AI_MAX_HISTORY sane", ai.AI_MAX_HISTORY >= 5)

# configure with a recorder
errors = []
ai.configure(db_instance=None, track_error=lambda k, d="": errors.append(k))
check("configure wires db", ai.db is None)

# history roundtrip (pure sqlite, no openai needed)
CID = 999_999_001
ai._history_clear(CID)
ai._history_save(CID, "user", "سؤال تجريبي")
ai._history_save(CID, "assistant", "رد تجريبي")
h = ai._history_load(CID)
check("history roundtrip 2 msgs", len(h) == 2, len(h))
check("history order user->assistant", h[0]["role"] == "user" and h[1]["role"] == "assistant")
ai._history_clear(CID)
check("history clear works", ai._history_load(CID) == [])

# compress: disabled/short -> unchanged
msgs = [{"role": "user", "content": "x"}] * 3
check("compress no-op when short", ai._history_compress(CID, msgs) == msgs)

# _ai_reply graceful when disabled (local machine has no openai lib)
if not ai.AI_ENABLED:
    r = ai._ai_reply(CID, "مرحبا")
    check("disabled reply returns warning", "غير مفعّل" in r or "OPENAI_API_KEY" in r, r[:60])
else:
    check("AI enabled on this machine (skip disabled-path test)", True)

# live context with db=None fails gracefully (returns "")
check("live context graceful without db", ai._ai_live_context() == "")

# knowledge loader returns str
check("knowledge loader returns str", isinstance(ai._ai_load_knowledge(), str))

print("\n" + "=" * 50)
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} passed")
sys.exit(1 if FAIL else 0)