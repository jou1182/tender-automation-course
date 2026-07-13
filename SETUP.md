# دليل التوسيم والتنصيب — نظام متابعة المناقصات

> حوّل هذا النظام لأي شركة مقاولات خلال ساعة واحدة، بلا لمس سطر كود.
> الأساس: كل ما يميّز شركتك يعيش في **ملف واحد**: `company_profile.json`.

---

## 0) نظرة عامة سريعة

| الطبقة | الملف/الخدمة | الدور |
|---|---|---|
| الهوية | `company_profile.json` | الاسم، الألوان، فريق المهندسين، رابط المنصة — **حرّره أولاً** |
| الأسرار | `.env` (من `.env.example`) | التوكنات وكلمات المرور — لا يُرفع لأي مستودع عام |
| السحب | `selectors.json` | محددات صفحة تسجيل الدخول بمنصة العميل |
| التشغيل | `bot_daemon.py` + `web_dashboard.py` | البوت (Telegram) واللوحة (Flask) — خدمتان مستقلتان |
| القاعدة | `output/tenders.db` | SQLite — تُنشأ فارغة عبر `provision_instance.py` |

---

## 1) المتطلبات

```yaml
Python: 3.12+
نظام السيرفر: Ubuntu 22.04+ (أو أي Linux به systemd)
Chrome/Chromium: فقط إن استخدمت السحب عبر Selenium (fallback نادر)
```

---

## 2) خطوة 1 — حرّر هوية الشركة

افتح `company_profile.json` وعدّل:

```json
{
  "name_ar":        "اسم الشركة بالعربي",
  "name_en":        "ENGLISH NAME",
  "short_ar":       "الاسم المختصر",
  "system_title":   "نظام [الشركة]",
  "system_subtitle":"لوحة متابعة المنافسات",
  "team_ar":        "اسم فريقك (مثال: فريق العروض الفنية)",
  "department_ar":  "اسم القسم",

  "portal_url":            "https://بوابة-عميلك.com",
  "portal_export_path":    "/مسار/تصدير/الإكسل",
  "portal_cookie_domain":  ".بوابة-عميلك.com",

  "footer_owner": "اسمك",
  "footer_url":   "موقعك أو رابط تواصل",

  "theme_bg":        "#RRGGBB",   ← خلفية الصفحة
  "theme_card":      "#RRGGBB",   ← بطاقات فاتحة
  "theme_hover":     "#RRGGBB",
  "theme_head":      "#RRGGBB",   ← شريط رأس الجداول
  "theme_primary":   "#RRGGBB",   ← اللون الأساسي (شعار الشركة)
  "theme_primary_l": "#RRGGBB",   ← درجة أفتح من الأساسي
  "theme_primary_d": "#RRGGBB",   ← درجة أغمق من الأساسي

  "engineers": [
    {"name": "اسم المهندس 1", "capacity": 5},
    {"name": "اسم المهندس 2", "capacity": 5}
  ]
}
```

**نصيحة الألوان:** اختر `theme_primary` = لون شعار الشركة، ثم درجة أفتح لـ`_l` وأغمق لـ`_d` (فرق ~20% إضاءة). `theme_bg`/`theme_card`/`theme_hover`/`theme_head` درجات فاتحة متجاورة تلائم القراءة (تجنّب تباين حاد يرهق العين).

> ⚠️ **ما لا يُغيَّر هنا:** ألوان الدلالة (أحمر=خطر، أخضر=نجاح، أزرق=معلومة) ثابتة عالمياً بقصد — لا تخصّص لكل شركة. وصفحات بوابة المهندسين تستخدم ثيماً داكناً منفصلاً بتصميم متعمد.

---

## 3) خطوة 2 — أنشئ قاعدة بيانات نظيفة

```bash
cd V4_Super_System
python provision_instance.py output/tenders.db
```

هذا السكريبت:
- يبني الهيكل الكامل (جداول المنافسات، المهندسين، الإعدادات...)
- يزرع هوية الشركة وفريق المهندسين **من `company_profile.json`**
- **صفر بيانات منافسات** — سلة فارغة جاهزة

**حواجز أمان مدمجة:** يرفض الكتابة فوق قاعدة بيانات حية أو ملف موجود مسبقاً — لن يحذف بياناتك بالخطأ.

---

## 4) خطوة 3 — الأسرار (`.env`)

```bash
cp .env.example .env
```

ثم افتح `.env` واملأ (راجع التعليقات بداخله لكل مفتاح):

