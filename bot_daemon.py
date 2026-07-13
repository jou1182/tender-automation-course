import sys
import time
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import schedule
import os
import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, UTC
from dotenv import load_dotenv
from db_manager import DBManager, DB_PATH
from security_vault import decrypt_val
try:
    from pdf_report import send_monthly_report as _send_pdf
    PDF_OK = True
except ImportError:
    PDF_OK = False
try:
    from openai import OpenAI as _OpenAIClient
    _OPENAI_IMPORT_OK = True
except ImportError:
    _OPENAI_IMPORT_OK = False

# ============================================================
# 1. LOAD SECURE CONFIGURATION
# ============================================================
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

TELEGRAM_TOKEN = decrypt_val(os.getenv("TELEGRAM_TOKEN"))
CHAT_ID = os.getenv("CHAT_ID")
# Optional but highly recommended: your personal Telegram User ID
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_MINUTES", 5))
ALLOW_AUTONOMOUS_LOGIN = os.getenv("ALLOW_AUTONOMOUS_LOGIN", "0").strip().lower() in {"1", "true", "yes", "on"}
NO_VNC_URL = os.getenv("NO_VNC_URL", "http://127.0.0.1:6080/vnc.html")
UPTIMEROBOT_URL = os.getenv("UPTIMEROBOT_HEARTBEAT_URL", "")

# ── OpenAI / AI Chat ──────────────────────────────────────────
# AI_MODEL: moved to ai_assistant.py
WHISPER_MODEL   = "whisper-1"
# AI_MAX_HISTORY: moved to ai_assistant.py

# ── Whisper: قاموس المصطلحات المتخصصة ─────────────────────────
# يُمرَّر لـ Whisper كـ prompt حتى يتعرف على مصطلحات المجال
# هذا يرفع دقة التفريغ بشكل كبير للأسماء والمصطلحات المتخصصة
WHISPER_DOMAIN_PROMPT = (
    "المناقصات الحكومية السعودية، منصة الرواف، شركة الرواف، "
    "العروض الفنية، الضمان الابتدائي، تاريخ التقديم، كراسة الشروط، "
    "الترسية، طرح المناقصة، العطاء، الجهة المالكة، المقاول، الاستشاري، "
    "أمانة الرياض، أمانة جدة، أمانة مكة، وزارة النقل، وزارة الإسكان، "
    "وزارة الشؤون البلدية، هيئة تطوير المنطقة، أرامكو، سابك، "
    "المهندس المعتمد، التصنيف، الدرجة الأولى، الثانية، الثالثة، "
    "مناقصة، منافسة، مشروع، طرق، جسور، مباني، كهرباء، ميكانيكا، "
    "موارد بشرية، رقم المنافسة، الحالة، نشط، مغلق، مُرسى، "
    # ── كلمات عامية مصرية لتحسين دقة Whisper ────────────────
    "دلوقتي، بعدين، لقيت، مش، تمام، كمان، بس، يعني، إيه، طب، "
    "اتنين، تلاتة، أربعة، خمسة، ستة، سبعة، تمانية، تسعة، عشرة، "
    "حداشر، اتناشر، عشرين، تلاتين، مية، ميتين، ألفين"
)

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise RuntimeError("CRITICAL: TELEGRAM_TOKEN or CHAT_ID missing from .env file!")

# ============================================================
# 2. PROFESSIONAL LOGGING SYSTEM (Captures ALL modules)
# ============================================================
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_fmt = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s - %(message)s')

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_fmt)

# File Handler (daily rotation, 30 days retention)
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=LOG_DIR / "bot.log",
    when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_fmt)

# KEY FIX: Configure ROOT logger so ALL modules are captured
# Previously only "BotDaemon" logger had handlers, causing EngineCore
# and DB_Manager errors to be silently swallowed!
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger("BotDaemon")

# Suppress noisy libraries — WARNING kept for telebot so handler exceptions surface
telebot.logger.setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("WDM").setLevel(logging.WARNING)

# ============================================================
# 3. INITIALIZE BOT & DATABASE
# ============================================================
bot = telebot.TeleBot(TELEGRAM_TOKEN)
db = DBManager()

# ============================================================
# JOB OVERLAP GUARD
# Prevents job_check_platform from running concurrently with itself
# if a previous cycle takes longer than CHECK_INTERVAL minutes.
# Without this, the scheduler fires a second job while the first
# is still scraping -> duplicate Telegram messages.
# ============================================================
_job_lock    = threading.Lock()
_backup_lock = threading.Lock()   # Prevents duplicate backup sends on concurrent restarts

# ── نظام التنبيه التلقائي عند الأعطال الصامتة ─────────────────
# إذا تكرر نفس الخطأ 3 مرات في 10 دقائق → رسالة تنبيه فورية للمسؤول
_error_tracker: dict = {}          # error_key → [timestamp, timestamp, ...]
_ERROR_ALERT_THRESHOLD  = 3        # عدد التكرارات قبل التنبيه
_ERROR_ALERT_WINDOW_SEC = 600      # نافزة الوقت (10 دقائق)
_last_alert_sent: dict  = {}       # error_key → last alert timestamp (لمنع الإزعاج)
_ALERT_COOLDOWN_SEC     = 1800     # لا ترسل نفس التنبيه مرتين خلال 30 دقيقة

def _track_error(error_key: str, detail: str = ""):
    """
    سجّل خطأً وأرسل تنبيهاً للمسؤول إذا تكرر كثيراً.
    error_key: وصف مختصر للخطأ (مثل 'OpenAI API' أو 'Whisper')
    detail: تفاصيل إضافية للرسالة
    """
    now = time.time()
    timestamps = _error_tracker.setdefault(error_key, [])

    # احتفظ فقط بالأخطاء ضمن النافذة الزمنية
    timestamps[:] = [t for t in timestamps if now - t < _ERROR_ALERT_WINDOW_SEC]
    timestamps.append(now)

    if len(timestamps) < _ERROR_ALERT_THRESHOLD:
        return  # لم يصل للحد بعد

    # تحقق من cooldown — لا تُزعج بنفس التنبيه كل دقيقة
    last_sent = _last_alert_sent.get(error_key, 0)
    if now - last_sent < _ALERT_COOLDOWN_SEC:
        return

    _last_alert_sent[error_key] = now

    # بناء رسالة التنبيه
    count    = len(timestamps)
    since    = int((now - timestamps[0]) / 60)
    msg = (
        f"🚨 *تنبيه — عطل متكرر*\n\n"
        f"*النوع:* `{error_key}`\n"
        f"*التكرار:* {count} مرة خلال {since} دقيقة\n"
    )
    if detail:
        msg += f"*التفاصيل:* `{detail[:200]}`\n"
    msg += f"\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        logger.warning(f"ALERT SENT: {error_key} × {count} in {since}min")
    except Exception as e:
        logger.error(f"Failed to send error alert: {e}")
STATE_FILE = BASE_DIR / "output" / "bot_state.json"
SESSION_ALERT_FILE = BASE_DIR / "output" / "session_alert_sent.flag"
BACKUP_ALERT_FILE = BASE_DIR / "output" / "backup_alert_sent.flag"

def utc_now_iso():
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("Could not read bot_state.json; starting with empty runtime state.")
        return {}

def save_state(**updates):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = load_state()
    state.update(updates)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state

def is_paused():
    return bool(load_state().get("paused", False))

def fmt_ts(ts):
    return ts or "غير متوفر"

def file_status(path):
    path = Path(path)
    if not path.exists():
        return "غير موجود"
    age_minutes = int((time.time() - path.stat().st_mtime) / 60)
    size_kb = max(1, int(path.stat().st_size / 1024))
    return f"موجود، الحجم {size_kb}KB، آخر تعديل منذ {age_minutes} دقيقة"

def build_health_report():
    state = load_state()
    stats = db.get_system_stats() or {}
    export_status = "غير متوفر"
    status_path = BASE_DIR / "output" / "export_status.txt"
    if status_path.exists():
        export_status = status_path.read_text(encoding="utf-8", errors="ignore").strip() or "فارغ"

    session_ok = "تعمل" if export_status == "success" else "تحتاج فحص"
    paused_text = "متوقفة مؤقتاً" if state.get("paused") else "تعمل"
    auto_login_text = "مفعّل" if ALLOW_AUTONOMOUS_LOGIN else "مغلق لحماية MFA"

    return (
        "🩺 *فحص صحة نظام الرواف*\n"
        "━━━━━━━━━━━━━━\n"
        f"الحالة: *{paused_text}*\n"
        f"آخر فحص: `{fmt_ts(state.get('last_check_at'))}`\n"
        f"آخر نجاح: `{fmt_ts(state.get('last_success_at'))}`\n"
        f"آخر نتيجة: `{state.get('last_result', 'غير متوفر')}`\n\n"
        f"آخر نسخة احتياطية: `{fmt_ts(state.get('last_backup_at'))}`\n"
        f"نتيجة النسخ: `{state.get('last_backup_result', 'غير متوفر')}`\n\n"
        f"المنافسات النشطة: *{stats.get('active_count', '؟')}*\n"
        f"المعلقات: *{stats.get('pending_count', '؟')}*\n"
        f"المغلقة: *{stats.get('closed_count', '؟')}*\n\n"
        f"جلسة الرواف: *{session_ok}* (`{export_status}`)\n"
        f"الدخول التلقائي لمايكروسوفت: *{auto_login_text}*\n"
        f"ملف الكوكيز: {file_status(BASE_DIR / 'output' / 'portal_cookies.json')}\n"
        f"قاعدة البيانات: {file_status(DB_PATH)}\n"
        f"ملف الماستر: {file_status(BASE_DIR / 'output' / 'Master_Tenders.xlsx')}\n"
    )

def send_session_expired_alert():
    # Re-send alert every 24h so user is reminded if they miss the first one
    RESEND_HOURS = 24
    if SESSION_ALERT_FILE.exists():
        try:
            age_hours = (time.time() - SESSION_ALERT_FILE.stat().st_mtime) / 3600
            if age_hours < RESEND_HOURS:
                return
        except Exception:
            pass  # If we can't check age, re-send to be safe

    err_msg = (
        "⚠️ *جلسة موقع الرواف تحتاج تجديد يدوي*\n\n"
        "وصل أمر الفحص، لكن السيرفر لا يملك جلسة دخول صالحة حالياً لمنصة الرواف.\n\n"
        "من جهازك شغّل:\n"
        "`D:\\in_progress_tender\\V4_Super_System\\AlRawaf_Update_Session.bat`\n\n"
        "بعد اكتمال التحديث أرسل /news مرة أخرى."
    )
    bot.send_message(CHAT_ID, err_msg, parse_mode="Markdown")
    SESSION_ALERT_FILE.write_text(utc_now_iso(), encoding="utf-8")

def send_backup_failure_alert(error):
    today = time.strftime("%Y-%m-%d")
    if BACKUP_ALERT_FILE.exists() and BACKUP_ALERT_FILE.read_text(encoding="utf-8").strip() == today:
        return
    bot.send_message(
        CHAT_ID,
        "⚠️ *فشل إرسال النسخة الاحتياطية اليومية*\n\n"
        f"التاريخ: `{today}`\n"
        f"السبب: `{str(error)[:500]}`\n\n"
        "يمكن تنفيذ /backup يدوياً بعد فحص /health.",
        parse_mode="Markdown"
    )
    BACKUP_ALERT_FILE.write_text(today, encoding="utf-8")

def ping_uptimerobot():
    """Send heartbeat ping to UptimeRobot. If pings stop, UptimeRobot alerts the admin."""
    if not UPTIMEROBOT_URL:
        return
    try:
        import requests as _req
        _req.get(UPTIMEROBOT_URL, timeout=10)
        logger.debug("UptimeRobot heartbeat sent.")
    except Exception as e:
        logger.warning(f"UptimeRobot ping failed (non-critical): {e}")

def job_cookie_reminder():
    """
    Daily check: if portal cookies file is 6+ days old, remind admin to renew.
    Fires daily but only sends message when threshold is crossed.
    """
    cookies_file = BASE_DIR / "output" / "portal_cookies.json"
    if not cookies_file.exists():
        return
    age_days = (time.time() - cookies_file.stat().st_mtime) / 86400
    if age_days < 6:
        return
    msg = (
        "🔑 *تذكير: تجديد جلسة موقع الرواف*\n"
        "━━━━━━━━━━━━━━\n"
        f"آخر تحديث للجلسة كان منذ *{int(age_days)} أيام*.\n\n"
        "للحفاظ على استمرارية المراقبة، شغّل من جهازك:\n"
        "`AlRawaf_Update_Session.bat`\n\n"
        "_(يُنصح بالتجديد قبل أن تصل إلى 7 أيام)_"
    )
    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    logger.info(f"Cookie renewal reminder sent (age: {age_days:.1f} days).")

def job_monthly_report():
    """Fires on 1st of each month at 09:00 — generates and sends PDF report."""
    if not PDF_OK:
        logger.warning("job_monthly_report: pdf_report module not available, skipping.")
        return
    logger.info("Sending monthly PDF report...")
    try:
        _send_pdf(bot, CHAT_ID)
        logger.info("Monthly PDF report sent successfully.")
    except Exception as e:
        logger.error(f"Monthly report failed: {e}")
        bot.send_message(CHAT_ID, f"⚠️ فشل إرسال التقرير الشهري: `{str(e)[:200]}`", parse_mode="Markdown")

def read_last_log_lines(limit=50):
    log_path = LOG_DIR / "bot.log"
    if not log_path.exists():
        return "ملف السجل غير موجود بعد."
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-limit:]) or "ملف السجل فارغ."

# ============================================================
# 4. TELEGRAM MESSAGE DELIVERY
# ============================================================
def get_progress_bar(pct):
    filled = int(pct / 10)
    return "▓" * filled + "░" * (10 - filled)

