# -*- coding: utf-8 -*-
"""new_tenant.py — أنشئ نسخة معزولة كاملة لعميل جديد (نموذج "نسخ معزولة").

كل عميل يحصل على: مجلد مستقل + قاعدة بيانات فارغة + ملفَي systemd جاهزين
للنشر + منفذ محجوز له وحده. لا يلمس هذا السكريبت نظام الرواف الحي إطلاقاً —
عمليات ملفات محلية فقط، بلا SSH وبلا تشغيل أي خدمة.

الاستخدام:
    python new_tenant.py --name "شركة النور" --dir "D:/clients/alnoor"

الخطوات التالية بعد التشغيل موثّقة في نهاية المخرجات وفي SETUP.md.
"""
import argparse, json, re, shutil, sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
REGISTRY = BASE / "tenants_registry.json"

# نفس قائمة الملفات الجوهرية المستخدمة في sync_server_to_local.py —
# مصدر واحد للحقيقة حول "ما الذي يُشكّل تطبيقاً كاملاً".
CORE_FILES = [
    "web_dashboard.py", "bot_daemon.py", "engine_core.py", "db_manager.py",
    "security_vault.py", "reverse_sync_to_sql.py", "server_autonomous_sync.py",
    "export_in_progress.py", "health_check.py", "chat_handler.py", "pdf_report.py",
    "admin_templates.py", "dashboard_templates.py", "tts_text.py", "ai_assistant.py",
    "bp_engineer.py", "analytics_engine.py", "provision_instance.py",
    "portal_adapter.py", "company_profile.py", "requirements.txt", "SETUP.md",
]
# ملفات تُنسخ كقوالب (placeholders) لا كنسخة الرواف الفعلية
TEMPLATE_ONLY = [".env.example"]


def _slug(name: str) -> str:
    """اسم صالح لوحدات systemd والمسارات: أحرف/أرقام/شرطات فقط."""
    s = re.sub(r"[^\w\-]+", "-", name.strip(), flags=re.UNICODE).strip("-")
    return s.lower() or "tenant"


def _load_registry():
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {"reserved_ports": [5050], "tenants": []}


def _next_port(reg) -> int:
    used = set(reg.get("reserved_ports", [])) | {t["port"] for t in reg["tenants"]}
    p = 5051
    while p in used:
        p += 1
    return p


def _systemd_unit(kind: str, slug: str, target_dir: Path, python_exe: str) -> str:
    if kind == "bot":
        exec_start = f"{target_dir}/start_bot.sh"
    else:
        exec_start = f"{python_exe} {target_dir}/web_dashboard.py"
    return f"""[Unit]
Description={slug}-{kind}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=CHANGE_ME
WorkingDirectory={target_dir}
{"EnvironmentFile=" + str(target_dir) + "/.env" if kind == "dashboard" else ""}
ExecStart={exec_start}
Restart=on-failure
RestartSec={"15" if kind == "bot" else "10"}
StandardOutput=append:{target_dir}/logs/{kind}_systemd.log
StandardError=append:{target_dir}/logs/{kind}_systemd.log

[Install]
WantedBy=multi-user.target
"""