| المفتاح | من أين تحصل عليه |
|---|---|
| `TELEGRAM_TOKEN` | حدّث بوتاً جديداً عبر `@BotFather` في تيليجرام |
| `CHAT_ID` | أضف البوت لمجموعتك، ثم استخدم `@userinfobot` أو API لمعرفة معرّف المجموعة |
| `DASHBOARD_PASSWORD` / `ADMIN_PASSWORD` | اختر كلمتي مرور قويتين |
| `OPENAI_API_KEY` | من [platform.openai.com](https://platform.openai.com) |
| `PORTAL_URL` | رابط منصة العميل الداخلية |
| `SERVER_IP` / `SERVER_USER` / `SERVER_PASS` | بيانات سيرفر VPS الخاص بك |

---

## 5) خطوة 4 — محدّدات منصة العميل (`selectors.json`)

كل منصة تسجيل دخول مختلفة قليلاً. افحص صفحة الدخول (أدوات المطوّر F12) وحدّد:

```json
{
  "portal_url": "من company_profile.json (كرّرها هنا للمصدر المباشر)",
  "login_path": "/مسار/صفحة/الدخول/",
  "export_path": "/مسار/تصدير/الإكسل/",
  "selectors": {
    "username_field": {"by": "name", "value": "اسم-حقل-المستخدم"},
    "password_field": {"by": "name", "value": "اسم-حقل-كلمة-المرور"},
    "submit_button":  {"by": "xpath", "value": "//button[@type='submit']"}
  }
}
```

> إن كانت منصة العميل تدعم السحب المباشر عبر ملفات تعريف الارتباط (كما في نظام الرواف)، فلن تحتاج Selenium إطلاقاً — راجع `extract_and_upload_cookies.py`.

---

## 6) خطوة 5 — التثبيت المحلي (بيئة العمل)

```bash
python -m venv .venv
.venv\Scripts\activate          # ويندوز
pip install -r requirements.txt
```

اختبر محلياً:
```bash
python -m py_compile web_dashboard.py bot_daemon.py
python tests\run_all.py          # بوابة الجودة — يجب أن تنجح كل الاختبارات
```

---

## 7) خطوة 6 — نشر السيرفر (VPS)

### أ) البيئة على السيرفر
```bash
mkdir -p /opt/APP_NAME && cd /opt/APP_NAME
python3.12 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### ب) خدمتا systemd (بوت + لوحة)

`/etc/systemd/system/APP-bot.service`:
```ini
[Unit]
Description=Tender Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/opt/APP_NAME
ExecStart=/opt/APP_NAME/start_bot.sh
Restart=on-failure
RestartSec=15
StandardOutput=append:/opt/APP_NAME/logs/systemd_stdout.log
StandardError=append:/opt/APP_NAME/logs/systemd_stderr.log

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/APP-dashboard.service`:
```ini
[Unit]
Description=Tender Dashboard
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/opt/APP_NAME
EnvironmentFile=/opt/APP_NAME/.env
ExecStart=/opt/APP_NAME/venv/bin/python3.12 /opt/APP_NAME/web_dashboard.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/opt/APP_NAME/logs/dashboard_systemd.log
StandardError=append:/opt/APP_NAME/logs/dashboard_systemd.log

[Install]
WantedBy=multi-user.target
```

`start_bot.sh` (يحمّل `.env` بشكل صحيح قبل تشغيل البوت):
```bash
#!/bin/bash
set -a
source /opt/APP_NAME/.env
set +a
exec /opt/APP_NAME/venv/bin/python3.12 /opt/APP_NAME/bot_daemon.py
```

```bash
chmod +x start_bot.sh
sudo systemctl daemon-reload
sudo systemctl enable --now APP-bot APP-dashboard
```

### ج) الوصول للوحة عبر رابط عام (Cloudflare Tunnel)
1. أنشئ نفقاً من Cloudflare Zero Trust Dashboard واربطه بنطاقك
2. ثبّت `cloudflared` كخدمة systemd (`cloudflared service install <TOKEN>`)
3. اللوحة تبقى محصورة بـ `127.0.0.1` داخلياً (`_ALLOWED_HOSTS` في `web_dashboard.py`) — الوصول الوحيد عبر النفق

### د) الحراسة الذاتية (اختياري لكن موصى به بشدة)
انسخ `bot_watchdog.sh` و`backup_sentinel.sh` وسجّلهما في `crontab -e` **لمستخدم root**:
```cron
*/5 * * * * /opt/APP_NAME/bot_watchdog.sh >> /opt/APP_NAME/logs/watchdog.log 2>&1
15 3 * * * /opt/APP_NAME/backup_sentinel.sh >> /opt/APP_NAME/logs/watchdog.log 2>&1
0 2 * * * /opt/APP_NAME/venv/bin/python3 /opt/APP_NAME/elrawaf_backup.py >> /opt/APP_NAME/logs/db_backup.log 2>&1
```
> عدّل المسارات `/opt/APP_NAME` داخل السكريبتين نفسيهما قبل النسخ.

---

## 8) قائمة التحقق النهائية ✅

- [ ] `company_profile.json` يعكس هوية الشركة الجديدة بالكامل
- [ ] `python provision_instance.py` نُفّذ — قاعدة بيانات فارغة بالمهندسين الصحيحين
- [ ] `.env` مملوء بكل الأسرار (لا مفاتيح فارغة حرجة)
- [ ] `selectors.json` يطابق صفحة دخول منصة العميل
- [ ] `python tests\run_all.py` ينجح بالكامل (بوابة الجودة)
- [ ] خدمتا systemd تعملان: `systemctl status APP-bot APP-dashboard`
- [ ] `/healthz` يرجع `200 OK` (`curl https://دومينك/healthz`)
- [ ] رسالة تجريبية وصلت من البوت للمجموعة (`/start` في تيليجرام)
- [ ] تسجيل الدخول للوحة يعمل بكلمتي المرور الجديدتين
- [ ] الحارس الذاتي والرقيب مُجدولان في `crontab`

---

## 9) الدعم والمرجع

- التوثيق التقني الكامل: `V4_MASTER_DOCUMENTATION.md` و`V4_SSOT_Architecture.md`
- سجل كل التغييرات المعمارية: قسم "Maintenance Log" في `V4_SSOT_Architecture.md`
- أوامر البوت: `/help` داخل تيليجرام بعد التشغيل

---

*هذا الدليل جزء من "التهيئة النظيفة" — الفصل الكامل بين منطق النظام وبيانات أي شركة بعينها.*