def send_approval_message(change):
    """Sends the interactive approval message to the Manager."""
    # ── استخراج بيانات الترشيح الذكي من details_json ──────────────────
    suggestion  = {}
    owner_name  = ""
    btype_name  = ""
    try:
        details = json.loads(change['details_json'] or "{}")
        suggestion  = details.get('_smart_suggestion', {})
        owner_name  = str(details.get('المالك', '') or details.get('owner', '')).strip()
        btype_name  = str(details.get('نوع الأعمال', '') or details.get('business_type', '')).strip()
    except Exception:
        pass

    eng_name  = suggestion.get('name') or change['suggested_engineer']
    score     = suggestion.get('score', 0)
    reason    = suggestion.get('reason', '')
    breakdown = suggestion.get('breakdown', '')

    # ── شريط حمل المهندس المقترح ──────────────────────────────────────
    eng_load = 50
    try:
        for e in db.get_all_engineers_with_load():
            if e['name'] == eng_name:
                eng_load = e['load_pct']
                break
    except Exception:
        pass
    bar = get_progress_bar(eng_load)

    action_str  = "مناقصة جديدة" if change['change_type'] == 'NEW' else "تعديل في تاريخ الإغلاق"
    score_stars = "⭐" * min(int(score // 20), 5)

    # ── بناء رسالة تيليجرام ───────────────────────────────────────────
    meta_line = ""
    if owner_name and owner_name not in ("N/A", "غير محدد", "nan"):
        meta_line += f"🏢 *الجهة:* {owner_name}\n"
    if btype_name and btype_name not in ("N/A", "غير محدد", "nan"):
        meta_line += f"🏗️ *النطاق:* {btype_name}\n"

    msg = (
        f"🚨 *اكتشاف {action_str}!*\n\n"
        f"📌 *الاسم:* {change['title']}\n"
        f"⏱️ *تاريخ الإغلاق:* {change['submission_date']}\n"
        f"{meta_line}"
        f"\n🤖 *اقتراح الذكاء الاصطناعي:*\n"
        f"المهندس *{eng_name}* هو الأنسب {score_stars}\n"
        f"⚖️ الحمل: [{bar}] {eng_load}%\n"
        f"💡 _السبب: {reason}_\n"
    )
    if breakdown:
        msg += f"\n{breakdown}\n"

    markup = InlineKeyboardMarkup(row_width=1)
    btn_approve = InlineKeyboardButton(
        f"✅ اعتماد لـ ({eng_name}) وتحديث الماستر",
        callback_data=f"approve_{change['id']}_{eng_name}"
    )
    btn_change_eng = InlineKeyboardButton(
        "🔄 أفضّل إسنادها لمهندس آخر",
        callback_data=f"changeeng_{change['id']}"
    )
    btn_reject = InlineKeyboardButton(
        "❌ تجاهل وحذف من المعلقات",
        callback_data=f"reject_{change['id']}"
    )
    markup.add(btn_approve, btn_change_eng, btn_reject)

    import requests
    payload = {
        'chat_id': CHAT_ID,
        'text': msg,
        'parse_mode': 'Markdown',
        'reply_markup': markup.to_json()
    }
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json=payload, timeout=15
        )
        logger.info(f"Delivered approval card for '{change['title']}' via fresh TCP connection.")
    except Exception as e:
        logger.error(f"Telegram delivery failed: {e}")

def is_auto_approve() -> bool:
    """وضع المزامنة الآلية — يُبدَّل بأمر /automode on|off."""
    return bool(load_state().get("auto_approve", False))

def _auto_engineer_for(change) -> str:
    """اختيار المهندس للاعتماد الآلي: مهندس المنافسة الحالي إن وُجدت،
    وإلا المقترح الذكي المخزن، وإلا اقتراح موازنة الأحمال."""
    try:
        with db._get_connection() as conn:
            r = conn.execute(
                "SELECT assigned_engineer FROM master_tenders WHERE title = ?",
                (change['title'],)
            ).fetchone()
        if r and r[0]:
            return r[0]
    except Exception:
        pass
    try:
        if change['suggested_engineer']:
            return change['suggested_engineer']
    except Exception:
        pass
    return db.suggest_best_engineer(change['title'])

def notify_pending_changes():
    """Notify manager for fresh pending approvals and mark them as notified."""
    notified_count = 0
    pending_changes = db.get_pending_changes()
    for change in pending_changes:
        try:
            # PRE-MARK as NOTIFIED atomically before sending to prevent duplicate sends.
            with db._get_connection() as conn:
                affected = conn.execute(
                    "UPDATE pending_changes SET status = 'NOTIFIED' WHERE id = ? AND status = 'PENDING_APPROVAL'",
                    (change['id'],)
                ).rowcount
                conn.commit()

            if affected == 0:
                logger.warning(f"Skipping duplicate send for pending_id={change['id']} (already claimed).")
                continue

            if change['change_type'] == 'CLOSED':
                bot.send_message(
                    CHAT_ID,
                    f"\u2139\ufe0f *للعلم:* تم إغلاق المناقصة بشكل آلي وإزالتها من الموقع:\n*{change['title']}*",
                    parse_mode="Markdown"
                )
                # الإغلاق مُطبَّق آلياً في الماستر — أكمل حالة السجل حتى لا يتضخم عداد "بانتظار الاعتماد"
                with db._get_connection() as conn:
                    conn.execute("UPDATE pending_changes SET status = 'APPROVED' WHERE id = ?", (change['id'],))
                    conn.commit()
            elif is_auto_approve():
                def _dmy(s):
                    p = str(s or '')[:10].split('-')
                    return f"{p[2]}/{p[1]}/{p[0]}" if len(p) == 3 and p[0].isdigit() else (str(s or '—')[:10])
                is_new = change['change_type'] in ('NEW', 'NEW_TENDER')
                old_date = ""
                if not is_new:
                    # التاريخ القديم يُقرأ قبل الاعتماد (الاعتماد سيستبدله)
                    try:
                        with db._get_connection() as conn:
                            r = conn.execute("SELECT submission_date FROM master_tenders WHERE title = ?",
                                             (change['title'],)).fetchone()
                        old_date = str(r[0])[:10] if r and r[0] else ""
                    except Exception:
                        pass
                eng = _auto_engineer_for(change)
                db.approve_change(change['id'], eng)
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("🔁 تغيير المهندس", callback_data=f"aem_{change['id']}"))
                new_date = _dmy(change['submission_date'])
                if is_new:
                    msg = (f"🤖 *مزامنة آلية:* تم اعتماد منافسة جديدة:\n*{change['title']}*\n"
                           f"تاريخ التقديم: {new_date}\nالمهندس: *{eng}*")
                else:
                    msg = (f"🤖 *مزامنة آلية:* تم اعتماد تحديث تاريخ:\n*{change['title']}*\n"
                           f"تاريخ التقديم القديم: {_dmy(old_date)}\n"
                           f"تاريخ التقديم الجديد: {new_date}\nالمهندس: *{eng}*")
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown", reply_markup=markup)
                if is_new:
                    _notify_engineer(eng, "📌 أُسندت إليك منافسة جديدة:" + chr(10)
                                     + str(change['title']) + chr(10) + "الإغلاق: " + new_date)
            else:
                send_approval_message(change)
            notified_count += 1
            time.sleep(1)
        except Exception as e:
            logger.error(f"Failed to send Telegram notification, will retry: {e}")
            # Revert to PENDING_APPROVAL so it retries next cycle.
            try:
                with db._get_connection() as conn:
                    conn.execute("UPDATE pending_changes SET status = 'PENDING_APPROVAL' WHERE id = ?", (change['id'],))
                    conn.commit()
            except Exception as e2:
                logger.error(f"CRITICAL: Could not revert status for pending_id={change['id']}: {e2}")
    return notified_count

def build_news_clear_message():
    return (
        "✅ لا توجد أي منافسات جديدة أو منافسات تم تغيير تاريخ التقديم حتى هذه اللحظة.\n\n"
        "اطمئن، منصة الرواف وقاعدة البيانات متطابقتان الآن.\n\n"
        "💚 صنع بكل حب من فريق العروض الفنية بشركة الرواف"
    )

def run_manual_list_report(chat_id):
    if not _job_lock.acquire(blocking=False):
        bot.send_message(chat_id, "⏳ يوجد فحص يعمل الآن بالفعل. جرّب /list بعد دقيقة.")
        return

    try:
        logger.info(f"Manual /list command received from chat_id={chat_id}")
        import pandas as pd
        import export_in_progress

        ok = export_in_progress.main()
        if not ok:
            bot.send_message(
                chat_id,
                "⚠️ لم أتمكن من تحديث قائمة منصة الرواف الآن. غالباً الجلسة تحتاج تحديث عبر `AlRawaf_Update_Session.bat`.",
                parse_mode="Markdown"
            )
            return

        export_path = BASE_DIR / "output" / "in_progress_tenders.xlsx"
        portal_count = len(pd.read_excel(export_path)) if export_path.exists() else 0

        with db._get_connection() as conn:
            db_count = conn.execute(
                "SELECT COUNT(*) FROM master_tenders WHERE status NOT IN ('CLOSED', 'REJECTED')"
            ).fetchone()[0]
            pending_count = conn.execute(
                "SELECT COUNT(*) FROM pending_changes WHERE status IN ('PENDING_APPROVAL', 'NOTIFIED')"
            ).fetchone()[0]

        match_text = "✅ متطابقان" if portal_count == db_count else "⚠️ يوجد فرق يحتاج مراجعة"
        msg = (
            "📋 *قائمة منافسات الرواف الحالية*\n"
            "━━━━━━━━━━━━━━\n"
            f"منصة الرواف: *{portal_count}* منافسة\n"
            f"قاعدة البيانات: *{db_count}* منافسة نشطة\n"
            f"الحالة: *{match_text}*\n"
            f"طلبات بانتظار الاعتماد: *{pending_count}*\n\n"
            f"آخر تحديث: `{utc_now_iso()}`"
        )
        bot.send_message(chat_id, msg, parse_mode="Markdown")
    except Exception as e:
        logger.exception(f"Manual /list report failed: {e}")
        bot.send_message(chat_id, f"❌ حدث خطأ أثناء تنفيذ /list:\n{e}")
    finally:
        _job_lock.release()

def send_open_pending_cards(chat_id):
    logger.info(f"Manual /pending command received from chat_id={chat_id}")
    with db._get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM pending_changes WHERE status IN ('PENDING_APPROVAL', 'NOTIFIED') ORDER BY created_at ASC"
        ).fetchall()

    if not rows:
        bot.send_message(chat_id, "✅ لا توجد طلبات بانتظار الاعتماد حالياً.")
        return

    bot.send_message(chat_id, f"🟡 يوجد ({len(rows)}) طلب بانتظار الاعتماد. سأعرضها الآن:")
    for change in rows:
        if change['change_type'] == 'CLOSED':
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("❌ إزالة من المعلقات", callback_data=f"reject_{change['id']}"))
            bot.send_message(
                chat_id,
                f"ℹ️ *طلب إغلاق معلق*\n\n*{change['title']}*",
                parse_mode="Markdown",
                reply_markup=markup
            )
        else:
            send_approval_message(change)
        time.sleep(1)

def send_tenders_detail_table(chat_id):
    logger.info(f"Manual detailed list command received from chat_id={chat_id}")
    try:
        import pandas as pd

        with db._get_connection() as conn:
            df = pd.read_sql(
                """
                SELECT title, submission_date, assigned_engineer
                FROM master_tenders
                WHERE status NOT IN ('CLOSED', 'REJECTED')
                ORDER BY created_at ASC
                """,
                conn
            )

        if df.empty:
            bot.send_message(chat_id, "لا توجد منافسات نشطة حالياً في قاعدة البيانات.")
            return

        def clean_date(value):
            try:
                if pd.isna(value) or str(value).strip().lower() in ("", "nan", "none", "n/a"):
                    return "غير محدد"
                return pd.to_datetime(value).strftime("%Y-%m-%d")
            except Exception:
                return str(value)

        report_df = pd.DataFrame({
            "مسلسل": range(1, len(df) + 1),
            "اسم المنافسة": df["title"].fillna(""),
            "تاريخ التقديم": df["submission_date"].apply(clean_date),
            "المهندس المسؤول": df["assigned_engineer"].fillna("غير محدد"),
        })

        report_path = BASE_DIR / "output" / "قائمة_المنافسات_الحالية.xlsx"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
            report_df.to_excel(writer, sheet_name="المنافسات الحالية", index=False)

        with open(report_path, "rb") as report_file:
            bot.send_document(
                chat_id,
                report_file,
                caption=(
                    f"📄 قائمة المنافسات الحالية\n"
                    f"العدد: {len(report_df)} منافسة\n"
                    "الأعمدة: مسلسل، اسم المنافسة، تاريخ التقديم، المهندس المسؤول"
                )
            )
    except Exception as e:
        logger.exception(f"Detailed tenders list failed: {e}")
        bot.send_message(chat_id, f"❌ حدث خطأ أثناء تجهيز جدول المنافسات:\n{e}")

