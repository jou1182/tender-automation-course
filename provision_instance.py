# -*- coding: utf-8 -*-
"""provision_instance.py — create a FRESH, EMPTY database for a NEW company.

Reads company_profile.json for identity + engineer roster, builds a clean DB
(schema only, zero tender data), seeds company identity + engineers.

SAFE: refuses to touch the live tenders.db; refuses to overwrite an existing file.
The app's own ensure_* functions create any remaining aux tables on first launch.

Usage:
    python provision_instance.py                 # -> output/tenders_new_company.db
    python provision_instance.py output/acme.db  # custom path
"""
import os, sys, sqlite3
from pathlib import Path

BASE = Path(__file__).parent
LIVE_DB = (BASE / "output" / "tenders.db").resolve()

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else (BASE / "output" / "tenders_new_company.db")
    target = target if target.is_absolute() else (BASE / target)

    # ── SAFETY GUARDS ──
    if target.resolve() == LIVE_DB:
        print("[REFUSED]: that is the LIVE database. Choose a different path.")
        sys.exit(1)
    if target.exists():
        print(f"[REFUSED]: {target} already exists. Delete it first or pick another path.")
        sys.exit(1)
    target.parent.mkdir(parents=True, exist_ok=True)

    from company_profile import PROFILE

    print("=" * 56)
    print("  PROVISION NEW INSTANCE")
    print("=" * 56)
    print(f"  Company : {PROFILE['name_ar']} ({PROFILE['system_title']})")
    print(f"  Target  : {target}")
    print()

    # core schema via the canonical DBManager (creates + seeds default engineers)
    os.environ["DB_PATH"] = str(target)
    from db_manager import DBManager
    DBManager(target)   # _initialize_tables + _seed_engineers run here

    with sqlite3.connect(str(target)) as c:
        # app_config (identity) — inline; app also ensures this on startup
        c.execute("""CREATE TABLE IF NOT EXISTS app_config (
            key TEXT PRIMARY KEY, value TEXT DEFAULT '',
            updated_at TEXT DEFAULT (datetime('now')))""")
        identity = {
            "company_name_ar": PROFILE["name_ar"],
            "company_name_en": PROFILE["name_en"],
            "system_title":    PROFILE["system_title"],
            "system_subtitle": PROFILE["system_subtitle"],
            "footer_owner":    PROFILE["footer_owner"],
            "footer_url":      PROFILE["footer_url"],
            "custom_logo_b64": "",
        }
        for k, v in identity.items():
            c.execute("INSERT OR REPLACE INTO app_config(key,value) VALUES(?,?)", (k, v))

        # engineers — replace DBManager's hardcoded seed with THIS company's roster
        c.execute("DELETE FROM engineers")
        roster = PROFILE.get("engineers") or [{"name": "مهندس 1", "capacity": 5}]
        for e in roster:
            c.execute("INSERT OR IGNORE INTO engineers(name,capacity,is_active) VALUES(?,?,1)",
                      (e["name"], int(e.get("capacity", 5))))
        c.commit()

        # ── verification ──
        n_eng = c.execute("SELECT COUNT(*) FROM engineers").fetchone()[0]
        n_tenders = c.execute("SELECT COUNT(*) FROM master_tenders").fetchone()[0]
        n_pending = c.execute("SELECT COUNT(*) FROM pending_changes").fetchone()[0]
        names = [r[0] for r in c.execute("SELECT name FROM engineers ORDER BY id")]

    print("  [OK] core schema created")
    print(f"  [OK] identity seeded from profile ({PROFILE['system_title']})")
    print(f"  [OK] engineers seeded: {n_eng}  ->  {'، '.join(names)}")
    print(f"  [OK] tender data EMPTY: master_tenders={n_tenders}, pending={n_pending}")
    print()
    print("  Aux tables (results/notes/guarantees/subs) are created by the app")
    print("  automatically on first launch.")
    print()
    print("  Next: set DB_PATH to this file in the new instance's .env,")
    print("        fill the other secrets (see .env.example), then start the services.")
    print("=" * 56)

if __name__ == "__main__":
    main()