def main():
    ap = argparse.ArgumentParser(description="أنشئ نسخة معزولة لعميل جديد")
    ap.add_argument("--name", required=True, help="اسم الشركة (عربي أو إنجليزي)")
    ap.add_argument("--dir", required=True, help="مسار المجلد الجديد (يجب ألا يكون موجوداً)")
    args = ap.parse_args()

    target = Path(args.dir)
    slug = _slug(args.name)

    # ── حواجز الأمان ──
    if target.resolve() == BASE.resolve():
        print("[REFUSED] لا يمكن أن يكون مسار المستأجر الجديد هو مجلد النظام الحالي.")
        sys.exit(1)
    if target.exists() and any(target.iterdir()):
        print(f"[REFUSED] المجلد {target} موجود وغير فارغ. اختر مساراً آخر.")
        sys.exit(1)

    reg = _load_registry()
    if any(t["slug"] == slug for t in reg["tenants"]):
        print(f"[REFUSED] يوجد مستأجر مسجّل بنفس المعرّف '{slug}' مسبقاً في tenants_registry.json")
        sys.exit(1)

    port = _next_port(reg)
    target.mkdir(parents=True, exist_ok=True)
    (target / "output").mkdir(exist_ok=True)
    (target / "logs").mkdir(exist_ok=True)

    print("=" * 56)
    print("  إنشاء نسخة معزولة جديدة")
    print("=" * 56)
    print(f"  الاسم    : {args.name}")
    print(f"  المعرّف  : {slug}")
    print(f"  المجلد   : {target}")
    print(f"  المنفذ   : {port}")
    print()

    # ── نسخ الملفات الجوهرية ──
    copied, missing = 0, []
    for f in CORE_FILES:
        src = BASE / f
        if src.exists():
            shutil.copy2(src, target / f)
            copied += 1
        else:
            missing.append(f)
    print(f"  [OK] نُسخ {copied}/{len(CORE_FILES)} ملفاً جوهرياً")
    if missing:
        print(f"  [!] ملفات غير موجودة محلياً (تخطّيها): {', '.join(missing)}")

    for f in TEMPLATE_ONLY:
        src = BASE / f
        if src.exists():
            shutil.copy2(src, target / f)
    print(f"  [OK] .env.example نُسخ (يحتاج تعديل يدوي قبل التشغيل)")

    # ── ملف هوية جديد فارغ القيم الحساسة (لا بيانات الرواف) ──
    fresh_profile = {
        "_comment": "ملف هوية هذا المستأجر — عدّله بالكامل قبل أي تشغيل حقيقي.",
        "name_ar": args.name, "name_en": args.name.upper(),
        "short_ar": args.name, "system_title": f"نظام {args.name}",
        "system_subtitle": "لوحة متابعة المنافسات",
        "team_ar": "فريق العروض الفنية", "department_ar": "قسم العروض الفنية",
        "portal_url": "https://ضع-رابط-منصة-العميل",
        "portal_export_path": "/", "portal_cookie_domain": "",
        "footer_owner": "", "footer_url": "",
        "ai_scope_ar": "المناقصات الحكومية ومنصة العميل",
        "theme_bg": "#b88800", "theme_card": "#fffde8", "theme_hover": "#fdf5c0",
        "theme_head": "#f5e870", "theme_primary": "#8a4800",
        "theme_primary_l": "#b86a00", "theme_primary_d": "#5e2e00",
        "engineers": [{"name": "مهندس 1", "capacity": 5}],
    }
    (target / "company_profile.json").write_text(
        json.dumps(fresh_profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  [OK] company_profile.json فارغ القيم أُنشئ (لا بيانات الرواف)")

    # ── قوالب systemd (نصوص محلية فقط — لا نشر تلقائي) ──
    py_exe = f"{target}/venv/bin/python3.12"
    (target / f"{slug}-bot.service").write_text(_systemd_unit("bot", slug, target, py_exe), encoding="utf-8")
    (target / f"{slug}-dashboard.service").write_text(_systemd_unit("dashboard", slug, target, py_exe), encoding="utf-8")
    print(f"  [OK] قوالب systemd: {slug}-bot.service / {slug}-dashboard.service")

    # ── تسجيل في السجل المركزي ──
    reg["tenants"].append({
        "slug": slug, "name": args.name, "dir": str(target),
        "port": port, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "provisioned_not_deployed",
    })
    REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] سُجّل في tenants_registry.json (المنفذ {port} محجوز الآن)")

    print()
    print("  الخطوات التالية (يدوية بقصد — راجع SETUP.md):")
    print(f"    1. عدّل {target}/company_profile.json بهوية العميل الفعلية")
    print(f"    2. cp {target}/.env.example {target}/.env  ثم املأ الأسرار (DASHBOARD_PORT={port})")
    print(f"    3. cd {target} && python -m venv venv && venv\\Scripts\\pip install -r requirements.txt")
    print(f"    4. python provision_instance.py   (يبني قاعدة بيانات فارغة داخل هذا المجلد)")
    print(f"    5. انشر ملفَي systemd المولَّدين على السيرفر المستهدف (عدّل User= أولاً)")
    print("=" * 56)


if __name__ == "__main__":
    main()