def run_manual_news_check(chat_id):
    if not _job_lock.acquire(blocking=False):
        bot.send_message(chat_id, "⏳ يوجد فحص يعمل الآن بالفعل. جرّب /news بعد دقيقة.")
        return

    try:
        save_state(last_manual_news_at=utc_now_iso(), last_manual_news_result="running")
        logger.info(f"{'='*20} Manual /news Check Started {'='*20}")

        try:
            import reverse_sync_to_sql
            reverse_sync_to_sql.reverse_sync()
            logger.info("Manual /news Excel -> SQL sync completed successfully.")
        except Exception as e:
            logger.error(f"Manual /news Excel Sync failed: {e}")

        import engine_core
        staged_count = engine_core.find_and_stage_changes()

        if staged_count == -1:
            send_session_expired_alert()
            save_state(last_manual_news_result="session_failed")
            bot.send_message(
                chat_id,
                "⚠️ لم أتمكن من فحص منصة الرواف الآن لأن الجلسة تحتاج تجديد. راجع /health للتفاصيل.",
                parse_mode="Markdown"
            )
            return

        if SESSION_ALERT_FILE.exists():
            SESSION_ALERT_FILE.unlink()

        notified_count = notify_pending_changes()
        save_state(last_manual_news_result=f"ok:{staged_count}", last_success_at=utc_now_iso())

        if staged_count > 0 or notified_count > 0:
            bot.send_message(
                chat_id,
                f"🚨 تم فحص منصة الرواف.\n\nتم العثور على ({max(staged_count, notified_count)}) تحديث يحتاج مراجعتك، وأرسلت لك تفاصيله الآن.",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(chat_id, build_news_clear_message())

        logger.info(f"{'='*20} Manual /news Check Ended {'='*20}")
    except Exception as e:
        logger.exception(f"Manual /news check failed: {e}")
        save_state(last_manual_news_result="failed")
        bot.send_message(chat_id, f"❌ حدث خطأ أثناء تنفيذ /news:\n{e}")
    finally:
        _job_lock.release()

# ============================================================
# 5. COMMAND HANDLERS
# ============================================================
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    if not is_authorized(message): return
    bot.send_message(message.chat.id, "👋 أهلاً بك في نظام الرواف لإدارة المناقصات.\n\n"
                                      "استخدم /news لفحص منصة الرواف الآن.\n"
                                      "استخدم /list لعرض عدد منافسات المنصة وقاعدة البيانات.\n"
                                      "استخدم /list_d لتحميل جدول المنافسات بالتفصيل.\n"
                                      "استخدم /pending لعرض طلبات الاعتماد العالقة.\n"
                                      "استخدم /status أو /health لفحص النظام.\n"
                                      "استخدم /stats لرؤية الإحصائيات.\n"
                                      "استخدم /backup لنقل نسخة احتياطية فورية.\n"
                                      "استخدم /report لإنشاء وإرسال تقرير PDF شهري الآن.\n"
                                      "استخدم /predict لتوقع تمديد المنافسات النشطة.\n"
                                      "استخدم /approve_all لاعتماد كل الطلبات المنتظرة دفعة واحدة.\n"
                                      "استخدم /automode للمزامنة الآلية الكاملة (on/off).\n"
                                      "استخدم /guarantees لعرض وتحديث الضمانات بالأزرار.\n"
                                      "استخدم /followup لتسجيل نتائج العروض المعلقة بضغطة.\n"
                                      "استخدم /find كلمة — بحث سريع ببطاقة إجراءات.\n"
                                      "استخدم /owner جهة — بطاقة ذاكرة الجهة المالكة.\n"
                                      "للمهندسين: راسلوا البوت خاصاً بـ /subscribe للإشعارات الشخصية.\n"
                                      "استخدم /test لتجربة إشعار آمن.\n"
                                      "استخدم /lastlog لآخر سجل تشغيل.\n"
                                      "استخدم /pause و /resume للتحكم في المزامنة.")

# ══════════════════════════════════════════════════════════
# v5.7: اشتراكات المهندسين الشخصية + بطاقة الجهة
# ══════════════════════════════════════════════════════════
def _ensure_subs_table(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS engineer_subs (
        chat_id INTEGER PRIMARY KEY,
        engineer_name TEXT NOT NULL,
        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

def _sub_of(chat_id):
    with db._get_connection() as conn:
        _ensure_subs_table(conn)
        r = conn.execute("SELECT engineer_name FROM engineer_subs WHERE chat_id=?", (chat_id,)).fetchone()
    return r[0] if r else None

def _subs_for(eng_name):
    with db._get_connection() as conn:
        _ensure_subs_table(conn)
        return [r[0] for r in conn.execute(
            "SELECT chat_id FROM engineer_subs WHERE engineer_name=?", (eng_name,)).fetchall()]

def _notify_engineer(eng_name, text):
    """إشعار خاص لمشتركي مهندس معين — أفضل جهد، لا يوقف التدفق."""
    try:
        for cid in _subs_for(eng_name):
            try:
                bot.send_message(cid, text)
            except Exception as _e:
                logger.debug(f"notify {eng_name}/{cid} failed: {_e}")
    except Exception as e:
        logger.debug(f"_notify_engineer failed: {e}")

def _personal_digest(eng_name):
    """ملخص شخصي: منافسات المهندس + مواعيدها + ضماناتها المستحقة."""
    from datetime import datetime as _dt, timedelta as _td
    today = _dt.now().date()
    with db._get_connection() as conn:
        rows = conn.execute("""
            SELECT mt.title, mt.owner, mt.submission_date,
                   COALESCE(g.status,'PENDING') gstatus, COALESCE(g.due_date,'') gdue
            FROM master_tenders mt
            LEFT JOIN tender_guarantees g ON g.tender_row_id = mt.id
            WHERE mt.assigned_engineer = ? AND mt.status NOT IN ('CLOSED','REJECTED')
            ORDER BY mt.submission_date""", (eng_name,)).fetchall()
    if not rows:
        return None
    lines = [f"👷 ملخصك اليومي يا {eng_name} — منافساتك ({len(rows)}):", ""]
    for r in rows[:12]:
        icon, dtxt = "⚪", ""
        try:
            d = _dt.strptime(str(r["submission_date"])[:10], "%Y-%m-%d").date()
            dl = (d - today).days
            icon = "🔴" if dl <= 3 else ("🟡" if dl <= 7 else "🟢")
            dtxt = f" (باقي {dl} يوم)" if dl >= 0 else " (منتهية!)"
        except Exception:
            pass
        lines.append(f"{icon} {r['title']}")
        lines.append(f"      الإغلاق: {str(r['submission_date'] or '—')[:10]}{dtxt}")
        if r["gstatus"] not in ("READY", "SUBMITTED", "NOT_REQUIRED"):
            gd = None
            if r["gdue"]:
                try: gd = _dt.strptime(r["gdue"][:10], "%Y-%m-%d").date()
                except Exception: pass
            if gd is None:
                try: gd = _dt.strptime(str(r["submission_date"])[:10], "%Y-%m-%d").date() - _td(days=5)
                except Exception: pass
            if gd is not None and (gd - today).days <= 5:
                lines.append(f"      🛡️ الضمان مستحق {gd.isoformat()} — غير جاهز بعد!")
        lines.append("")
    return chr(10).join(lines).strip()

def job_engineer_digests():
    """v5.7: ملخص صباحي خاص لكل مهندس مشترك (08:15)."""
    if is_paused():
        return
    try:
        with db._get_connection() as conn:
            _ensure_subs_table(conn)
            subs = conn.execute("SELECT chat_id, engineer_name FROM engineer_subs").fetchall()
        sent = 0
        for cid, eng in subs:
            digest = _personal_digest(eng)
            if digest:
                try:
                    bot.send_message(cid, digest)
                    sent += 1
                except Exception as e:
                    logger.debug(f"digest to {eng}/{cid} failed: {e}")
        logger.info(f"Engineer digests sent: {sent}/{len(subs)}.")
    except Exception as e:
        logger.error(f"job_engineer_digests failed: {e}")

@bot.message_handler(commands=['subscribe'])
def handle_subscribe(message):
    """اشتراك مهندس (محادثة خاصة + PIN بوابة المهندسين)."""
    if getattr(message.chat, "type", "") != "private":
        bot.send_message(message.chat.id,
                         "🔒 الاشتراك يتم في محادثة خاصة مع البوت — راسلني خاصاً بالأمر:" + chr(10) +
                         "/subscribe رقم-البوابة")
        return
    cur = _sub_of(message.chat.id)
    parts = (message.text or "").strip().split()
    pin = os.getenv("ENGINEER_PIN", "1234")
    if len(parts) < 2 or parts[1].strip() != pin:
        hint = f"(مشترك حالياً باسم: {cur})" + chr(10) if cur else ""
        bot.send_message(message.chat.id,
                         hint + "🔑 أرسل: /subscribe متبوعاً برقم بوابة المهندسين" + chr(10) +
                         "مثال: /subscribe 0000")
        return
    engineers = db.get_all_engineers()
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(*[InlineKeyboardButton(e['name'], callback_data=f"sub_{e['name']}")
                 for e in engineers])
    bot.send_message(message.chat.id, "✅ رمز صحيح — اختر اسمك:", reply_markup=markup)

@bot.message_handler(commands=['unsubscribe'])
def handle_unsubscribe(message):
    cur = _sub_of(message.chat.id)
    if not cur:
        bot.send_message(message.chat.id, "لا يوجد اشتراك مسجل لهذه المحادثة.")
        return
    with db._get_connection() as conn:
        conn.execute("DELETE FROM engineer_subs WHERE chat_id=?", (message.chat.id,))
        conn.commit()
    bot.send_message(message.chat.id, f"🚫 أُلغي اشتراك «{cur}» — لن تصلك إشعارات شخصية بعد الآن.")

@bot.message_handler(commands=['mytenders'])
def handle_mytenders(message):
    """منافساتي الآن — للمهندس المشترك."""
    eng = _sub_of(message.chat.id)
    if not eng:
        bot.send_message(message.chat.id,
                         "هذا الأمر للمهندسين المشتركين — راسلني خاصاً بـ /subscribe أولاً.")
        return
    digest = _personal_digest(eng)
    bot.send_message(message.chat.id, digest or f"✨ لا منافسات نشطة مسندة إليك حالياً يا {eng}.")

def _owner_card_text(term):
    """بطاقة ذاكرة الجهة — نفس ذكاء صفحة /owners مضغوطاً لتيليجرام."""
    import json as _json
    from datetime import datetime as _dt
    # v5.7.1: مطابقة عربية ذكية — توحيد الهمزات + تجربة الاسم بدون "ال" التعريف
    # (مثال: "الإسكان" يجب أن يجد "الشركة الوطنية للإسكان" رغم اختلاف "ال" عن "لل")
    from engine_core import normalize_arabic as _norm
    t = _norm(term).strip()
    cands = [t]
    if t.startswith("ال") and len(t) > 4:
        cands.append(t[2:])
    with db._get_connection() as conn:
        all_owners = conn.execute("""
            SELECT TRIM(owner) ow, COUNT(*) total,
                   SUM(CASE WHEN status NOT IN ('CLOSED','REJECTED') THEN 1 ELSE 0 END) active,
                   MIN(CASE WHEN status NOT IN ('CLOSED','REJECTED')
                        AND submission_date >= date('now') THEN submission_date END) next_dl
            FROM master_tenders
            WHERE owner IS NOT NULL AND TRIM(owner) != ''
              AND TRIM(LOWER(owner)) NOT IN ('n/a','nan')
            GROUP BY TRIM(owner)""").fetchall()
    matches = [r for r in all_owners if any(c and c in _norm(r["ow"]) for c in cands)]
    if not matches:
        return None
    matches.sort(key=lambda r: (-(r["active"] or 0), -(r["total"] or 0)))
    b = matches[0]
    _others = [m["ow"] for m in matches[1:4]]
    with db._get_connection() as conn:
        ow = b["ow"]
        rr = conn.execute("""
            SELECT SUM(CASE WHEN did_submit=1 THEN 1 ELSE 0 END) s,
                   SUM(CASE WHEN result='won'  THEN 1 ELSE 0 END) w,
                   SUM(CASE WHEN result='lost' THEN 1 ELSE 0 END) l
            FROM tender_results WHERE TRIM(owner)=?""", (ow,)).fetchone()
        acts = conn.execute("""
            SELECT title, submission_date FROM master_tenders
            WHERE TRIM(owner)=? AND status NOT IN ('CLOSED','REJECTED')
            ORDER BY submission_date LIMIT 3""", (ow,)).fetchall()
        ext_rows = conn.execute(
            "SELECT details_json FROM pending_changes WHERE change_type='UPDATED_DATE'").fetchall()
    OWNER_KEY = "المالك"
    ext = 0
    for e_ in ext_rows:
        try:
            if str(_json.loads(e_["details_json"] or "{}").get(OWNER_KEY, "")).strip() == ow:
                ext += 1
        except Exception:
            pass
    s = rr["s"] or 0
    w = rr["w"] or 0
    l = rr["l"] or 0
    dec = w + l
    active = b["active"] or 0
    if w and active:   cls = "🟢 عميل رابح نشط"
    elif w:            cls = "🟠 رابح — يحتاج تنشيط"
    elif active:       cls = "🔵 فرصة جارية"
    elif s:            cls = "⚪ علاقة تحتاج تنشيط"
    else:              cls = "🗂 أرشيف"
    lines = [f"🏢 *{ow}*", f"التصنيف: {cls}", ""]
    lines.append(f"📊 السجل: {b['total']} منافسة معروفة | جارية الآن: {active}")
    lines.append(f"📤 قدمنا: {s} | 🏆 فوز: {w} | ❌ خسارة: {l}"
                 + (f" | نسبة الفوز: {round(w/dec*100)}% (من {dec} معروفة)" if dec else ""))
    if ext:
        lines.append(f"🔮 سلوك التمديد: مدّدت مواعيدها {ext} مرة تاريخياً — توقع مرونة في المواعيد")
    if b["next_dl"]:
        lines.append(f"⏰ أقرب إغلاق: {str(b['next_dl'])[:10]}")
    if acts:
        lines.append("")
        lines.append("*الفرص الجارية:*")
        for a in acts:
            lines.append(f"• {a['title']}")
            lines.append(f"   يغلق {str(a['submission_date'] or '—')[:10]}")
        if active > 3:
            lines.append(f"… و{active - 3} أخرى")
    if _others:
        lines.append("")
        lines.append("🔎 جهات أخرى مطابقة: " + "، ".join(_others))
    return chr(10).join(lines)

@bot.message_handler(commands=['owner'])
def handle_owner(message):
    """v5.7: بطاقة ذاكرة الجهة المالكة."""
    if not is_authorized(message): return
    q = (message.text or "").split(maxsplit=1)
    if len(q) < 2 or not q[1].strip():
        bot.send_message(message.chat.id,
                         "الاستخدام: `/owner جزء من اسم الجهة`" + chr(10) + "مثال: `/owner الإسكان`",
                         parse_mode="Markdown")
        return
    try:
        card = _owner_card_text(q[1].strip())
        if card:
            bot.send_message(message.chat.id, card, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"🔍 لا توجد جهة تطابق «{q[1].strip()}»")
    except Exception as e:
        logger.error(f"/owner failed: {e}")
        bot.send_message(message.chat.id, f"⚠️ خطأ: {e}")

def _guarantee_status_markup(mid):
    m = InlineKeyboardMarkup(row_width=3)
    m.add(InlineKeyboardButton("🟢 جاهز", callback_data=f"gst_{mid}_READY"),
          InlineKeyboardButton("✅ قُدّم", callback_data=f"gst_{mid}_SUBMITTED"),
          InlineKeyboardButton("⚪ غير مطلوب", callback_data=f"gst_{mid}_NOT_REQUIRED"))
    return m

def _send_guarantee_cards(due_list, chat_id=None):
    """بطاقة لكل ضمان مع أزرار تحديث الحالة. due_list: (dleft,title,owner,due,mid)"""
    for dleft, title, owner, due, mid in due_list[:8]:
        when = ("⚠️ متأخر" if dleft < 0 else "🔴 اليوم" if dleft == 0
                else "🟠 غداً" if dleft == 1 else f"🟡 بعد {dleft} يوم")
        txt = f"{when} — استحقاق {due}\n*{title}*"
        if owner:
            txt += f"\n{owner}"
        bot.send_message(chat_id or CHAT_ID, txt, parse_mode="Markdown",
                         reply_markup=_guarantee_status_markup(mid))

def _collect_guarantees(max_ahead=14, min_behind=-3):
    """كل الضمانات غير المكتملة ضمن النافذة. يعيد (dleft,title,owner,due,mid) مرتبة."""
    from datetime import datetime as _dt, timedelta as _td
    with db._get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS tender_guarantees (
            tender_row_id INTEGER PRIMARY KEY, required INTEGER DEFAULT 1,
            due_date TEXT DEFAULT '', status TEXT DEFAULT 'PENDING',
            notes TEXT DEFAULT '', updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        rows = conn.execute("""
            SELECT mt.id, mt.title, mt.owner, mt.submission_date,
                   COALESCE(g.status,'PENDING') gstatus, COALESCE(g.due_date,'') gdue
            FROM master_tenders mt
            LEFT JOIN tender_guarantees g ON g.tender_row_id = mt.id
            WHERE mt.status NOT IN ('CLOSED','REJECTED')
              AND COALESCE(g.status,'PENDING') NOT IN ('READY','SUBMITTED','NOT_REQUIRED')
        """).fetchall()
    today = _dt.now().date()
    out = []
    for r in rows:
        due = None
        if r["gdue"]:
            try:
                due = _dt.strptime(r["gdue"][:10], "%Y-%m-%d").date()
            except Exception:
                pass
        if due is None:
            try:
                due = _dt.strptime(str(r["submission_date"])[:10], "%Y-%m-%d").date() - _td(days=5)
            except Exception:
                continue
        dleft = (due - today).days
        if min_behind <= dleft <= max_ahead:
            out.append((dleft, str(r["title"]), str(r["owner"] or ""), due.isoformat(), r["id"]))
    out.sort()
    return out

@bot.message_handler(commands=['guarantees'])
def handle_guarantees(message):
    """v5.6.4: قائمة الضمانات المستحقة مع أزرار تحديث فورية."""
    if not is_authorized(message): return
    try:
        items = _collect_guarantees(max_ahead=14, min_behind=-3)
        if not items:
            bot.send_message(message.chat.id, "🛡️ لا ضمانات مستحقة خلال 14 يوماً القادمة ✓")
            return
        bot.send_message(message.chat.id,
                         f"🛡️ *الضمانات المستحقة خلال 14 يوماً* — {len(items)}:",
                         parse_mode="Markdown")
        _send_guarantee_cards(items, chat_id=message.chat.id)
    except Exception as e:
        logger.error(f"/guarantees failed: {e}")
        bot.send_message(message.chat.id, f"⚠️ خطأ: {e}")

@bot.message_handler(commands=['followup'])
def handle_followup(message):
    """v5.6.4: العروض المقدمة بلا نتيجة — تسجيل بضغطة."""
    if not is_authorized(message): return
    try:
        from datetime import datetime as _dt
        with db._get_connection() as conn:
            rows = conn.execute("""
                SELECT id, title, owner, submission_date FROM tender_results
                WHERE did_submit = 1 AND (result IS NULL OR result = 'pending')
                ORDER BY submission_date""").fetchall()
        if not rows:
            bot.send_message(message.chat.id, "✅ لا عروض بانتظار نتيجة — السجل نظيف!")
            return
        today = _dt.now().date()
        bot.send_message(message.chat.id,
                         f"📋 *عروض بانتظار النتيجة* — {len(rows)}:\n"
                         "(النتائج لا تُعلن دائماً — «لم تُعلن» تقفل المتابعة)",
                         parse_mode="Markdown")
        for r in rows[:10]:
            days = ""
            try:
                sd = _dt.strptime(str(r["submission_date"])[:10], "%Y-%m-%d").date()
                days = f" · منذ {(today - sd).days} يوم"
            except Exception:
                pass
            txt = f"*{str(r['title'])}*\n{str(r['owner'] or '')}{days}"
            m = InlineKeyboardMarkup(row_width=3)
            m.add(InlineKeyboardButton("🏆 فزنا", callback_data=f"fres_{r['id']}_won"),
                  InlineKeyboardButton("❌ خسرنا", callback_data=f"fres_{r['id']}_lost"),
                  InlineKeyboardButton("⚪ لم تُعلن", callback_data=f"fres_{r['id']}_unknown"))
            bot.send_message(message.chat.id, txt, parse_mode="Markdown", reply_markup=m)
    except Exception as e:
        logger.error(f"/followup failed: {e}")
        bot.send_message(message.chat.id, f"⚠️ خطأ: {e}")

@bot.message_handler(commands=['find'])
def handle_find(message):
    """v5.6.4: بحث سريع بالاسم أو الجهة — بطاقة كاملة بأزرار إجراء."""
    if not is_authorized(message): return
    q = (message.text or "").split(maxsplit=1)
    if len(q) < 2 or not q[1].strip():
        bot.send_message(message.chat.id, "الاستخدام: `/find كلمة من اسم المنافسة أو الجهة`", parse_mode="Markdown")
        return
    term = q[1].strip()
    try:
        from datetime import datetime as _dt, timedelta as _td
        # v5.7.2: مطابقة عربية موحّدة (همزات + "ال") — نفس محرك /owner
        from engine_core import normalize_arabic as _norm
        t = _norm(term).strip()
        cands = [t]
        if t.startswith("ال") and len(t) > 4:
            cands.append(t[2:])
        def _hit(title, owner):
            hay = _norm(str(title or "") + " " + str(owner or ""))
            return any(c and c in hay for c in cands)
        with db._get_connection() as conn:
            all_rows = conn.execute("""
                SELECT mt.id, mt.title, mt.owner, mt.submission_date,
                       COALESCE(mt.assigned_engineer,'—') eng, mt.status,
                       COALESCE(g.status,'PENDING') gstatus, COALESCE(g.due_date,'') gdue
                FROM master_tenders mt
                LEFT JOIN tender_guarantees g ON g.tender_row_id = mt.id
                WHERE mt.status NOT IN ('CLOSED','REJECTED')
                ORDER BY mt.submission_date""").fetchall()
            closed_rows = conn.execute(
                "SELECT title, owner FROM master_tenders WHERE status IN ('CLOSED','REJECTED')").fetchall()
        rows = [r for r in all_rows if _hit(r["title"], r["owner"])][:5]
        closed_n = sum(1 for r in closed_rows if _hit(r["title"], r["owner"]))
        if not rows:
            extra = f"\n(يوجد {closed_n} نتيجة في الأرشيف المغلق)" if closed_n else ""
            bot.send_message(message.chat.id, f"🔍 لا نتائج نشطة تطابق «{term}»{extra}")
            return
        today = _dt.now().date()
        _GLBL = {"PENDING": "⚪ لم يبدأ", "IN_PROGRESS": "🟡 قيد الإصدار",
                 "READY": "🟢 جاهز", "SUBMITTED": "✅ قُدّم", "NOT_REQUIRED": "➖ غير مطلوب"}
        for r in rows:
            days_txt, icon = "", "⚪"
            try:
                d = _dt.strptime(str(r["submission_date"])[:10], "%Y-%m-%d").date()
                dl = (d - today).days
                icon = "🔴" if dl <= 3 else ("🟡" if dl <= 7 else "🟢")
                days_txt = f" (باقي {dl} يوم)" if dl >= 0 else f" (منتهية منذ {-dl} يوم)"
            except Exception:
                pass
            gdue_txt = ""
            if r["gstatus"] not in ("READY", "SUBMITTED", "NOT_REQUIRED"):
                gd = None
                if r["gdue"]:
                    try: gd = _dt.strptime(r["gdue"][:10], "%Y-%m-%d").date()
                    except Exception: pass
                if gd is None:
                    try: gd = _dt.strptime(str(r["submission_date"])[:10], "%Y-%m-%d").date() - _td(days=5)
                    except Exception: pass
                if gd:
                    gdue_txt = f" · استحقاقه {gd.isoformat()}"
            txt = (f"{icon} *{str(r['title'])}*\n"
                   f"الجهة: {str(r['owner'] or '—')}\n"
                   f"الإغلاق: {str(r['submission_date'] or '—')[:10]}{days_txt}\n"
                   f"المهندس: *{r['eng']}*\n"
                   f"الضمان: {_GLBL.get(r['gstatus'], r['gstatus'])}{gdue_txt}")
            m = InlineKeyboardMarkup(row_width=2)
            m.add(InlineKeyboardButton("🔁 تغيير المهندس", callback_data=f"fem_{r['id']}"),
                  InlineKeyboardButton("🛡️ حالة الضمان", callback_data=f"gmenu_{r['id']}"))
            bot.send_message(message.chat.id, txt, parse_mode="Markdown", reply_markup=m)
        if len(rows) == 5:
            bot.send_message(message.chat.id, "عرضت أول 5 نتائج — دقّق كلمة البحث لنتائج أقل.")
    except Exception as e:
        logger.error(f"/find failed: {e}")
        bot.send_message(message.chat.id, f"⚠️ خطأ: {e}")

@bot.message_handler(commands=['approve_all'])
def handle_approve_all(message):
    """اعتماد جماعي لكل الطلبات المنتظرة (جديدة + تعديلات مواعيد) بضغطة واحدة."""
    if not is_authorized(message): return
    with db._get_connection() as conn:
        n = conn.execute(
            "SELECT COUNT(*) FROM pending_changes WHERE status IN ('PENDING_APPROVAL','NOTIFIED') "
            "AND change_type IN ('NEW','NEW_TENDER','UPDATED_DATE')"
        ).fetchone()[0]
    if n == 0:
        bot.send_message(message.chat.id, "✅ لا توجد طلبات منتظرة — كل شيء متزامن.")
        return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"✅ نعم، اعتمد الكل ({n})", callback_data="bulkapprove_go"),
               InlineKeyboardButton("إلغاء", callback_data="bulkapprove_no"))
    bot.send_message(message.chat.id,
        f"⚠️ سيتم اعتماد *{n}* طلباً منتظراً دفعة واحدة\n"
        "(الجديدة تُسند للمهندس المقترح، وتعديلات التواريخ تحافظ على مهندسها الحالي)\n\nهل أنت متأكد؟",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('bulkapprove_'))
def handle_bulk_approve(call):
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ غير مصرح.", show_alert=True)
        return
    if call.data == 'bulkapprove_no':
        bot.edit_message_text("تم الإلغاء — لم يُعتمد شيء.", call.message.chat.id, call.message.message_id)
        return
    with db._get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM pending_changes WHERE status IN ('PENDING_APPROVAL','NOTIFIED') "
            "AND change_type IN ('NEW','NEW_TENDER','UPDATED_DATE') ORDER BY created_at"
        ).fetchall()
    done, lines = 0, []
    for row in rows:
        try:
            eng = _auto_engineer_for(row)
            db.approve_change(row['id'], eng)
            kind = "🆕" if row['change_type'] in ('NEW', 'NEW_TENDER') else "📅"
            lines.append(f"{kind} {str(row['title'])[:42]} ← {eng}")
            _notify_engineer(eng, "📌 أُسندت إليك منافسة:" + chr(10) + str(row['title']))
            done += 1
        except Exception as e:
            logger.error(f"Bulk approve failed for id={row['id']}: {e}")
    summary = f"✅ *تم اعتماد {done} طلباً:*\n" + "\n".join(lines[:20])
    if len(lines) > 20:
        summary += f"\n… و{len(lines)-20} أخرى"
    bot.edit_message_text(summary, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    logger.info(f"BULK APPROVE: {done} items approved via Telegram.")

@bot.message_handler(commands=['automode'])
def handle_automode(message):
    """تفعيل/إيقاف المزامنة الآلية الكاملة (اعتماد تلقائي + إشعار للعلم فقط)."""
    if not is_authorized(message): return
    parts = (message.text or "").strip().split()
    if len(parts) > 1 and parts[1].lower() in ("on", "off"):
        save_state(auto_approve=(parts[1].lower() == "on"))
        logger.info(f"AUTO-APPROVE mode set to {parts[1].lower()} via Telegram.")
    status = "🟢 مفعّل — الاعتماد تلقائي والإشعارات للعلم فقط" if is_auto_approve() \
             else "🔴 متوقف — كل تغيير يحتاج موافقتك (الوضع الحالي)"
    bot.send_message(message.chat.id,
        f"🤖 *وضع المزامنة الآلية:* {status}\n\n"
        "للتبديل: /automode on أو /automode off",
        parse_mode="Markdown")

@bot.message_handler(commands=['predict'])
def handle_predict(message):
    """V6: توقع تمديد المنافسات النشطة بناءً على سلوك الجهات التاريخي."""
    if not is_authorized(message): return
    try:
        from analytics_engine import format_extension_prediction_for_telegram
        bot.send_message(message.chat.id,
                         format_extension_prediction_for_telegram(db),
                         parse_mode="Markdown")
    except Exception as e:
        logger.error(f"/predict failed: {e}")
        bot.send_message(message.chat.id, f"⚠️ تعذر حساب التوقع: {e}")

@bot.message_handler(commands=['news'])
def handle_news(message):
    if not is_authorized(message): return
    logger.info(f"Manual /news command received from chat_id={message.chat.id}")
    bot.send_message(message.chat.id, "🔎 حاضر، سأفحص منصة الرواف الآن وأقارنها بقاعدة البيانات...")
    threading.Thread(target=run_manual_news_check, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['list'])
def handle_list(message):
    if not is_authorized(message): return
    bot.send_message(message.chat.id, "📋 حاضر، سأحدّث قائمة منصة الرواف وأقارنها بقاعدة البيانات...")
    threading.Thread(target=run_manual_list_report, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['list_d'])
def handle_list_details(message):
    if not is_authorized(message): return
    bot.send_message(message.chat.id, "📄 حاضر، سأجهز لك جدول المنافسات الحالي...")
    threading.Thread(target=send_tenders_detail_table, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(func=lambda message: bool(getattr(message, "text", "")) and message.text.strip().split()[0].lower().split("@")[0] == "/list-d")
def handle_list_details_hyphen(message):
    if not is_authorized(message): return
    bot.send_message(message.chat.id, "📄 حاضر، سأجهز لك جدول المنافسات الحالي...")
    threading.Thread(target=send_tenders_detail_table, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['pending'])
def handle_pending(message):
    if not is_authorized(message): return
    send_open_pending_cards(message.chat.id)

@bot.message_handler(commands=['status', 'health'])
def handle_health(message):
    if not is_authorized(message): return
    bot.send_message(message.chat.id, build_health_report(), parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    if not is_authorized(message): return
    stats = db.get_system_stats() # Corrected method name
    if not stats: 
        bot.send_message(message.chat.id, "❌ فشل جلب الإحصائيات.")
        return
    
    msg = (f"📊 *إحصائيات نظام الرواف*\n"
           f"━━━━━━━━━━━━━━\n"
           f"🟢 نشطة: {stats['active_count']}\n"
           f"🟡 معلقة: {stats['pending_count']}\n"
           f"⚪ مغلقة: {stats['closed_count']}\n\n"
           f"👷 *حمل المهندسين:*\n")
    
    for e in stats['engineers']:
        bar = get_progress_bar(e['load_pct'])
        msg += f"• *{e['name']}:* {e['load']}/{e['capacity']}\n  [{bar}] {e['load_pct']}%\n"
    
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['backup'])
def handle_manual_backup(message):
    if not is_authorized(message): return
    ok = job_backup_system()
    if ok:
        bot.send_message(message.chat.id, "✅ تم إرسال النسخة الاحتياطية بنجاح.")
    else:
        bot.send_message(message.chat.id, "❌ فشل إرسال النسخة الاحتياطية. راجع /health أو سجل البوت.")

@bot.message_handler(commands=['report'])
def handle_report(message):
    if not is_authorized(message): return
    if not PDF_OK:
        bot.send_message(message.chat.id,
            "⚠️ مكتبة `reportlab` غير مثبّتة على السيرفر.\n"
            "شغّل: `pip install reportlab` ثم أعد المحاولة.",
            parse_mode="Markdown")
        return
    bot.send_message(message.chat.id, "⏳ جاري إنشاء التقرير الشهري، لحظة...")
    job_monthly_report()

@bot.message_handler(commands=['test'])
def handle_test(message):
    if not is_authorized(message): return
    bot.send_message(
        message.chat.id,
        "🧪 *اختبار إشعار فقط - لا يؤثر على قاعدة البيانات*\n\n"
        "هذه رسالة تجربة من بوت الرواف. لم يتم إنشاء pending، ولم يتم تعديل قاعدة البيانات، ولا يوجد إجراء مطلوب.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['lastlog'])
def handle_lastlog(message):
    if not is_authorized(message): return
    log_text = read_last_log_lines(45)
    if len(log_text) > 3500:
        log_text = log_text[-3500:]
    bot.send_message(message.chat.id, f"```text\n{log_text}\n```", parse_mode="Markdown")

@bot.message_handler(commands=['pause'])
def handle_pause(message):
    if not is_authorized(message): return
    save_state(paused=True, paused_at=utc_now_iso(), paused_by=getattr(message.from_user, "id", "telegram"))
    bot.send_message(message.chat.id, "⏸️ تم إيقاف مزامنة موقع الرواف مؤقتاً. النسخ الاحتياطية وأوامر تيليجرام ستبقى تعمل.")

@bot.message_handler(commands=['resume'])
def handle_resume(message):
    if not is_authorized(message): return
    save_state(paused=False, resumed_at=utc_now_iso())
    bot.send_message(message.chat.id, "▶️ تم تشغيل المزامنة مرة أخرى. سأبدأ الفحص في الدورة القادمة.")

@bot.message_handler(func=lambda m: (
    bool(getattr(m, "text", ""))
    and not m.text.strip().startswith("/")
))
def handle_text_query(message):
    """Conversational NLQ handler — responds to free-text Arabic questions."""
    if not is_authorized(message):
        return
    logger.info(f"Chat query received from user={getattr(message.from_user,'id','?')}: {message.text[:80]}")
    try:
        from chat_handler import handle_chat_query
        response = handle_chat_query(message.text, db.db_path)
        if response:
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        else:
            bot.send_message(
                message.chat.id,
                "🤖 لم أفهم سؤالك تماماً.\n\n"
                "جرّب مثلاً:\n"
                "• _غداً معنا كم منافسة مفروض تسلم؟_\n"
                "• _المعمري معه كم منافسة؟_\n"
                "• _مواعيد منافسات محمد_\n"
                "• _من الأكثر مشغولاً؟_\n"
                "• _من عنده وقت؟_\n"
                "• _بحث عن أرامكو_\n"
                "• _كم منافسة عندنا؟_\n\n"
                "أو اكتب /help لقائمة الأوامر.",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.exception(f"handle_text_query error: {e}")
        bot.send_message(message.chat.id, f"❌ حدث خطأ أثناء معالجة سؤالك:\n`{e}`", parse_mode="Markdown")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    if not is_authorized(message): return
    
    file_name = message.document.file_name
    if not file_name.endswith('.xlsx'):
        bot.reply_to(message, "❌ نأسف، النظام يقبل ملفات Excel فقط (.xlsx).")
        return
        
    try:
        # Download the file from Telegram
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save it over the Master_Tenders.xlsx
        master_path = BASE_DIR / "output" / "Master_Tenders.xlsx"
        master_path.parent.mkdir(parents=True, exist_ok=True)
        with open(master_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.reply_to(message, "⏳ تم استلام الملف بنجاح. جاري المزامنة مع قاعدة البيانات...")
        
        # Trigger the reverse sync
        import reverse_sync_to_sql
        updated_count = reverse_sync_to_sql.reverse_sync()
        
        bot.send_message(message.chat.id, f"✅ اكتملت المزامنة!\nتم تحديث ({updated_count}) مناقصة في النظام بناءً على ملفك.")
        logger.info(f"Manual Excel Upload applied: {updated_count} updates.")
        
    except Exception as e:
        logger.error(f"Failed to process uploaded Excel: {e}")
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة الملف:\n{e}")

# ============================================================
# 5. SECURITY HELPERS
# ============================================================
def is_authorized(message_or_call):
    """
    Auth — two valid scenarios:
      A) Message from the designated group CHAT_ID
         (if ADMIN_USER_ID is set, only that user is allowed inside the group)
      B) Private DM to the bot
         (if ADMIN_USER_ID is set, restricted to that user only;
          if not set, any private chat is allowed — the bot token is the security gate)
    """
    chat_obj  = message_or_call.chat if hasattr(message_or_call, 'chat') else message_or_call.message.chat
    from_user = getattr(message_or_call, "from_user", None)
    user_id   = str(getattr(from_user, "id", None))
    chat_id   = str(chat_obj.id)
    chat_type = getattr(chat_obj, "type", "")

    # ── Scenario A: message from the designated group ─────────────────────────
    if chat_id == str(CHAT_ID):
        if ADMIN_USER_ID and user_id != str(ADMIN_USER_ID):
            return False
        return True

    # ── Scenario B: private DM ────────────────────────────────────────────────
    if chat_type == "private":
        # If admin ID is configured → restrict to that user
        if ADMIN_USER_ID:
            if user_id == str(ADMIN_USER_ID):
                return True
        else:
            # No admin filter configured → log the user ID (helpful for first setup)
            # and allow the DM (the bot token itself is the access gate)
            logger.info(f"Private DM received from user_id={user_id}. "
                        "Set ADMIN_USER_ID in .env to restrict access to this user only.")
            return True

    logger.warning(f"Rejected: chat_id={chat_id} user_id={user_id} type={chat_type}")
    return False

# ============================================================
# 6. TELEGRAM CALLBACK HANDLERS
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def handle_approve(call):
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ خطأ أمني: غير مصرح لك.", show_alert=True)
        return
    """Handles Approve Button"""
    _, pending_id, eng_name = call.data.split('_', 2)

    # Get title + status; block double-approval from stale cards
    with db._get_connection() as conn:
        p = conn.execute("SELECT title, status FROM pending_changes WHERE id = ?", (pending_id,)).fetchone()
        title = p[0] if p else None
        cur_status = p[1] if p else None
    if cur_status not in ('PENDING_APPROVAL', 'NOTIFIED'):
        bot.answer_callback_query(call.id, "⚠️ هذا الطلب تمت معالجته مسبقاً — لا حاجة لإجراء.", show_alert=True)
        return

    # Proceed with database approval
    db.approve_change(pending_id, eng_name)
    logger.info(f"APPROVED: Pending ID {pending_id} assigned to {eng_name}")

    bot.edit_message_text(
        f"✅ تم بنجاح اعتماد المناقصة: *{title}*\nللمهندس: *{eng_name}* وتم تحديث ملف الماستر!",
        call.message.chat.id, call.message.message_id, parse_mode='Markdown'
    )

    # SMART CLEANUP: Invalidate any other pending records for the same title
    if title:
        with db._get_connection() as conn:
            conn.execute(
                "UPDATE pending_changes SET status = 'CLEANED' "
                "WHERE title = ? AND status IN ('PENDING_APPROVAL', 'NOTIFIED')",
                (title,)
            )
            conn.commit()
            logger.info(f"Cleanup: Marked all duplicate pending items for '{title}' as CLEANED.")
    
    bot.answer_callback_query(call.id, "تم الاعتماد بنجاح!")


@bot.callback_query_handler(func=lambda call: call.data.startswith('sub_'))
def handle_sub_pick(call):
    """تثبيت اشتراك المهندس (خاص فقط — الأزرار تظهر بعد PIN صحيح)."""
    if getattr(call.message.chat, "type", "") != "private":
        bot.answer_callback_query(call.id, "الاشتراك في الخاص فقط.", show_alert=True)
        return
    _, eng_name = call.data.split('_', 1)
    with db._get_connection() as conn:
        _ensure_subs_table(conn)
        conn.execute("""INSERT INTO engineer_subs (chat_id, engineer_name, subscribed_at)
                        VALUES (?,?,CURRENT_TIMESTAMP)
                        ON CONFLICT(chat_id) DO UPDATE SET
                          engineer_name=excluded.engineer_name, subscribed_at=CURRENT_TIMESTAMP""",
                     (call.message.chat.id, eng_name))
        conn.commit()
    db.log_audit("ENG_SUBSCRIBE", eng_name, f"chat_id={call.message.chat.id}", "TelegramBot")
    bot.edit_message_text(
        f"✅ تم اشتراكك باسم *{eng_name}*" + chr(10) + chr(10) +
        "سيصلك هنا خاصاً:" + chr(10) +
        "• إشعار فوري عند إسناد منافسة إليك" + chr(10) +
        "• ملخص صباحي يومياً 8:15 بمنافساتك ومواعيدها وضماناتها" + chr(10) + chr(10) +
        "أوامرك: /mytenders لعرض منافساتك الآن — /unsubscribe لإلغاء الاشتراك",
        call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id, f"أهلاً {eng_name}!")
    logger.info(f"Engineer subscribed: {eng_name} chat={call.message.chat.id}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('gst_'))
def handle_guarantee_set(call):
    """تحديث حالة الضمان من زر تيليجرام."""
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ غير مصرح.", show_alert=True)
        return
    _, mid, status = call.data.split('_', 2)
    labels = {"READY": "🟢 جاهز", "SUBMITTED": "✅ قُدّم مع العرض", "NOT_REQUIRED": "⚪ غير مطلوب"}
    if status not in labels:
        return
    with db._get_connection() as conn:
        t = conn.execute("SELECT title FROM master_tenders WHERE id = ?", (mid,)).fetchone()
        if not t:
            bot.answer_callback_query(call.id, "⚠️ لم أجد المنافسة.", show_alert=True)
            return
        conn.execute("""INSERT INTO tender_guarantees (tender_row_id, status, updated_at)
                        VALUES (?,?,CURRENT_TIMESTAMP)
                        ON CONFLICT(tender_row_id) DO UPDATE SET
                          status=excluded.status, updated_at=CURRENT_TIMESTAMP""", (mid, status))
        conn.commit()
    db.log_audit("GUARANTEE_TG", t[0], f"status={status}", "TelegramBot")
    bot.edit_message_text(f"🛡️ *{str(t[0])}*\nحالة الضمان: {labels[status]} ✓",
                          call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id, "تم التحديث ✓")
    logger.info(f"Guarantee status via TG: master_id={mid} -> {status}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('fres_'))
def handle_followup_result(call):
    """تسجيل نتيجة عرض من زر تيليجرام."""
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ غير مصرح.", show_alert=True)
        return
    _, rec_id, res = call.data.split('_', 2)
    labels = {"won": "🏆 فوز", "lost": "❌ خسارة", "unknown": "⚪ لم تُعلن"}
    if res not in labels:
        return
    with db._get_connection() as conn:
        row = conn.execute("SELECT title FROM tender_results WHERE id = ?", (rec_id,)).fetchone()
        if not row:
            bot.answer_callback_query(call.id, "⚠️ لم أجد السجل.", show_alert=True)
            return
        conn.execute("""UPDATE tender_results
                        SET result=?, did_submit=CASE WHEN ? IN ('won','lost') THEN 1 ELSE did_submit END,
                            updated_at=CURRENT_TIMESTAMP WHERE id=?""", (res, res, rec_id))
        conn.commit()
    db.log_audit("RESULT_TG", row[0], f"result={res}", "TelegramBot")
    bot.edit_message_text(f"📋 *{str(row[0])}*\nالنتيجة: {labels[res]} ✓",
                          call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id, "سُجلت النتيجة ✓")
    logger.info(f"Result via TG: rec_id={rec_id} -> {res}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('gmenu_'))
def handle_guarantee_menu(call):
    """عرض أزرار حالة الضمان على بطاقة /find."""
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ غير مصرح.", show_alert=True)
        return
    _, mid = call.data.split('_', 1)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=_guarantee_status_markup(mid))
    bot.answer_callback_query(call.id, "اختر حالة الضمان")

@bot.callback_query_handler(func=lambda call: call.data.startswith('fes_'))
def handle_find_eng_set(call):
    """تعيين مهندس من بطاقة /find وتثبيته."""
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ غير مصرح.", show_alert=True)
        return
    _, mid, eng_name = call.data.split('_', 2)
    with db._get_connection() as conn:
        t = conn.execute("SELECT title FROM master_tenders WHERE id = ?", (mid,)).fetchone()
        if not t:
            bot.answer_callback_query(call.id, "⚠️ لم أجد المنافسة.", show_alert=True)
            return
        conn.execute("""UPDATE master_tenders SET assigned_engineer=?, engineer_locked=1,
                        updated_at=CURRENT_TIMESTAMP WHERE id=?""", (eng_name, mid))
        conn.commit()
    db.log_audit("CHANGE_ENG", t[0], f"/find reassigned to {eng_name} (locked)", "TelegramBot")
    db.export_master_excel()
    bot.edit_message_text(f"✅ *{str(t[0])}*\nالمهندس الجديد: *{eng_name}* 🔒",
                          call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id, f"تم الإسناد إلى {eng_name}")
    _notify_engineer(eng_name, "📌 أُسندت إليك منافسة:" + chr(10) + str(t[0]))

@bot.callback_query_handler(func=lambda call: call.data.startswith('fem_'))
def handle_find_eng_menu(call):
    """قائمة المهندسين على بطاقة /find."""
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ غير مصرح.", show_alert=True)
        return
    _, mid = call.data.split('_', 1)
    engineers = db.get_all_engineers()
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(*[InlineKeyboardButton(e['name'], callback_data=f"fes_{mid}_{e['name']}")
                 for e in engineers])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, "اختر المهندس")

@bot.callback_query_handler(func=lambda call: call.data.startswith('aes_'))
def handle_autoeng_set(call):
    """مزامنة آلية: تطبيق تغيير المهندس وتثبيته ضد أي اقتراح مستقبلي."""
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ غير مصرح.", show_alert=True)
        return
    _, pending_id, eng_name = call.data.split('_', 2)
    with db._get_connection() as conn:
        p = conn.execute("SELECT title FROM pending_changes WHERE id = ?", (pending_id,)).fetchone()
        if not p:
            bot.answer_callback_query(call.id, "⚠️ لم أجد السجل.", show_alert=True)
            return
        conn.execute(
            "UPDATE master_tenders SET assigned_engineer = ?, engineer_locked = 1, "
            "updated_at = CURRENT_TIMESTAMP WHERE title = ?",
            (eng_name, p[0])
        )
        conn.commit()
    db.log_audit("CHANGE_ENG", p[0], f"Auto-sync reassigned to {eng_name} (locked)", "Admin")
    db.export_master_excel()
    bot.edit_message_text(
        f"✅ تم تغيير المهندس إلى: *{eng_name}* وتثبيته 🔒\n*{p[0]}*",
        call.message.chat.id, call.message.message_id, parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, f"تم الإسناد إلى {eng_name}")
    _notify_engineer(eng_name, "📌 أُسندت إليك منافسة:" + chr(10) + str(p[0]))
    logger.info(f"AUTO-SYNC REASSIGN: pending_id={pending_id} -> {eng_name} (locked)")

@bot.callback_query_handler(func=lambda call: call.data.startswith('aem_'))
def handle_autoeng_menu(call):
    """مزامنة آلية: عرض قائمة المهندسين للتبديل بضغطة."""
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ غير مصرح.", show_alert=True)
        return
    _, pending_id = call.data.split('_', 1)
    engineers = db.get_all_engineers()
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(*[InlineKeyboardButton(e['name'], callback_data=f"aes_{pending_id}_{e['name']}")
                 for e in engineers])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, "اختر المهندس الجديد")

@bot.callback_query_handler(func=lambda call: call.data.startswith('changeeng_'))
def handle_change_eng(call):
    """Handles Change Engineer Button"""
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ خطأ أمني: غير مصرح لك.", show_alert=True)
        return

    _, pending_id = call.data.split('_')
    engineers = db.get_all_engineers()
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(eng['name'], callback_data=f"approve_{pending_id}_{eng['name']}")
        for eng in engineers
    ]
    markup.add(*buttons)
    bot.edit_message_text(
        "🔄 الرجاء اختيار المهندس المراد إسناد المناقصة له من القائمة:",
        call.message.chat.id, call.message.message_id, reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def handle_reject(call):
    if not is_authorized(call):
        bot.answer_callback_query(call.id, "❌ خطأ أمني: غير مصرح لك.", show_alert=True)
        return
    """Handles Reject Button"""
    _, pending_id = call.data.split('_')
    db.delete_pending_change(pending_id)
    logger.info(f"REJECTED: Pending ID {pending_id} dismissed by user.")
    bot.edit_message_text(
        "❌ تم تجاهل المناقصة وإزالتها من قائمة المعلقات.",
        call.message.chat.id, call.message.message_id
    )
    bot.answer_callback_query(call.id, "تم التجاهل")

# ============================================================
# 5b. AI CHAT ASSISTANT  (OpenAI GPT + Whisper voice)
# ============================================================

# ── Initialise client ────────────────────────────────────────
import ai_assistant
from ai_assistant import (AI_MODEL, AI_MAX_HISTORY, AI_ENABLED, _ai_client,
                          _ai_history, _AI_LOCK, _history_load, _history_save,
                          _history_clear, _history_compress, _dialect_per_user,
                          _DIALECT_PROMPTS, _AI_SYSTEM, _AI_KNOWLEDGE,
                          _ai_load_knowledge, _ai_live_context, _ai_reply,
                          _VOICE_MODE_SUFFIX, _VOICE_MODE_SUFFIX_MASRI,
                          _ARABIC_ONLY_SUFFIX)
ai_assistant.configure(db, _track_error)
# _OPENAI_KEY: moved to ai_assistant.py
# CLIENT_INIT: moved to ai_assistant.py

# _ai_history: moved to ai_assistant.py
# _AI_LOCK: moved to ai_assistant.py

# ── Persistent AI history (SQLite) ────────────────────────────
# _AI_HISTORY_DB: moved to ai_assistant.py

# _history_db_init: moved to ai_assistant.py

# _history_load: moved to ai_assistant.py

# _COMPRESS_THRESHOLD: moved to ai_assistant.py

# _history_compress: moved to ai_assistant.py


# _history_save: moved to ai_assistant.py

# _history_clear: moved to ai_assistant.py

# DB_INIT_CALL: moved to ai_assistant.py

# ── Per-user runtime state ─────────────────────────────────────
_last_voice_reply:  dict = {}   # chat_id → last audio bytes (for /repeat)
_voicemode_users:   set  = set()# chat_id → always reply with voice
_voice_rate_limit:  dict = {}   # chat_id → last voice message timestamp

# TTS voices — user can switch with /voice command
_TTS_VOICES = {
    "1": ("onyx",    "رجل — صوت عميق"),
    "2": ("echo",    "رجل — صوت متوسط"),
    "3": ("fable",   "رجل — صوت ناعم"),
    "4": ("nova",    "امرأة — صوت طبيعي"),
    "5": ("shimmer", "امرأة — صوت ناعم"),
}
_tts_voice_per_user: dict = {}   # chat_id → voice name (default: onyx)

# Dialect settings per user
_DIALECTS = {
    "1": ("فصحى",   "اللغة العربية الفصحى — الافتراضي"),
    "2": ("مصري",   "العامية المصرية 🇪🇬"),
    "3": ("خليجي",  "اللهجة الخليجية 🇸🇦"),
}
# _DIALECT_PROMPTS: moved to ai_assistant.py
# _dialect_per_user: moved to ai_assistant.py

# _AI_SYSTEM: moved to ai_assistant.py

# _ai_load_knowledge: moved to ai_assistant.py

# Load knowledge base once at startup (reloaded on bot restart after upload)
# _AI_KNOWLEDGE: moved to ai_assistant.py


# _ai_live_context: moved to ai_assistant.py

# _VOICE_MODE_SUFFIX: moved to ai_assistant.py

# نسخة مصرية من الـ prompt الصوتي — تُستخدَم لما المستخدم يختار اللهجة المصرية
# _VOICE_MODE_SUFFIX_MASRI: moved to ai_assistant.py

# نفس التعليمات للردود النصية — عربي خالص دائماً
# _ARABIC_ONLY_SUFFIX: moved to ai_assistant.py

# _ai_reply: moved to ai_assistant.py


@bot.message_handler(commands=['reset'])
def handle_ai_reset(message):
    """Clear conversation history for this user (RAM + DB)."""
    if not is_authorized(message): return
    _ai_history.pop(message.chat.id, None)
    _history_clear(message.chat.id)
    bot.send_message(message.chat.id, "🔄 تم مسح سجل المحادثة. ابدأ محادثة جديدة!")


@bot.message_handler(commands=['repeat'])
def handle_repeat(message):
    """Resend last voice reply."""
    if not is_authorized(message): return
    audio = _last_voice_reply.get(message.chat.id)
    if not audio:
        bot.send_message(message.chat.id, "⚠️ لا يوجد رد صوتي سابق لإعادته.")
        return
    import io
    buf = io.BytesIO(audio); buf.name = "reply.ogg"
    bot.send_voice(message.chat.id, buf)


@bot.message_handler(commands=['voicemode'])
def handle_voicemode(message):
    """Toggle: all replies as voice, regardless of input type."""
    if not is_authorized(message): return
    cid = message.chat.id
    if cid in _voicemode_users:
        _voicemode_users.discard(cid)
        bot.send_message(cid, "🔇 وضع الصوت الدائم: *مُوقَف*\nالردود النصية ستعود نصاً.",
                         parse_mode="Markdown")
    else:
        _voicemode_users.add(cid)
        bot.send_message(cid, "🔊 وضع الصوت الدائم: *مُفعَّل*\nجميع ردودي ستكون صوتاً الآن.",
                         parse_mode="Markdown")


@bot.message_handler(commands=['voice'])
def handle_voice_select(message):
    """Let user pick TTS voice."""
    if not is_authorized(message): return
    parts = message.text.strip().split()
    if len(parts) == 1:
        # Show menu
        current_voice = _tts_voice_per_user.get(message.chat.id, "onyx")
        lines = ["🎙️ *اختر صوت الردود الصوتية:*\n"]
        for num, (vname, vdesc) in _TTS_VOICES.items():
            marker = "✅" if vname == current_voice else "  "
            lines.append(f"{marker} /voice {num}  —  {vdesc}")
        lines.append(f"\n_الصوت الحالي: {current_voice}_")
        bot.send_message(message.chat.id, "\n".join(lines), parse_mode="Markdown")
    elif parts[1] in _TTS_VOICES:
        voice_name, voice_desc = _TTS_VOICES[parts[1]]
        _tts_voice_per_user[message.chat.id] = voice_name
        bot.send_message(message.chat.id,
                         f"✅ تم تغيير الصوت إلى: *{voice_desc}*\n"
                         f"سيُطبّق على ردودك الصوتية القادمة.",
                         parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚠️ رقم غير صحيح. اكتب /voice لرؤية الخيارات.")


@bot.message_handler(commands=['dialect'])
def handle_dialect_select(message):
    """Let user pick reply dialect (فصحى / مصري / خليجي)."""
    if not is_authorized(message): return
    parts = message.text.strip().split()
    if len(parts) == 1:
        current = _dialect_per_user.get(message.chat.id, "فصحى")
        lines = ["🗣️ *اختر لهجة الردود:*\n"]
        for num, (dname, ddesc) in _DIALECTS.items():
            marker = "✅" if dname == current else "  "
            lines.append(f"{marker} /dialect {num}  —  {ddesc}")
        lines.append(f"\n_اللهجة الحالية: {current}_")
        bot.send_message(message.chat.id, "\n".join(lines), parse_mode="Markdown")
    elif parts[1] in _DIALECTS:
        dialect_name, dialect_desc = _DIALECTS[parts[1]]
        _dialect_per_user[message.chat.id] = dialect_name
        bot.send_message(message.chat.id,
                         f"✅ تم تغيير اللهجة إلى: *{dialect_desc}*\n"
                         f"سيُطبّق على جميع ردودي القادمة.",
                         parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚠️ رقم غير صحيح. اكتب /dialect لرؤية الخيارات.")


# ── قاموس النطق المخصص (شامل) ────────────────────────────────
from tts_text import (_PRONUNCIATION_DICT, _ARABIC_PHONETIC_CORRECTIONS,
                      _EN_PHONETIC, _transliterate, _apply_pronunciation,
                      _num_to_ar, _tts_prepare, _split_for_tts)
# _PRONUNCIATION_DICT: moved to tts_text.py

# ── تصحيح نطق الكلمات العربية بالعامية المصرية ──────────────
# _ARABIC_PHONETIC_CORRECTIONS: moved to tts_text.py

# نقل صوتي للحروف الإنجليزية → عربية (للكلمات غير الموجودة بالقاموس)
# _EN_PHONETIC: moved to tts_text.py

# _transliterate: moved to tts_text.py

# _apply_pronunciation: moved to tts_text.py


# _num_to_ar: moved to tts_text.py


# _tts_prepare: moved to tts_text.py


# ── تعيين صوت Google TTS بناءً على اختيار المستخدم ─────────────
_GOOGLE_VOICE_MAP = {
    "onyx":    "ar-XA-Chirp3-HD-Charon",   # ذكر  — مختار من المستخدم ⭐
    "echo":    "ar-XA-Chirp3-HD-Charon",   # ذكر
    "fable":   "ar-XA-Chirp3-HD-Charon",   # ذكر
    "nova":    "ar-XA-Chirp3-HD-Kore",     # أنثى
    "shimmer": "ar-XA-Chirp3-HD-Kore",     # أنثى
}

def _ai_speak_google(speakable: str, chat_id: int = 0) -> bytes | None:
    """تحويل نص → صوت عربي أصيل باستخدام Google Cloud TTS مع SSML."""
    import requests, base64, html as _html
    key = os.getenv("GOOGLE_TTS_KEY", "")
    if not key:
        return None
    oai_voice    = _tts_voice_per_user.get(chat_id, "onyx")
    google_voice = _GOOGLE_VOICE_MAP.get(oai_voice, "ar-XA-Chirp3-HD-Charon")

    # ── تنظيف إضافي قبل SSML: إزالة أي حرف قد يكسر XML ─────────
    import re as _re
    clean = _re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', speakable)

    # ── بناء SSML: توقفات طبيعية تُحسّن الإيقاع والوضوح ─────────
    safe = _html.escape(clean)
    safe = safe.replace(". ",  '.<break time="300ms"/> ')
    safe = safe.replace("، ", '،<break time="120ms"/> ')
    safe = safe.replace("؟ ",  '؟<break time="320ms"/> ')
    safe = safe.replace("! ",  '!<break time="260ms"/> ')
    safe = safe.replace(": ",  ':<break time="180ms"/> ')
    ssml = f'<speak>{safe}</speak>'

    _voice_cfg = {"languageCode": "ar-XA", "name": google_voice}
    _audio_cfg = {
        "audioEncoding": "OGG_OPUS",
        "speakingRate":  0.96,
        "pitch":         -2.5,
        # effectsProfileId محذوف — غير متوافق مع Chirp3-HD ويسبب 400
    }
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}"

    def _post(input_payload):
        r = requests.post(url,
                          json={"input": input_payload,
                                "voice": _voice_cfg,
                                "audioConfig": _audio_cfg},
                          timeout=20)
        r.raise_for_status()
        return base64.b64decode(r.json()["audioContent"])

    # ① حاول SSML أولاً
    try:
        audio_bytes = _post({"ssml": ssml})
        logger.info(f"Google TTS ok (SSML): voice={google_voice} audio={len(audio_bytes)}")
        return audio_bytes
    except Exception as ssml_err:
        logger.warning(f"Google TTS SSML failed: {ssml_err} → retrying plain text")

    # ② fallback لـ plain text عند أي فشل في SSML
    try:
        audio_bytes = _post({"text": clean})
        logger.info(f"Google TTS ok (plain): voice={google_voice} audio={len(audio_bytes)}")
        return audio_bytes
    except Exception as plain_err:
        # فقط لو الاتنين فشلوا → أرسل تنبيه
        logger.warning(f"Google TTS failed (SSML+plain): {plain_err}")
        _track_error("Google TTS", str(plain_err)[:120])
        return None




def _ai_speak_gemini(speakable: str, chat_id: int = 0) -> bytes | None:
    """Arabic TTS using Gemini 2.5 Flash TTS — best Arabic quality."""
    try:
        from google import genai
        from google.genai import types
        import wave as _wave, io as _io, subprocess, tempfile, os as _os

        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            return None

        _GEMINI_VOICE_MAP = {
            "onyx": "Charon", "echo": "Fenrir", "fable": "Puck",
            "nova": "Kore", "shimmer": "Aoede", "alloy": "Charon",
        }
        oai_voice    = _tts_voice_per_user.get(chat_id, "onyx")
        gemini_voice = _GEMINI_VOICE_MAP.get(oai_voice, "Charon")

        client   = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=speakable,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=gemini_voice
                        )
                    )
                )
            )
        )

        part    = response.candidates[0].content.parts[0]
        pcm_raw = part.inline_data.data   # bytes, L16 PCM 24kHz mono

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wt:
            wav_path = wt.name
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ot:
            ogg_path = ot.name

        try:
            with _wave.open(wav_path, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(24000)
                wav.writeframes(pcm_raw)

            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            proc = subprocess.run(
                [ffmpeg_exe, "-i", wav_path,
                 "-c:a", "libopus", "-b:a", "64k",
                 ogg_path, "-y", "-loglevel", "error"],
                capture_output=True, timeout=15
            )
            if proc.returncode == 0:
                with open(ogg_path, "rb") as f:
                    ogg_bytes = f.read()
                duration = len(pcm_raw) / 48000
                logger.info(f"Gemini TTS ok: voice={gemini_voice} size={len(ogg_bytes)}B duration={duration:.1f}s")
                return ogg_bytes
            else:
                logger.warning(f"ffmpeg conversion failed: {proc.stderr.decode()[:80]}")
                return None
        finally:
            _os.unlink(wav_path) if _os.path.exists(wav_path) else None
            _os.unlink(ogg_path) if _os.path.exists(ogg_path) else None

    except Exception as e:
        logger.warning(f"Gemini TTS failed: {e}")
        _track_error("Gemini TTS", str(e)[:120])
        return None



def _ai_speak(reply_text: str, chat_id: int = 0) -> bytes | None:
    """تحويل نص → صوت. يستخدم Google TTS أولاً (عربي أصيل) ثم OpenAI كاحتياط."""
    speakable = _tts_prepare(reply_text)

    # ① Gemini TTS — الأولوية (عربي أصيل - أفضل جودة)
    if os.getenv("GEMINI_API_KEY"):
        audio = _ai_speak_gemini(speakable, chat_id)
        if audio:
            _last_voice_reply[chat_id] = audio
            return audio

    # ② OpenAI TTS — احتياط عند فشل Google
    if not AI_ENABLED:
        return None
    voice = _tts_voice_per_user.get(chat_id, "onyx")
    try:
        import io
        response = _ai_client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=speakable,
            response_format="opus",
        )
        buf = io.BytesIO()
        for chunk in response.iter_bytes(chunk_size=4096):
            buf.write(chunk)
        audio_bytes = buf.getvalue()
        _last_voice_reply[chat_id] = audio_bytes
        return audio_bytes
    except Exception as e:
        logger.warning(f"OpenAI TTS failed: {e}")
        _track_error("OpenAI TTS", str(e)[:120])
        return None


_VOICE_RATE_LIMIT_SEC  = 8    # minimum seconds between voice messages per user

# ── Cache رسائل الخطأ الصوتية — تُولَّد مرة واحدة وتُحفَظ ───────
_voice_err_cache: dict[str, bytes | None] = {}

def _send_voice_error(cid: int, text: str):
    """أرسل رسالة خطأ صوتياً — مع cache للرسائل المتكررة."""
    import io
    # ابحث في الـ cache أولاً (لو نفس النص أُرسِل قبل كده)
    audio = _voice_err_cache.get(text)
    if audio is None:
        audio = _ai_speak(text, cid)
        if audio:
            _voice_err_cache[text] = audio   # احفظ للمرات القادمة
    if audio:
        buf = io.BytesIO(audio); buf.seek(0); buf.name = "err.ogg"
        try:
            bot.send_voice(cid, buf); return
        except Exception:
            pass
    bot.send_message(cid, text)   # fallback نصي
_VOICE_MIN_SIZE_BYTES  = 3000 # أقل من هذا = ضجيج أو صمت → تجاهل
_thinking_audio_cache: dict = {}  # voice_name → bytes (lazy-generated per voice)

def _get_thinking_audio(voice: str) -> bytes | None:
    """
    صوت 'لحظة من فضلك' يُرسَل فوراً بعد التفريغ.
    يستخدم Google TTS أولاً ثم OpenAI كاحتياط.
    يُولَّد مرة واحدة لكل صوت ويُخزَّن في الذاكرة.
    """
    if not AI_ENABLED:
        return None
    if voice not in _thinking_audio_cache:
        # بدون أي معالجة — النموذج العصبي ينطقها طبيعياً من غير تدخّل
        text = "لحظة من فضلك."
        # ① Gemini TTS أولاً (أفضل جودة عربية)
        audio = _ai_speak_gemini(text, 0) if os.getenv("GEMINI_API_KEY") else None
        # ② OpenAI كاحتياط
        if not audio:
            try:
                import io
                resp = _ai_client.audio.speech.create(
                    model="tts-1", voice=voice,
                    input=text, response_format="opus",
                )
                buf = io.BytesIO()
                for chunk in resp.iter_bytes(4096): buf.write(chunk)
                audio = buf.getvalue()
            except Exception as e:
                logger.warning(f"Thinking audio generation failed: {e}")
                audio = None
        _thinking_audio_cache[voice] = audio
        if audio:
            logger.info(f"Thinking audio cached for voice '{voice}' ({len(audio)} bytes)")
    return _thinking_audio_cache.get(voice)


# _split_for_tts: moved to tts_text.py

@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    """
    Pipeline صوتي عالمي المستوى:
    1. فحص الحجم → رفض الضجيج فوراً
    2. Rate limiting
    3. Whisper + domain prompt + سياق المحادثة → دقة عالية
    4. إرسال "لحظة..." صوتياً → لا صمت مخيف
    5. GPT مختصر → TTS-HD
    6. تقسيم الرد الطويل → جزأين (تجاوب أسرع)
    """
    if not is_authorized(message): return
    if not AI_ENABLED:
        bot.send_message(message.chat.id, "⚠️ خاصية المساعد الذكي غير مفعّلة.")
        return

    cid = message.chat.id
    import io

    # ── 1. فحص حجم الصوت — رفض الضجيج ──────────────────────
    file_size = getattr(message.voice, 'file_size', 0) or 0
    if file_size < _VOICE_MIN_SIZE_BYTES:
        _send_voice_error(cid, "الرسالة قصيرة جداً. تحدث بوضوح وجرّب مرة أخرى.")
        return

    # ── 2. Rate limiting ──────────────────────────────────────
    now  = time.time()
    last = _voice_rate_limit.get(cid, 0)
    if now - last < _VOICE_RATE_LIMIT_SEC:
        remaining = int(_VOICE_RATE_LIMIT_SEC - (now - last))
        bot.send_message(cid, f"⏳ انتظر {remaining} ثانية.")
        return
    _voice_rate_limit[cid] = now

    try:
        bot.send_chat_action(cid, 'record_voice')

        # ── 3. تنزيل وتفريغ الصوت مع domain prompt ───────────
        finfo = bot.get_file(message.voice.file_id)
        raw   = bot.download_file(finfo.file_path)
        buf   = io.BytesIO(raw); buf.name = "voice.ogg"

        # سياق المحادثة السابقة يساعد Whisper على فهم الكلمات الغامضة
        hist = _ai_history.get(cid, [])
        last_exchange = ""
        if hist:
            for msg in reversed(hist[-4:]):
                if msg["role"] == "assistant":
                    last_exchange = msg["content"][:120]
                    break
        whisper_prompt = WHISPER_DOMAIN_PROMPT
        if last_exchange:
            whisper_prompt += f". السياق السابق: {last_exchange}"

        def _do_transcribe(audio_buf, prompt):
            audio_buf.seek(0)
            return _ai_client.audio.transcriptions.create(
                model=WHISPER_MODEL, file=audio_buf,
                language="ar", prompt=prompt,
            )

        transcript = _do_transcribe(buf, whisper_prompt)
        user_text  = (transcript.text or "").strip()

        # إعادة محاولة واحدة بـ prompt قصير جداً → يعطي Whisper حرية أكبر
        if not user_text:
            logger.info("Whisper returned empty — retrying with minimal prompt")
            buf2 = io.BytesIO(raw); buf2.name = "voice.ogg"
            transcript = _do_transcribe(buf2, "مناقصات، أرقام، تواريخ، دلوقتي")
            user_text  = (transcript.text or "").strip()

        if not user_text:
            _track_error("Whisper Empty", f"file_size={file_size}")
            _send_voice_error(cid, "لم أتمكن من فهم الرسالة. تحدث بوضوح وجرّب مرة أخرى.")
            return

        # ── 4. عرض ما سُمع + إرسال "لحظة..." فوراً ──────────
        bot.send_message(cid, f"🎤 *سمعت:* _{user_text}_", parse_mode="Markdown")

        # إرسال صوت "لحظة من فضلك" فيما يُحضَّر الرد الحقيقي
        voice_name = _tts_voice_per_user.get(cid, "onyx")
        thinking   = _get_thinking_audio(voice_name)
        if thinking:
            tbuf = io.BytesIO(thinking); tbuf.name = "thinking.ogg"
            bot.send_voice(cid, tbuf)

        bot.send_chat_action(cid, 'record_voice')

        # ── 5. رد GPT مختصر ──────────────────────────────────
        reply = _ai_reply(cid, user_text, voice_mode=True)

        # ── 6. تقسيم وإرسال (جزء واحد أو جزآن بالتوازي) ────────
        parts = _split_for_tts(reply)
        if len(parts) == 2:
            # توليد الجزأين بالتوازي → أسرع بنسبة ~40%
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=2) as _ex:
                _futs  = [_ex.submit(_ai_speak, p, cid) for p in parts]
                audios = [f.result() for f in _futs]
            for part, audio_bytes in zip(parts, audios):
                if audio_bytes:
                    vbuf = io.BytesIO(audio_bytes); vbuf.name = "reply.ogg"
                    bot.send_voice(cid, vbuf)
                else:
                    bot.send_message(cid, part)
        else:
            audio_bytes = _ai_speak(parts[0], chat_id=cid)
            if audio_bytes:
                vbuf = io.BytesIO(audio_bytes); vbuf.name = "reply.ogg"
                bot.send_voice(cid, vbuf)
            else:
                bot.send_message(cid, parts[0])

    except Exception as e:
        logger.error(f"Voice handler error: {e}")
        _track_error("Voice Pipeline", str(e)[:120])   # ← تنبيه تلقائي
        bot.send_message(message.chat.id, f"⚠️ خطأ في معالجة الرسالة الصوتية.")


@bot.message_handler(func=lambda m: m.content_type == 'text' and not m.text.startswith('/'))
def handle_ai_text(message):
    """Catch-all: any non-command text → GPT reply (text or voice if voicemode on)."""
    if not is_authorized(message): return
    cid        = message.chat.id
    is_voice_m = cid in _voicemode_users

    bot.send_chat_action(cid, 'record_voice' if is_voice_m else 'typing')
    reply = _ai_reply(cid, message.text, voice_mode=is_voice_m)

    if is_voice_m:
        import io
        audio_bytes = _ai_speak(reply, chat_id=cid)
        if audio_bytes:
            vbuf = io.BytesIO(audio_bytes); vbuf.name = "reply.ogg"
            bot.send_voice(cid, vbuf)
            return
    bot.send_message(cid, reply)


# ============================================================
# 6. MAIN HEARTBEAT JOB (Runs every N minutes)
# ============================================================
def job_check_platform():
    """The primary scheduled heartbeat function."""
    # JOB OVERLAP GUARD: non-blocking acquire
    if not _job_lock.acquire(blocking=False):
        logger.warning("job_check_platform: Previous cycle still running - SKIPPING this trigger to prevent duplicate notifications.")
        return
    try:
        save_state(last_check_at=utc_now_iso(), last_result="running")
        if is_paused():
            logger.info("Scheduled check skipped because bot sync is paused by admin.")
            save_state(last_result="paused")
            return

        logger.info(f"{'='*20} Scheduled Check Started {'='*20}")

        # STEP A: تعطيل reverse_sync التلقائي — يُشغَّل فقط عند رفع Excel يدوياً
        # (تعطيل: كان يُعيد كتابة تعيينات المهندسين من Excel القديم كل دورة)
        # try:
        #     import reverse_sync_to_sql
        #     reverse_sync_to_sql.reverse_sync()
        #     logger.info("Excel -> SQL sync completed successfully.")
        # except Exception as e:
        #     logger.error(f"Automatic Excel Sync failed: {e}")

        # STEP B: Run the portal scraper and compare with Master DB
        import engine_core
        staged_count = engine_core.find_and_stage_changes()

        if staged_count == -1:
            # 🛡️ AUTONOMOUS RECOVERY (V4.1 Cyber-Resilience Feature)
            if not ALLOW_AUTONOMOUS_LOGIN:
                logger.error(
                    "Session failure detected, but Microsoft SSO auto-login is disabled. "
                    "Keeping MFA quiet; manual noVNC login is required if cookies expire."
                )
            else:
                logger.warning("Session failure detected. Attempting autonomous server-side refresh...")
                import subprocess
                try:
                    # Try to refresh cookies directly on the server (Watchdog Timeout = 4 minutes)
                    result = subprocess.run([sys.executable, "server_autonomous_sync.py"], capture_output=True, text=True, timeout=240)
                    if "Login Success" in result.stdout:
                        logger.info("✨ Autonomous recovery SUCCESS! Retrying scraper...")
                        staged_count = engine_core.find_and_stage_changes()
                    else:
                        logger.error(f"❌ Autonomous recovery failed: {result.stderr}")
                except subprocess.TimeoutExpired:
                    logger.error("🛑 WATCHDOG ALERT: Autonomous scraper froze for > 4 minutes! Killing process.")
                    if os.name == 'nt':
                        os.system("taskkill /F /IM chromedriver.exe >nul 2>&1")
                    else:
                        os.system("pkill -f chromedriver || true; pkill -f google-chrome || true")
                except Exception as e:
                    logger.error(f"Critical error during recovery attempt: {e}")

        if staged_count == -1:
            # STILL FAILED. Now we must alert the user (Human-in-the-loop fallback)
            send_session_expired_alert()
            save_state(last_result="session_failed")

        else:
            # Reset alert flag on success
            if SESSION_ALERT_FILE.exists():
                SESSION_ALERT_FILE.unlink()
            save_state(last_success_at=utc_now_iso(), last_result=f"ok:{staged_count}")
            ping_uptimerobot()

            if staged_count > 0:
                logger.info(f"Staging complete: {staged_count} new changes found.")
            else:
                logger.info("No new changes detected. System is up to date.")

        # STEP C: Notify manager via Telegram for any pending approvals.
        notify_pending_changes()

        logger.info(f"{'='*20} Scheduled Check Ended {'='*20}")
    finally:
        _job_lock.release()

def job_backup_system():
    """Daily backup: sends the latest DB and Excel to Telegram."""
    # ── Lock guard: prevents two concurrent calls (e.g. scheduler + manual /backup) ──
    if not _backup_lock.acquire(blocking=False):
        logger.info("Backup guard: another backup is already running. Skipping.")
        return

    today = time.strftime("%Y-%m-%d")
    try:
        # ── Date guard (re-checked inside lock) ──────────────────────────
        if load_state().get("last_backup_local_date") == today:
            logger.info(f"Backup guard: already sent today ({today}). Skipping duplicate.")
            return

        # ── CLAIM TODAY FIRST — before any sending ────────────────────────
        # Saving the date BEFORE we send prevents a restart-during-send from
        # causing the backup to be sent twice (different file sizes).
        save_state(
            last_backup_at=utc_now_iso(),
            last_backup_local_date=today,
            last_backup_result="sending"
        )

        logger.info("📦 Generating daily cloud backup...")

        # Ensure latest excel is generated
        db.export_master_excel()

        # Files to backup
        files = [
            (DB_PATH, "🗄️ نسخة احتياطية لقاعدة البيانات (SQLite)"),
            (BASE_DIR / "output" / "Master_Tenders.xlsx", "📊 نسخة احتياطية لملف الماستر (Excel)")
        ]

        for file_path, caption in files:
            if file_path.exists():
                with open(file_path, "rb") as f:
                    bot.send_document(CHAT_ID, f, caption=f"{caption}\n📅 بتاريخ: {time.strftime('%Y-%m-%d')}")
            else:
                raise FileNotFoundError(f"Backup file missing: {file_path}")

        logger.info("✅ Daily backup sent to Telegram.")
        save_state(
            last_backup_at=utc_now_iso(),
            last_backup_local_date=today,
            last_backup_result="ok"
        )
        if BACKUP_ALERT_FILE.exists():
            BACKUP_ALERT_FILE.unlink()
        return True

    except Exception as e:
        logger.error(f"❌ Backup Job failed: {e}")
        save_state(
            last_backup_at=utc_now_iso(),
            last_backup_local_date=today,
            last_backup_result=f"failed:{e}"
        )
        try:
            send_backup_failure_alert(e)
        except Exception as alert_error:
            logger.error(f"Could not send backup failure alert: {alert_error}")
        return False

    finally:
        _backup_lock.release()

def job_guarantee_reminder():
    """v5.6: تذكير يومي بالضمانات الابتدائية المستحقة (اليوم/غداً/بعد 3 أيام)."""
    if is_paused():
        return
    try:
        from datetime import datetime as _dt, timedelta as _td
        with db._get_connection() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS tender_guarantees (
                tender_row_id INTEGER PRIMARY KEY, required INTEGER DEFAULT 1,
                due_date TEXT DEFAULT '', status TEXT DEFAULT 'PENDING',
                notes TEXT DEFAULT '', updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            rows = conn.execute("""
                SELECT mt.id, mt.title, mt.owner, mt.submission_date,
                       COALESCE(g.status,'PENDING') gstatus, COALESCE(g.due_date,'') gdue
                FROM master_tenders mt
                LEFT JOIN tender_guarantees g ON g.tender_row_id = mt.id
                WHERE mt.status NOT IN ('CLOSED','REJECTED')
                  AND COALESCE(g.status,'PENDING') NOT IN ('READY','SUBMITTED','NOT_REQUIRED')
            """).fetchall()
        today = _dt.now().date()
        due_list = []
        for r in rows:
            due = None
            if r["gdue"]:
                try:
                    due = _dt.strptime(r["gdue"][:10], "%Y-%m-%d").date()
                except Exception:
                    pass
            if due is None:
                try:
                    due = _dt.strptime(str(r["submission_date"])[:10], "%Y-%m-%d").date() - _td(days=5)
                except Exception:
                    continue
            dleft = (due - today).days
            if dleft in (-1, 0, 1, 3):
                due_list.append((dleft, str(r["title"]), str(r["owner"] or ""), due.isoformat(), r["id"]))
        if not due_list:
            logger.info("Guarantee reminder: nothing due — skipped.")
            return
        due_list.sort()
        bot.send_message(CHAT_ID,
                         f"🛡️ *تذكير الضمانات الابتدائية* — {len(due_list)} مستحقة، حدّث الحالة بالأزرار:",
                         parse_mode="Markdown")
        _send_guarantee_cards(due_list)
        logger.info(f"Guarantee reminder sent: {len(due_list)} item(s).")
    except Exception as e:
        logger.error(f"Guarantee reminder failed: {e}")

def job_morning_briefing():
    """Daily 8:00 AM briefing: tenders due today/tomorrow, overdue, pending approvals."""
    logger.info("🌅 Running Morning Briefing...")
    import pandas as pd
    from datetime import datetime, timedelta

    _ARABIC_DAYS = {
        "Monday": "الإثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء",
        "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"
    }
    try:
        with db._get_connection() as conn:
            tenders = conn.execute(
                "SELECT title, submission_date, assigned_engineer FROM master_tenders WHERE status = 'InProgress'"
            ).fetchall()
            pending_count = conn.execute(
                "SELECT COUNT(*) FROM pending_changes WHERE status IN ('PENDING_APPROVAL','NOTIFIED')"
            ).fetchone()[0]

        now          = datetime.now()
        today_s      = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_s   = today_s + timedelta(days=1)
        day_after_s  = tomorrow_s + timedelta(days=1)

        due_today, due_tomorrow, overdue = [], [], []
        for t in tenders:
            try:
                d = pd.to_datetime(t['submission_date'], errors='coerce')
                if pd.notnull(d):
                    dn = d.replace(tzinfo=None)
                    if today_s <= dn < tomorrow_s:
                        due_today.append(t)
                    elif tomorrow_s <= dn < day_after_s:
                        due_tomorrow.append(t)
                    elif dn < today_s:
                        overdue.append(t)
            except Exception:
                pass

        day_ar = _ARABIC_DAYS.get(now.strftime("%A"), now.strftime("%A"))
        msg = f"🌅 *صباح الخير — {day_ar} {now.strftime('%Y-%m-%d')}*\n━━━━━━━━━━━━━━\n"

        if due_today:
            msg += f"🔴 *تسليمات اليوم ({len(due_today)}):*\n"
            for t in due_today:
                msg += f"  • _{t['title'][:55]}_\n    👷 {t['assigned_engineer'] or 'غير محدد'}\n"
        else:
            msg += "✅ لا تسليمات اليوم\n"

        msg += "\n"

        if due_tomorrow:
            msg += f"⚡ *تسليمات غداً ({len(due_tomorrow)}):*\n"
            for t in due_tomorrow:
                msg += f"  • _{t['title'][:55]}_\n    👷 {t['assigned_engineer'] or 'غير محدد'}\n"
        else:
            msg += "✅ لا تسليمات غداً\n"

        if overdue:
            msg += f"\n⚠️ *متأخرة ولم تُغلق ({len(overdue)}):*\n"
            for t in overdue[:3]:
                msg += f"  • _{t['title'][:55]}_\n"
            if len(overdue) > 3:
                msg += f"  _...و {len(overdue) - 3} أخرى_\n"

        if pending_count > 0:
            msg += f"\n🟡 *بانتظار اعتمادك: {pending_count} طلب* — /pending\n"

        msg += "\n💚 _فريق العروض الفنية — الرواف_"

        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        logger.info(f"Morning briefing sent: today={len(due_today)}, tomorrow={len(due_tomorrow)}, overdue={len(overdue)}, pending={pending_count}")

    except Exception as e:
        logger.error(f"Morning briefing failed: {e}")


def job_evening_alert():
    """Daily 5:00 PM alert — only fires when there are tenders due tomorrow."""
    logger.info("🌆 Running Evening Alert...")
    import pandas as pd
    from datetime import datetime, timedelta

    try:
        with db._get_connection() as conn:
            tenders = conn.execute(
                "SELECT title, submission_date, assigned_engineer FROM master_tenders WHERE status = 'InProgress'"
            ).fetchall()

        now         = datetime.now()
        tomorrow_s  = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_after_s = tomorrow_s + timedelta(days=1)

        due_tomorrow = []
        for t in tenders:
            try:
                d = pd.to_datetime(t['submission_date'], errors='coerce')
                if pd.notnull(d):
                    dn = d.replace(tzinfo=None)
                    if tomorrow_s <= dn < day_after_s:
                        due_tomorrow.append(t)
            except Exception:
                pass

        if not due_tomorrow:
            logger.info("Evening alert: no tenders due tomorrow — skipping.")
            return

        msg = (
            f"⏰ *تنبيه المساء — تسليمات الغد*\n"
            f"━━━━━━━━━━━━━━\n"
            f"غداً *{tomorrow_s.strftime('%Y-%m-%d')}* معنا *{len(due_tomorrow)}* تسليم:\n\n"
        )
        for t in due_tomorrow:
            msg += f"📌 *{t['title'][:60]}*\n   👷 {t['assigned_engineer'] or 'غير محدد'}\n\n"
        msg += "_تأكد من جاهزية الملفات الآن 💼_"

        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        logger.info(f"Evening alert sent: {len(due_tomorrow)} tenders due tomorrow.")

    except Exception as e:
        logger.error(f"Evening alert failed: {e}")


def job_deadline_sentinel():
    """Checks for tenders closing in the next 48 hours and sends alerts."""
    logger.info("⏰ Running Deadline Sentinel...")
    import pandas as pd
    from datetime import datetime, timedelta

    try:
        with db._get_connection() as conn:
            # Fetch all InProgress tenders
            tenders = conn.execute("SELECT title, submission_date, assigned_engineer FROM master_tenders WHERE status = 'InProgress'").fetchall()

        now = datetime.now()
        threshold = now + timedelta(hours=48)

        for t in tenders:
            try:
                # Robust date parsing
                close_date = pd.to_datetime(t['submission_date'], errors='coerce')
                if pd.notnull(close_date):
                    if now < close_date <= threshold:
                        #🚨 ALERT!
                        msg = (f"⏰ *إنذار الموعد النهائي (Deadline)!*\n"
                               f"━━━━━━━━━━━━━━\n"
                               f"📌 *المناقصة:* {t['title']}\n"
                               f"👷 *المسؤول:* {t['assigned_engineer']}\n"
                               f"⏱️ *تاريخ الإغلاق:* {t['submission_date']}\n\n"
                               f"⚡ الرجاء التأكد من جاهزية ملفات التقديم!")
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
            except: continue

    except Exception as e:
        logger.error(f"Deadline Sentinel failed: {e}")

# ============================================================
# 7. BACKGROUND SCHEDULER THREAD
# ============================================================
def schedule_runner():
    """Runs the schedule loop inside a background thread."""
    # ★ Run one check IMMEDIATELY on startup
    logger.info("Running initial startup check...")
    try:
        job_check_platform()
    except Exception as e:
        logger.error(f"Initial check failed: {e}")

    schedule.every(CHECK_INTERVAL).minutes.do(job_check_platform)

    # ★ Daily Cloud Backup at Midnight
    schedule.every().day.at("00:00").do(job_backup_system)

    # ★ Morning Briefing at 08:00 AM
    schedule.every().day.at("08:00").do(job_morning_briefing)
    schedule.every().day.at("08:30").do(job_guarantee_reminder)
    schedule.every().day.at("08:15").do(job_engineer_digests)

    # ★ Evening Alert at 17:00 (only fires if tenders due tomorrow)
    schedule.every().day.at("17:00").do(job_evening_alert)

    # ★ Daily cookie renewal reminder (fires only if cookies > 6 days old)
    schedule.every().day.at("10:00").do(job_cookie_reminder)

    # ★ Monthly PDF report on 1st of each month at 09:00
    schedule.every().day.at("09:00").do(
        lambda: job_monthly_report() if datetime.now().day == 1 else None
    )

    logger.info(f"Scheduler armed: every {CHECK_INTERVAL}min | Briefing 08:00 | EngDigest 08:15 | Guarantees 08:30 | Evening 17:00 | Backup 00:00 | CookieCheck 10:00 | MonthlyReport 1st@09:00.")
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logger.error(f"Schedule Runner error: {e}")
        time.sleep(1)

# Prevent multiple instances globally (Windows + Linux)


# ============================================================
# ANALYTICS COMMANDS — Phase 3
# ============================================================

@bot.message_handler(commands=['analytics'])
def handle_analytics(message):
    """تقارير analytics اليومية والأسبوعية والشهرية."""
    if not is_authorized(message): return
    parts = message.text.strip().split()
    sub = parts[1].lower() if len(parts) > 1 else ''

    try:
        from analytics_engine import (
            format_daily_report_for_telegram,
            format_weekly_report_for_telegram,
            AnalyticsEngine,
        )

        if sub == 'daily':
            msg = format_daily_report_for_telegram(db)
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')

        elif sub == 'weekly':
            msg = format_weekly_report_for_telegram(db)
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')

        elif sub == 'monthly':
            engine = AnalyticsEngine(db)
            report = engine.get_monthly_report()
            msg = (
                f"\U0001f4c5 *تقرير الشهر*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"\U0001f4cc {report.get('period', '')}\n\n"
                f"\U0001f7e2 مناقصات جديدة: {report.get('new_tenders', 0)}\n"
                f"✅ مناقصات مغلقة: {report.get('closed_tenders', 0)}\n"
                f"\U0001f4ca إجمالي نشطة: {report.get('total_active', 0)}\n"
            )
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')

        else:
            help_msg = (
                "\U0001f4ca *أوامر Analytics:*\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                "• `/analytics daily` — تقرير اليوم\n"
                "• `/analytics weekly` — تقرير الأسبوع\n"
                "• `/analytics monthly` — تقرير الشهر\n"
                "• `/trends` — تحليل القطاعات\n"
            )
            bot.send_message(message.chat.id, help_msg, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Analytics error: {e}", exc_info=True)
        bot.send_message(message.chat.id,
                         f"❌ خطأ في التحليل: `{str(e)[:150]}`",
                         parse_mode='Markdown')


@bot.message_handler(commands=['trends'])
def handle_trends(message):
    """تحليل اتجاهات القطاعات."""
    if not is_authorized(message): return
    try:
        from analytics_engine import AnalyticsEngine
        engine = AnalyticsEngine(db)
        trends = engine.get_sector_trends()

        msg = "\U0001f4c8 *تحليل اتجاهات القطاعات*\n━━━━━━━━━━━━━━━━━━━\n\n"

        sectors = trends.get('top_sectors', [])
        if sectors:
            msg += "\U0001f3c6 *أكثر القطاعات نشاطاً:*\n"
            for i, s in enumerate(sectors[:5], 1):
                msg += f"  {i}. {s.get('sector', '?')}: {s.get('count', 0)} مناقصة\n"
        else:
            msg += "لا توجد بيانات كافية للتحليل.\n"

        growth = trends.get('growth_rate')
        if growth is not None:
            icon = "\U0001f4c8" if growth >= 0 else "\U0001f4c9"
            msg += f"\n{icon} *معدل النمو:* {growth:+.1f}%\n"

        bot.send_message(message.chat.id, msg, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Trends error: {e}", exc_info=True)
        bot.send_message(message.chat.id,
                         f"❌ خطأ في التحليل: `{str(e)[:150]}`",
                         parse_mode='Markdown')


_lock_fd = None
def acquire_lock():
    global _lock_fd
    import tempfile
    lock_file = os.path.join(tempfile.gettempdir(), "alrawaf_bot.lock")
    try:
        if os.name == 'nt':
            import msvcrt
            _lock_fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
            msvcrt.locking(_lock_fd, msvcrt.LK_NBLCK, 1)
        else:
            if os.path.exists(lock_file):
                try:
                    with open(lock_file, "r") as f:
                        pid = int(f.read().strip())
                    os.kill(pid, 0)  # raises ProcessLookupError if dead
                    # Process IS alive — exit cleanly (exit 0 = not an error, prevents systemd restart loop)
                    logger.info(f"Instance guard: bot already running (PID={pid}). This extra start will exit cleanly.")
                    sys.exit(0)
                except ProcessLookupError:
                    pass  # Old process is dead — safe to take over
                except (ValueError, FileNotFoundError):
                    pass  # Corrupt/missing lock file — proceed
            _lock_fd = open(lock_file, "w")
            _lock_fd.write(str(os.getpid()))
            _lock_fd.flush()
    except Exception as e:
        logger.error(f"FATAL: Lock acquisition error ({e})! Exiting.")
        sys.exit(1)

# ============================================================
# 8. ENTRY POINT
# ============================================================
if __name__ == "__main__":
    acquire_lock()
    logger.info("Starting Al-Rawaf V4 - Professional Edition...")
    logger.info(f"Logs are being saved to: {LOG_DIR}")

    # Start background scheduler
    t = threading.Thread(target=schedule_runner, daemon=True)
    t.start()

    # Start Telegram polling with ISP-drop resilience
    logger.info("Bot is live and polling for Telegram callbacks...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.warning(f"Telegram connection dropped. Reconnecting in 5s... ({e})")
            time.sleep(5)
