# -*- coding: utf-8 -*-
"""HTML templates for the public dashboard (extracted verbatim from
web_dashboard.py on 2026-07-05 - same pattern as admin_templates.py).
Rendered with flask.render_template_string by web_dashboard.py."""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ co.short_ar }} — دخول</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#b88800;font-family:'Tajawal',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center}
  .wrap{width:100%;max-width:360px;padding:1rem}
  .card{background:#fffde8;border:1px solid #c8a028;border-top:3px solid #8a4800;border-radius:12px;padding:2.2rem 1.75rem;text-align:center;box-shadow:0 8px 32px rgba(100,60,0,.18);position:relative}
  .logo{font-size:2.6rem;margin-bottom:.6rem}
  h1{color:#1e1404;font-size:1.3rem;font-weight:900;margin-bottom:.25rem;letter-spacing:-.3px}
  p{color:#7a5e28;font-size:.85rem;margin-bottom:1.5rem}
  .err{background:rgba(176,40,40,.08);border:1px solid rgba(176,40,40,.25);color:#b02828;border-radius:8px;padding:.6rem;font-size:.85rem;margin-bottom:1rem}
  input[type=password]{width:100%;background:#fdf5c0;border:1px solid #c8a028;color:#1e1404;border-radius:8px;padding:.75rem 1rem;font-family:'Tajawal',sans-serif;font-size:1rem;text-align:center;outline:none;transition:.2s;margin-bottom:.75rem}
  input[type=password]:focus{border-color:#8a4800;box-shadow:0 0 0 3px rgba(138,72,0,.15)}
  button{width:100%;background:#8a4800;border:none;color:#fff;border-radius:8px;padding:.8rem;font-family:'Tajawal',sans-serif;font-size:1rem;font-weight:900;cursor:pointer;transition:.2s;letter-spacing:.3px}
  button:hover{background:#a85a00}
  .version{color:#9a7838;font-size:.72rem;margin-top:1.25rem}
  .copyright{color:#9a7838;font-size:.68rem;margin-top:.4rem}
  .copyright a{color:#7a5e28;text-decoration:none}
</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <div class="logo">
      <img src="{{ logo_uri }}" alt="{{ co.name_ar }}" style="width:170px;height:auto;display:block;margin:0 auto 6px;mix-blend-mode:multiply">
    </div>
    <h1>{{ co.system_title }}</h1>
    <p>لوحة متابعة المنافسات</p>
    {% if error %}<div class="err">{{ error }}</div>{% endif %}
{% if expired %}<div style="background:rgba(184,106,0,.12);border:1px solid rgba(184,106,0,.4);color:#8a4800;
  border-radius:9px;padding:.6rem .9rem;font-size:.85rem;font-weight:700;margin-bottom:.8rem;text-align:center">
  ⏳ انتهت الجلسة لعدم النشاط لأكثر من ساعتين — فضلاً سجّل الدخول من جديد</div>{% endif %}
{% if reset_ok %}<div style="background:rgba(26,107,60,.08);border:1px solid rgba(26,107,60,.3);color:#1a6b3c;
  border-radius:8px;padding:.6rem;font-size:.85rem;margin-bottom:1rem">تم تحديث كلمة المرور بنجاح — سجّل الدخول بها الآن ✅</div>{% endif %}
    <form method="POST">
      <input type="password" name="password" placeholder="كلمة المرور" autofocus>
      <button type="submit">دخول</button>
    </form>
    <a href="/forgot" style="display:block;margin-top:.7rem;color:#8a4800;font-size:.8rem;text-decoration:none;font-weight:700">نسيت كلمة المرور؟</a>
    <div class="version">{{ co.system_title }}</div>
    <div class="copyright">Copyright 2026 &copy; Your Name &mdash; <a href="https://example.com" target="_blank">example.com</a></div>
    <div style="margin-top:1.2rem;padding-top:.85rem;border-top:1px solid rgba(200,160,40,.25);text-align:center"><a href="/admin/login" style="display:inline-flex;align-items:center;gap:.4rem;color:#8a4800;font-size:.8rem;font-weight:700;text-decoration:none;padding:.4rem .9rem;border-radius:8px;border:1px solid rgba(138,72,0,.3);background:rgba(138,72,0,.06);transition:.2s" onmouseover="this.style.background='rgba(138,72,0,.14)';this.style.borderColor='rgba(138,72,0,.6)'" onmouseout="this.style.background='rgba(138,72,0,.06)';this.style.borderColor='rgba(138,72,0,.3)'">&#9881; الدخول إلى لوحة التحكم</a></div>
  </div>
</div>

<script>
function toggleLock() {
  const btn = document.getElementById('lockBtn');
  btn.disabled = true;
  fetch('/api/tender/' + TID + '/toggle-lock', {method:'POST', headers:{'Content-Type':'application/json'}})
    .then(r => r.json())
    .then(d => {
      if (d.ok) {
        btn.textContent = d.locked ? '🔒 مقفول — انقر للفتح' : '🔓 مفتوح — انقر للقفل';
        btn.style.background = d.locked ? 'rgba(255,180,0,.18)' : 'rgba(255,255,255,.08)';
        toast(d.message);
        // تحديث الأيقونة في العنوان
        const chip = document.querySelector('.echip');
        if (chip && chip.nextSibling) {
          const icon = chip.nextElementSibling;
          if (icon) icon.textContent = d.locked ? '🔒' : '🔓';
        }
      } else {
        toast('خطأ: ' + (d.error || 'غير معروف'), 1);
      }
    })
    .catch(() => toast('خطأ في الاتصال', 1))
    .finally(() => { btn.disabled = false; });
}
</script>
</body></html>"""

DASH_FORGOT_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ co.short_ar }} — استعادة كلمة المرور</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#b88800;font-family:'Tajawal',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center}
.wrap{width:100%;max-width:390px;padding:1rem}
.card{background:#fffde8;border:1px solid #c8a028;border-top:3px solid #8a4800;border-radius:12px;padding:2.2rem 1.75rem;text-align:center;box-shadow:0 8px 32px rgba(100,60,0,.18)}
.badge{display:inline-block;background:rgba(138,72,0,.1);border:1px solid rgba(138,72,0,.3);color:#8a4800;font-size:.72rem;font-weight:700;padding:3px 12px;border-radius:20px;margin-bottom:1.2rem;letter-spacing:.8px}
h1{color:#1e1404;font-size:1.15rem;font-weight:900;margin-bottom:.3rem}
.sub{color:#7a5e28;font-size:.82rem;margin-bottom:1.6rem;line-height:1.6}
.err{background:rgba(176,40,40,.08);border:1px solid rgba(176,40,40,.25);color:#b02828;border-radius:8px;padding:.65rem;font-size:.83rem;margin-bottom:1rem}
.field{margin-bottom:.85rem;text-align:right}
label{display:block;font-size:.75rem;font-weight:700;color:#5a3810;margin-bottom:.3rem}
input{width:100%;background:#fdf5c0;border:1px solid #c8a028;color:#1e1404;border-radius:8px;padding:.7rem 1rem;font-family:'Tajawal',sans-serif;font-size:.95rem;outline:none;transition:.2s}
input:focus{border-color:#8a4800;box-shadow:0 0 0 3px rgba(138,72,0,.15)}
.btn{width:100%;background:#8a4800;border:none;color:#fff;border-radius:8px;padding:.8rem;font-family:'Tajawal',sans-serif;font-size:1rem;font-weight:900;cursor:pointer;transition:.2s;margin-top:.3rem}
.btn:hover{background:#a85a00}
.back{display:block;margin-top:1.2rem;color:#9a7838;font-size:.78rem;text-decoration:none}
</style>
</head>
<body>
<div class="wrap"><div class="card">
  <img src="{{ logo_uri }}" alt="{{ co.name_ar }}" style="width:110px;height:auto;margin:0 auto .9rem;display:block;mix-blend-mode:multiply">
  <div class="badge">&#128274; استعادة كلمة المرور</div>
  <h1>استعادة كلمة مرور الدخول</h1>
  {% if not sent %}
    <p class="sub">سيُرسل كود تحقق من 6 أرقام إلى حساب تليجرام الخاص بالمالك فقط، صالح لمدة 10 دقائق.</p>
    {% if error %}<div class="err">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="hidden" name="action" value="send">
      <button type="submit" class="btn">إرسال الكود إلى تليجرام</button>
    </form>
  {% else %}
    <p class="sub">تم إرسال الكود إلى تليجرام (إن كان الإعداد مفعّلاً). أدخله مع كلمة المرور الجديدة:</p>
    {% if error %}<div class="err">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="hidden" name="action" value="verify">
      <input type="hidden" name="token" value="{{ token }}">
      <div class="field"><label>كود التحقق</label>
        <input type="text" name="code" inputmode="numeric" maxlength="6" dir="ltr" autofocus></div>
      <div class="field"><label>كلمة المرور الجديدة</label>
        <input type="password" name="new_pwd" placeholder="8 أحرف على الأقل"></div>
      <div class="field"><label>تأكيد كلمة المرور الجديدة</label>
        <input type="password" name="new_pwd2"></div>
      <button type="submit" class="btn">تعيين كلمة المرور &#8592;</button>
    </form>
  {% endif %}
  <a href="/login" class="back">&#8592; العودة لصفحة الدخول</a>
</div></div>
</body></html>"""


TENDER_DETAIL_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>تفاصيل — {{ t.title[:40] }}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css">
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:{{ co.theme_bg }};--card:{{ co.theme_card }};--hover:{{ co.theme_hover }};--head:{{ co.theme_head }};
  --border:#c8a028;--border2:#a07820;--text:#1e1404;--sub:#4a3810;--muted:#7a5e28;
  --amber:{{ co.theme_primary }};--amber-l:{{ co.theme_primary_l }};--amber-d:{{ co.theme_primary_d }};
  --blue:#1a5a9a;--green:#247848;--red:#b02828;--yellow:#a06800;--orange:#a84e1a;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:'Tajawal',sans-serif;font-size:14px;margin:0}

/* TOP BAR */
.topbar{background:linear-gradient(135deg,#5a2800 0%,#8a4800 55%,#b06000 100%);
  border-bottom:2px solid #6e3200;padding:.9rem 1.5rem;
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:200;color:#fff4d8}
.brand{font-weight:900;font-size:1.1rem;display:flex;align-items:center;gap:.55rem;color:#fff4d8}
.tnav a{color:rgba(255,215,140,.8);text-decoration:none;font-size:.83rem;
  padding:.3rem .65rem;border-radius:7px;transition:.15s}
.tnav a:hover{background:rgba(255,255,255,.12);color:#fff}
.tnav a.hi{color:#ffd060}
.tnav{display:flex;align-items:center;gap:.5rem}

/* LAYOUT */
.page{padding:1.25rem 1.5rem;max-width:1000px;margin:0 auto}

/* INFO CARD */
.info-card{background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1.5rem 1.75rem;margin-bottom:1rem;
  border-top:3px solid var(--amber)}
.info-card h2{font-size:1.2rem;font-weight:800;color:var(--text);margin-bottom:1rem;
  padding-bottom:.6rem;border-bottom:1px solid var(--border)}

/* SECTION PANEL */
.spanel{background:var(--card);border:1px solid var(--border);border-radius:12px;
  overflow:hidden;margin-bottom:1rem}
.sp-head{background:var(--head);border-bottom:1px solid var(--border);
  border-right:3px solid var(--amber);padding:.7rem 1rem;
  font-weight:700;font-size:.88rem;display:flex;align-items:center;gap:.5rem}
.sp-body{padding:1.1rem 1.25rem}

/* META GRID */
.mg{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.75rem}
.mrow{display:flex;flex-direction:column;gap:.2rem}
.mlbl{color:var(--muted);font-size:.74rem;font-weight:600;letter-spacing:.4px;text-transform:uppercase}
.mval{color:var(--text);font-weight:500;font-size:.9rem}

/* DAY BADGE */
.db{display:inline-flex;align-items:center;padding:2px 10px;border-radius:20px;font-size:.78rem;font-weight:700}
.db-r{background:rgba(248,81,73,.15);color:var(--red);border:1px solid rgba(248,81,73,.3)}
.db-w{background:rgba(227,179,65,.15);color:var(--yellow);border:1px solid rgba(227,179,65,.3)}
.db-g{background:rgba(63,185,80,.15);color:var(--green);border:1px solid rgba(63,185,80,.3)}
.db-s{background:rgba(139,148,158,.1);color:var(--muted);border:1px solid var(--border)}

/* ENGINEER CHIP */
.echip{display:inline-block;padding:3px 10px;background:rgba(200,135,60,.1);
  color:var(--amber-l);border-radius:5px;font-size:.82rem;font-weight:600;
  border:1px solid rgba(200,135,60,.25)}

/* CHECKLIST */
.chk-item{display:flex;align-items:flex-start;gap:.75rem;padding:.8rem .9rem;
  background:var(--hover);border:1px solid var(--border);border-radius:9px;
  margin-bottom:.6rem;transition:.18s;cursor:pointer}
.chk-item:hover{border-color:var(--border2);background:#fef8c8}
.chk-item.done{background:rgba(36,120,72,.06);border-color:rgba(36,120,72,.25)}
.chk-item.done .chk-lbl{color:var(--green)}
.chk-box{width:22px;height:22px;flex-shrink:0;accent-color:var(--green);cursor:pointer;margin-top:1px}
.chk-lbl{font-weight:600;font-size:.92rem;margin-bottom:.15rem}
.chk-sub{font-size:.78rem;color:var(--muted);margin-top:.1rem}
.chk-date{display:none;margin-top:.5rem}
.chk-date.show{display:block}
.chk-date input{background:var(--bg);border:1px solid var(--border);color:var(--text);
  border-radius:7px;padding:.35rem .65rem;font-family:'Tajawal',sans-serif;font-size:.83rem;outline:none;transition:.2s}
.chk-date input:focus{border-color:var(--amber);box-shadow:0 0 0 2px rgba(200,135,60,.12)}

/* EXTENSION BADGE */
.ext-badge{display:inline-flex;align-items:center;gap:.35rem;padding:2px 10px;
  background:rgba(168,78,26,.1);color:var(--orange);border-radius:20px;
  font-size:.76rem;font-weight:700;border:1px solid rgba(168,78,26,.25)}

/* FORM ELEMENTS */
.form-control,.form-select{background:var(--bg)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;border-radius:8px;font-family:'Tajawal',sans-serif}
.form-control:focus,.form-select:focus{border-color:var(--amber)!important;
  box-shadow:0 0 0 3px rgba(200,135,60,.12)!important}
.form-label{color:var(--muted);font-size:.8rem;font-weight:600;letter-spacing:.3px;margin-bottom:.3rem}
textarea.form-control{resize:vertical;min-height:110px}

/* SAVE BUTTON */
.save-btn{background:var(--amber);border:none;color:#fff;border-radius:9px;
  padding:.7rem 2rem;font-family:'Tajawal',sans-serif;font-size:1rem;font-weight:800;
  cursor:pointer;transition:.18s;letter-spacing:.2px;display:inline-flex;align-items:center;gap:.5rem}
.save-btn:hover{background:var(--amber-l);transform:translateY(-1px);box-shadow:0 4px 16px rgba(100,60,0,.22)}
.save-btn:active{transform:scale(.96)}
.save-btn:disabled{opacity:.6;cursor:not-allowed;transform:none}

/* TOAST */
#tw{position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%);z-index:9999}
.tmsg{background:#e8f5ea;color:var(--green);border:1px solid rgba(36,120,72,.3);
  padding:.6rem 1.5rem;border-radius:10px;font-size:.87rem;
  box-shadow:0 6px 28px rgba(100,60,0,.15);opacity:0;
  transform:translateY(12px) scale(.96);
  transition:opacity .28s,transform .32s cubic-bezier(.22,1,.36,1);
  pointer-events:none;white-space:nowrap}
.tmsg.err{background:#fde8e8;color:var(--red);border-color:rgba(176,40,40,.3)}
.tmsg.on{opacity:1;transform:translateY(0) scale(1)}

/* ENTRANCE */
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.info-card,.spanel{opacity:0}

/* MOBILE */
@media(max-width:600px){
  .page{padding:.75rem .7rem}
  .info-card{padding:1rem 1rem}
  .sp-body{padding:.85rem .9rem}
  .mg{grid-template-columns:1fr 1fr}
  .save-btn{width:100%;justify-content:center}
}

/* PRINT */
@media print{
  .topbar,.save-btn,#tw{display:none!important}
  body{background:#fff!important;color:#000!important}
  .info-card,.spanel{background:#fff!important;border-color:#ccc!important;opacity:1!important}
  .sp-head{background:#f0f0f0!important}
  .chk-item{background:#f8f8f8!important}
}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <div class="brand">
    <span style="font-size:1.2rem">📋</span>
    <span>تفاصيل المنافسة</span>
  </div>
  <div class="tnav">
    <a href="/" class="hi">← اللوحة الرئيسية</a>
    <a href="/logout">خروج ↩</a>
  </div>
</div>

<div class="page">

  <!-- TENDER INFO -->
  <div class="info-card">
    <h2>
      {{ t.icon if t.icon else '' }}
      {% if t.missing_seen_count and t.missing_seen_count > 0 %}
      <span style="background:rgba(139,148,158,.1);color:var(--muted);border-radius:5px;
            padding:2px 7px;font-size:.65rem;vertical-align:middle;margin-left:.5rem">غائبة {{ t.missing_seen_count }}x</span>
      {% endif %}
      {{ t.title }}
    </h2>
    <div class="mg">
      <div class="mrow">
        <span class="mlbl">رقم المنافسة</span>
        <span class="mval">{{ t.tender_id or '—' }}</span>
      </div>
      <div class="mrow">
        <span class="mlbl">الجهة المالكة</span>
        <span class="mval">{{ t.owner or '—' }}</span>
      </div>
      <div class="mrow">
        <span class="mlbl">تاريخ الإغلاق</span>
        <span class="mval">
          {{ (t.submission_date or '')[:10] or '—' }} <span title="{{ 'تاريخ مقفول — لن يتغير تلقائياً' if t.date_locked else 'تاريخ مفتوح — قد يتغير بتغيير المنصة' }}" style="cursor:default;font-size:.85em">{{ '🔒' if t.date_locked else '🔓' }}</span>
          {% if days_left is not none %}
          &nbsp;
          {% if badge=='danger' %}{% set dc='db-r' %}{% elif badge=='warning' %}{% set dc='db-w' %}{% elif badge=='success' %}{% set dc='db-g' %}{% else %}{% set dc='db-s' %}{% endif %}
          <span class="db {{ dc }}">
            {% if days_left < 0 %}منتهية
            {% elif days_left == 0 %}اليوم
            {% elif days_left == 1 %}غداً
            {% else %}{{ days_left }} يوم{% endif %}
          </span>
          {% endif %}
        </span>
      </div>
      <div class="mrow">
        <span class="mlbl">المهندس المسؤول</span>
        <span class="mval">
          {% if t.assigned_engineer %}<span class="echip">{{ t.assigned_engineer }}</span> <span title="{{ 'تعيين مقفول — لا يتغير تلقائياً' if t.engineer_locked else 'تعيين مفتوح — قد يتغير تلقائياً' }}" style="cursor:default;font-size:.9em">{{ '🔒' if t.engineer_locked else '🔓' }}</span>
          {% else %}<span style="color:var(--muted)">غير معيّن</span>{% endif %}
        </span>
      </div>
      <div class="mrow">
        <span class="mlbl"></span>
        <span class="mval">
          <button onclick="location.href='/?edit={{ t.id }}'" style="background:rgba(200,144,64,.12);color:var(--yellow);border:1px solid rgba(200,144,64,.35);border-radius:7px;padding:.3rem .8rem;font-size:.78rem;font-weight:700;cursor:pointer;font-family:'Tajawal',sans-serif">✏️ تعديل تاريخ الإغلاق / المهندس</button>
        </span>
      </div>
      <div class="mrow">
        <span class="mlbl">نوع الأعمال</span>
        <span class="mval">{{ t.business_type or '—' }}</span>
      </div>
      <div class="mrow">
        <span class="mlbl">القطاع</span>
        <span class="mval">{{ t.sector or '—' }}</span>
      </div>
      <div class="mrow">
        <span class="mlbl">الحالة</span>
        <span class="mval">{{ t.status or '—' }}</span>
      </div>
      {% if t.nt_extended %}
      <div class="mrow">
        <span class="mlbl">التمديدات</span>
        <span class="mval">
          <span class="ext-badge">🔄 مُمدَّدة {{ t.nt_ext_count }}x</span>
        </span>
      </div>
      {% endif %}
    </div>
  </div>

  <div class="row g-3">
    <div class="col-12 col-md-7">

      <!-- CHECKLIST -->
      <div class="spanel mb-3">
        <div class="sp-head">✅ قائمة المهام</div>
        <div class="sp-body">

          <!-- 1. Submitted to Review -->
          <div class="chk-item {% if t.nt_s_review %}done{% endif %}" onclick="toggleChk('s_review',this)">
            <input type="checkbox" class="chk-box" id="ck_s_review" {% if t.nt_s_review %}checked{% endif %} onclick="event.stopPropagation()">
            <div style="flex:1">
              <div class="chk-lbl">📄 تم تقديم المنافسة لقسم المراجعة</div>
              <div class="chk-sub">وثائق المنافسة قُدِّمت لمراجعة المستندات</div>
              <div class="chk-date {% if t.nt_review_date %}show{% endif %}" id="dt_s_review">
                <label class="form-label">تاريخ التقديم للمراجعة</label>
                <input type="date" id="date_s_review" class="form-control" style="max-width:220px"
                       value="{{ t.nt_review_date[:10] if t.nt_review_date else '' }}"
                       onclick="event.stopPropagation()">
              </div>
            </div>
          </div>

          <!-- 2. Submitted to Upload Dept -->
          <div class="chk-item {% if t.nt_s_upload %}done{% endif %}" onclick="toggleChk('s_upload',this)">
            <input type="checkbox" class="chk-box" id="ck_s_upload" {% if t.nt_s_upload %}checked{% endif %} onclick="event.stopPropagation()">
            <div style="flex:1">
              <div class="chk-lbl">📤 تم الرفع لقسم إدارة رفع المنافسات</div>
              <div class="chk-sub">ملف المنافسة سُلِّم لقسم الرفع على المنصة</div>
              <div class="chk-date {% if t.nt_upload_date %}show{% endif %}" id="dt_s_upload">
                <label class="form-label">تاريخ الرفع للقسم</label>
                <input type="date" id="date_s_upload" class="form-control" style="max-width:220px"
                       value="{{ t.nt_upload_date[:10] if t.nt_upload_date else '' }}"
                       onclick="event.stopPropagation()">
              </div>
            </div>
          </div>

          <!-- 3. Uploaded to Platform -->
          <div class="chk-item {% if t.nt_uploaded %}done{% endif %}" onclick="toggleChk('uploaded',this)">
            <input type="checkbox" class="chk-box" id="ck_uploaded" {% if t.nt_uploaded %}checked{% endif %} onclick="event.stopPropagation()">
            <div style="flex:1">
              <div class="chk-lbl">🌐 تم النشر على المنصة الإلكترونية</div>
              <div class="chk-sub">العرض نُشِر ورُفع رسمياً على منصة المنافسات</div>
              <div class="chk-date {% if t.nt_platform_date %}show{% endif %}" id="dt_uploaded">
                <label class="form-label">تاريخ النشر على المنصة</label>
                <input type="date" id="date_uploaded" class="form-control" style="max-width:220px"
                       value="{{ t.nt_platform_date[:10] if t.nt_platform_date else '' }}"
                       onclick="event.stopPropagation()">
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- EXTENSION TRACKING -->
      <div class="spanel">
        <div class="sp-head">🔄 تتبع التمديد</div>
        <div class="sp-body">
          <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem">
            <input type="checkbox" class="chk-box" id="ck_extended"
                   {% if t.nt_extended %}checked{% endif %}
                   onchange="toggleExt(this)">
            <label for="ck_extended" style="font-weight:600;font-size:.9rem;cursor:pointer">
              هذه المنافسة تم تمديدها
            </label>
            {% if t.nt_extended %}
            <span class="ext-badge">🔄 مُمدَّدة</span>
            {% endif %}
          </div>
          <div id="extDetails" style="display:{% if t.nt_extended %}block{% else %}none{% endif %}">
            <div class="row g-2">
              <div class="col-auto">
                <label class="form-label">عدد مرات التمديد</label>
                <input type="number" id="extCount" class="form-control" min="1" max="20" style="width:100px"
                       value="{{ t.nt_ext_count or 1 }}">
              </div>
            </div>
            <div class="mt-2">
              <label class="form-label">تواريخ التمديد (افصل بفاصلة)</label>
              <input type="text" id="extDates" class="form-control"
                     placeholder="مثال: 2025-01-15، 2025-02-20"
                     value="{{ t.nt_ext_dates or '' }}">
            </div>
          </div>
        </div>
      </div>

    </div>

    <div class="col-12 col-md-5">

      <!-- NOTES -->
      <div class="spanel">
        <div class="sp-head">📝 ملاحظات المهندس</div>
        <div class="sp-body">
          <textarea id="tNotes" class="form-control" rows="8"
            placeholder="أضف أي ملاحظات، متطلبات خاصة، مستجدات، أو معلومات مهمة عن هذه المنافسة..."
          >{{ t.nt_notes or '' }}</textarea>
          <div style="margin-top:.75rem">
            <div class="form-label">المهندس المسؤول</div>
            <select id="engSelect" class="form-select">
              {% for eng in engineers %}
              <option value="{{ eng }}" {% if eng == t.assigned_engineer %}selected{% endif %}>{{ eng }}</option>
              {% endfor %}
            </select>
          <button type="button" id="lockBtn" onclick="toggleLock()" title="قفل/فتح تعيين المهندس" style="margin-top:.5rem;padding:.45rem .8rem;border-radius:7px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.06);color:#aaa;cursor:pointer;font-size:.88rem;width:100%;text-align:center;transition:background .15s,color .15s,border-color .15s">{{ "🔒 مقفول — انقر للفتح" if t.engineer_locked else "🔓 مفتوح — انقر للقفل" }}</button>
          </div>
        </div>
      </div>

      <!-- GUARANTEE (v5.6) -->
      <div class="spanel" style="margin-top:1rem">
        <div class="sp-head">🛡️ الضمان الابتدائي</div>
        <div class="sp-body">
          <div class="form-label">حالة الضمان</div>
          <select id="gStatus" class="form-select">
            <option value="PENDING">⚪ لم يبدأ</option>
            <option value="IN_PROGRESS">🟡 قيد الإصدار من البنك</option>
            <option value="READY">🟢 جاهز</option>
            <option value="SUBMITTED">✅ قُدّم مع العرض</option>
            <option value="NOT_REQUIRED">➖ غير مطلوب</option>
          </select>
          <div class="form-label" style="margin-top:.6rem">موعد الاستحقاق <span id="gAuto" style="font-size:.7rem;color:#888"></span></div>
          <input type="date" id="gDue" class="form-control">
          <div class="form-label" style="margin-top:.6rem">ملاحظات الضمان</div>
          <input type="text" id="gNotes" class="form-control" placeholder="رقم الضمان، البنك، النسبة...">
          <button type="button" onclick="gSave()" id="gBtn" style="margin-top:.7rem;width:100%;padding:.5rem;
            border-radius:8px;border:1px solid rgba(184,106,0,.4);background:rgba(184,106,0,.12);
            color:#b86a00;font-weight:700;cursor:pointer;font-family:'Tajawal',sans-serif">💾 حفظ الضمان</button>
          <script>
          (function(){
            fetch(`/api/tender/{{ t.id }}/guarantee`).then(r=>r.json()).then(g=>{
              if(!g.ok) return;
              document.getElementById('gStatus').value = g.status || 'PENDING';
              document.getElementById('gDue').value = g.due_date || '';
              document.getElementById('gNotes').value = g.notes || '';
              document.getElementById('gAuto').textContent = g.auto ? '(محسوب تلقائياً: قبل التقديم بـ5 أيام)' : '(محدد يدوياً)';
            }).catch(()=>{});
          })();
          function gSave(){
            const btn = document.getElementById('gBtn');
            btn.disabled = true; btn.textContent = '⏳ جاري الحفظ...';
            fetch(`/api/tender/{{ t.id }}/guarantee`, {method:'POST',
              headers:{'Content-Type':'application/json'},
              body: JSON.stringify({status: document.getElementById('gStatus').value,
                                    due_date: document.getElementById('gDue').value,
                                    notes: document.getElementById('gNotes').value})
            }).then(r=>r.json()).then(j=>{
              btn.textContent = j.ok ? '✅ تم الحفظ' : '⚠️ خطأ';
              setTimeout(()=>{btn.disabled=false;btn.textContent='💾 حفظ الضمان';}, 1600);
            }).catch(()=>{btn.disabled=false;btn.textContent='💾 حفظ الضمان';});
          }
          </script>
        </div>
      </div>

    </div>
  </div>

  <!-- SAVE -->
  <div style="display:flex;justify-content:center;gap:1rem;margin-top:.5rem;padding-bottom:2rem">
    <button class="save-btn" id="saveBtn" onclick="saveAll()">
      💾 حفظ جميع التغييرات
    </button>
    <a href="{{ back_url }}" style="display:inline-flex;align-items:center;gap:.4rem;
       padding:.7rem 1.5rem;border:1px solid var(--border);border-radius:9px;
       color:var(--muted);text-decoration:none;font-weight:600;font-size:.9rem;
       background:var(--card);transition:.18s"
       onmouseover="this.style.background='var(--hover)'"
       onmouseout="this.style.background='var(--card)'">
      ← العودة للوحة
    </a>
  </div>

</div>

<div id="tw"><div id="toast" class="tmsg"></div></div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
const TID = {{ t.id }};

// Checkbox toggle with date reveal
function toggleChk(key, el) {
  const cb = document.getElementById('ck_' + key);
  const dt = document.getElementById('dt_' + key);
  cb.checked = !cb.checked;
  el.classList.toggle('done', cb.checked);
  if (dt) dt.classList.toggle('show', cb.checked);
}

// Extension toggle
function toggleExt(cb) {
  document.getElementById('extDetails').style.display = cb.checked ? 'block' : 'none';
}

// Entrance animations
(function(){
  const items = document.querySelectorAll('.info-card,.spanel');
  items.forEach((el, i) => {
    el.style.animation = `fadeUp .45s cubic-bezier(.25,1,.5,1) ${40+i*70}ms both`;
  });
})();

// Save all
function saveAll() {
  const btn = document.getElementById('saveBtn');
  btn.disabled = true; btn.textContent = '⏳ جاري الحفظ...';

  const payload = {
    notes:               document.getElementById('tNotes').value,
    is_extended:         document.getElementById('ck_extended').checked,
    extension_count:     document.getElementById('extCount') ? +document.getElementById('extCount').value : 0,
    extension_dates:     document.getElementById('extDates') ? document.getElementById('extDates').value : '',
    submitted_to_review: document.getElementById('ck_s_review').checked,
    review_date:         document.getElementById('date_s_review') ? document.getElementById('date_s_review').value : '',
    submitted_to_upload: document.getElementById('ck_s_upload').checked,
    upload_submit_date:  document.getElementById('date_s_upload') ? document.getElementById('date_s_upload').value : '',
    uploaded_to_platform:document.getElementById('ck_uploaded').checked,
    platform_upload_date:document.getElementById('date_uploaded') ? document.getElementById('date_uploaded').value : '',
  };

  // Also update engineer if changed
  const engSel = document.getElementById('engSelect');
  const eng = engSel ? engSel.value : '';
  const savedEng = '{{ t.assigned_engineer or "" }}';
  const isLocked = {{ 'true' if t.engineer_locked else 'false' }};

  const notesPromise = fetch('/api/tender/' + TID + '/notes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });

  const promises = [notesPromise];
  if (eng && eng !== savedEng) {
    promises.push(fetch('/api/tender/' + TID + '/update', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({engineer: eng})
    }));
  }

  Promise.all(promises)
    .then(resps => Promise.all(resps.map(r => r.json())))
    .then(results => {
      const allOk = results.every(d => d.ok);
      if (allOk) {
        btn.textContent = '✅ تم الحفظ';
        btn.style.background = 'var(--green)';
        toast('✅ تم حفظ جميع التغييرات بنجاح');
        setTimeout(() => { btn.style.background = ''; btn.textContent = '💾 حفظ جميع التغييرات'; }, 2000);
      } else {
        toast('⚠️ حدث خطأ أثناء الحفظ', 1);
      }
    })
    .catch(() => toast('خطأ في الاتصال بالسيرفر', 1))
    .finally(() => { btn.disabled = false; });
}

let _tt;
function toast(m, err=0) {
  const t = document.getElementById('toast');
  if (_tt) clearTimeout(_tt);
  t.textContent = m;
  t.className = 'tmsg' + (err ? ' err' : '');
  void t.offsetWidth;
  t.classList.add('on');
  _tt = setTimeout(() => {
    t.style.opacity = '0';
    setTimeout(() => { t.className = 'tmsg' + (err?' err':''); t.style.opacity=''; }, 300);
  }, err ? 3500 : 2800);
}

// Keyboard save
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') { e.preventDefault(); saveAll(); }
});
</script>
<!-- COPYRIGHT FOOTER -->
<div style="text-align:center;padding:1rem;color:rgba(255,255,255,.82);font-size:.68rem;font-family:'Tajawal',sans-serif;letter-spacing:.3px">
  Copyright 2026 &copy; Your Name &mdash; <a href="https://example.com" target="_blank" style="color:rgba(255,255,255,.6);text-decoration:none">example.com</a>
</div>

</body></html>"""


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="refresh" content="300">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>{{ co.short_ar }} — لوحة المنافسات</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css">
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:{{ co.theme_bg }}; --card:{{ co.theme_card }}; --hover:{{ co.theme_hover }}; --head:{{ co.theme_head }};
  --border:#c8a028; --border2:#a07820; --text:#1e1404; --sub:#4a3810; --muted:#7a5e28;
  --amber:{{ co.theme_primary }}; --amber-l:{{ co.theme_primary_l }}; --amber-d:{{ co.theme_primary_d }};
  --blue:#1a5a9a; --green:#247848; --yellow:#a06800;
  --red:#b02828; --orange:#a84e1a; --purple:#643ca0;
}
html{-webkit-text-size-adjust:100%}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:'Tajawal',sans-serif;font-size:14px;margin:0}

/* TOP BAR */
.topbar{background:linear-gradient(135deg,#5a2800 0%,#8a4800 55%,#b06000 100%);
  border-bottom:2px solid #6e3200;
  padding:.9rem 1.5rem;display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:200;color:#fff4d8;
  transition:box-shadow .3s cubic-bezier(.25,1,.5,1)}
.brand{display:flex;align-items:center;gap:.65rem;font-weight:900;font-size:1.2rem;letter-spacing:-.3px;color:#fff4d8}
.brand-sub{color:rgba(255,215,140,.7);font-weight:500;font-size:.83rem}
.pulse{width:8px;height:8px;background:#6effa0;border-radius:50%;
  animation:blink 2s ease-in-out infinite;flex-shrink:0}
@keyframes blink{0%,100%{box-shadow:0 0 0 0 rgba(110,255,160,.5)}50%{box-shadow:0 0 0 5px rgba(110,255,160,0)}}
.tnav{display:flex;align-items:center;gap:.5rem}
.tnav a{color:rgba(255,215,140,.8);text-decoration:none;font-size:.83rem;padding:.3rem .65rem;border-radius:7px;transition:.15s}
.tnav a:hover{background:rgba(255,255,255,.12);color:#fff}
.tnav a.hi{color:#ffd060}
.ts{font-size:.74rem;color:rgba(255,215,140,.6)}

/* STAT CARDS */
.stats-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:1rem;margin-bottom:1rem}
@media(max-width:900px){.stats-grid{grid-template-columns:1fr 1fr}}
.scard{background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:1.5rem 1.75rem;position:relative;overflow:hidden;transition:.2s;cursor:default}
.scard:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(100,60,0,.2)}
.scard.t-amber{background:linear-gradient(145deg,var(--head) 0%,var(--card) 65%);border-color:var(--amber-d)}
.scard.t-red{border-color:rgba(196,82,82,.3)}
.scard.t-yellow{border-color:rgba(200,144,64,.3)}
.scard.t-orange{border-color:rgba(200,120,64,.3)}
.scard.t-green{border-color:rgba(90,171,120,.3)}
.stat-hero{padding:2.2rem 2rem}
.snum{font-size:3.4rem;font-weight:900;line-height:.9;letter-spacing:-2px;margin-top:.35rem}
.stat-hero .snum{font-size:clamp(4.2rem,5.5vw,6rem);letter-spacing:-3px}
.slbl{color:var(--sub);font-size:.78rem;letter-spacing:.4px;margin-bottom:.3rem;font-weight:600}

/* PANEL */
.panel{background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden}
.phead{background:var(--head);border-bottom:1px solid var(--border);
  border-right:3px solid var(--amber);padding:.75rem 1rem;
  font-weight:700;font-size:.84rem;display:flex;align-items:center;justify-content:space-between}
.pbody{padding:.85rem}

/* TABLE */
.t-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse}
thead tr{background:var(--head);border-bottom:1px solid var(--border)}
thead th{padding:.55rem .8rem;font-weight:700;font-size:.82rem;color:var(--sub);
  text-transform:uppercase;letter-spacing:.3px;white-space:nowrap}
tbody tr{border-bottom:1px solid rgba(180,140,40,.25);transition:background .1s}
/* v5.7.4: rows are NEVER hidden by CSS — the entrance animation hides/reveals via JS inline styles */
/* v5.7.3: modal rows are added dynamically AFTER the entrance animation ran —
   without this exemption they inherit opacity:0 forever and render invisible */
.modal tbody tr{opacity:1!important;transform:none!important;animation:none!important}
tbody tr:hover{background:var(--hover)}
tbody td{padding:.5rem .8rem;vertical-align:middle;font-size:.88rem}
tr.ru td:first-child{box-shadow:inset 3px 0 0 var(--red)}
tr.rw td:first-child{box-shadow:inset 3px 0 0 var(--yellow)}
tr.ro td:first-child{box-shadow:inset 3px 0 0 var(--green)}
tr.rg td:first-child{box-shadow:inset 3px 0 0 var(--border)}
tr.miss{opacity:.5}

/* DAY BADGES */
.db{display:inline-flex;align-items:center;padding:2px 9px;border-radius:20px;
  font-size:.74rem;font-weight:700;white-space:nowrap}
.db-r{background:rgba(248,81,73,.15);color:var(--red);border:1px solid rgba(248,81,73,.3)}
.db-w{background:rgba(227,179,65,.15);color:var(--yellow);border:1px solid rgba(227,179,65,.3)}
.db-g{background:rgba(63,185,80,.15);color:var(--green);border:1px solid rgba(63,185,80,.3)}
.db-s{background:rgba(139,148,158,.1);color:var(--muted);border:1px solid var(--border)}

/* ENG CHIP */
.echip{display:inline-block;padding:2px 8px;background:rgba(200,135,60,.1);
  color:var(--amber-l);border-radius:4px;font-size:.77rem;font-weight:600;
  border:1px solid rgba(200,135,60,.25)}

/* ACTION BUTTONS */
.abtn{width:27px;height:27px;border:1px solid var(--border);background:transparent;
  color:var(--muted);border-radius:7px;cursor:pointer;transition:.15s;
  display:inline-flex;align-items:center;justify-content:center;font-size:.78rem;padding:0}
.abtn:hover{background:var(--hover);color:var(--text);border-color:#444d56}
.abtn.ae:hover{background:rgba(88,166,255,.1);color:var(--blue);border-color:rgba(88,166,255,.4)}
.abtn.ar:hover{background:rgba(63,185,80,.1);color:var(--green);border-color:rgba(63,185,80,.4)}

/* ENGINEER CARDS */
.ecard{background:var(--hover);border:1px solid var(--border);border-radius:8px;
  padding:.75rem .9rem;margin-bottom:.5rem;transition:.15s}
.ecard:hover{border-color:var(--border2)}
.eavatar{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-weight:700;font-size:.95rem;flex-shrink:0;color:#fff}
.ebar{height:5px;border-radius:3px;background:rgba(160,112,0,.18);margin-top:5px;overflow:hidden}
.ebar-fill{height:100%;width:100%;border-radius:3px;transform-origin:right center;transform:scaleX(0);transition:transform .75s cubic-bezier(.25,1,.5,1)}

/* MODAL */
.modal-content{background:var(--card);border:1px solid var(--border);color:var(--text)}
.modal-header{background:var(--head);border-bottom:1px solid var(--border)}
.modal-footer{border-top:1px solid var(--border)}
.form-label{color:var(--muted);font-size:.81rem;margin-bottom:.3rem}
.form-control,.form-select{background:var(--bg)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;border-radius:8px}
.form-control:focus,.form-select:focus{border-color:var(--amber)!important;
  box-shadow:0 0 0 3px rgba(200,135,60,.12)!important}

/* TOAST */
#tw{position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%);z-index:9999}
.tmsg{background:#e8f5ea;color:var(--green);border:1px solid rgba(36,120,72,.3);
  padding:.6rem 1.5rem;border-radius:10px;font-size:.87rem;
  box-shadow:0 6px 28px rgba(100,60,0,.15),0 0 0 1px rgba(36,120,72,.1);
  opacity:0;transform:translateY(12px) scale(.96);
  transition:opacity .28s cubic-bezier(.22,1,.36,1),
             transform .32s cubic-bezier(.22,1,.36,1);
  pointer-events:none;white-space:nowrap}
.tmsg.err{background:#fde8e8;color:var(--red);border-color:rgba(176,40,40,.3);
  box-shadow:0 6px 28px rgba(100,60,0,.15),0 0 0 1px rgba(176,40,40,.1)}
.tmsg.on{opacity:1;transform:translateY(0) scale(1)}

/* ── ENTRANCE KEYFRAMES ──────────────────────── */
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}

/* ── URGENT BADGE GLOW PULSE ─────────────────── */
@keyframes urgGlow{0%,100%{box-shadow:0 0 0 0 rgba(248,81,73,.55)}65%{box-shadow:0 0 0 7px rgba(248,81,73,0)}}
.db-r{animation:urgGlow 2.8s ease-in-out infinite}

/* ── PAGE LOAD — START INVISIBLE ─────────────── */
.scard{opacity:0}
.panel{opacity:0}

/* ── ENHANCED COLOR-MATCHED HOVER GLOWS ─────── */
.scard.t-amber:hover{box-shadow:0 10px 28px rgba(100,60,0,.22),0 0 0 1px rgba(138,72,0,.35)}
.scard.t-red:hover{box-shadow:0 10px 28px rgba(100,60,0,.15),0 0 0 1px rgba(176,40,40,.28)}
.scard.t-yellow:hover{box-shadow:0 10px 28px rgba(100,60,0,.15),0 0 0 1px rgba(160,104,0,.28)}
.scard.t-orange:hover{box-shadow:0 10px 28px rgba(100,60,0,.15),0 0 0 1px rgba(168,78,26,.28)}

/* ── BUTTON PRESS FEEDBACK ───────────────────── */
.abtn{transition:background .15s,color .15s,border-color .15s,box-shadow .18s,transform .08s}
.abtn:active{transform:scale(0.82)!important;transition:transform .08s!important}
.abtn.ae:hover{box-shadow:0 0 0 3px rgba(126,179,232,.18)!important}
.abtn.ar:hover{box-shadow:0 0 0 3px rgba(90,171,120,.18)!important}

/* ── ENGINEER CHIP HOVER ─────────────────────── */
.echip{transition:transform .18s cubic-bezier(.25,1,.5,1),
  box-shadow .18s,background .18s}
.echip:hover{transform:scale(1.06);
  box-shadow:0 2px 10px rgba(200,135,60,.22)}

/* ── TOPBAR ELEVATION ON SCROLL ──────────────── */
.topbar.elevated{box-shadow:0 4px 28px rgba(60,20,0,.45)}

/* ── COPY FLASH ON TITLE ─────────────────────── */
@keyframes cpFlash{
  0%  {background:rgba(200,135,60,.22);color:var(--amber-l);border-radius:4px}
  80% {background:rgba(200,135,60,.08)}
  100%{background:transparent;color:inherit}
}
td.t-title.flashing{animation:cpFlash .55s cubic-bezier(.25,1,.5,1) both}

/* ── FILTER BUTTON SMOOTH TRANSITION ─────────── */
.fbtn{transition:background .2s cubic-bezier(.25,1,.5,1),
  color .2s,border-color .2s,transform .1s}
.fbtn:active{transform:scale(.93)}

/* ── SEARCH RESULT COUNT FADE ────────────────── */
.srch-res{transition:opacity .2s}

/* ── SAVE BUTTON SUCCESS FLASH ───────────────── */
@keyframes saveOk{
  0%  {background:#5aab78;color:#fff;transform:scale(.96)}
  40% {transform:scale(1.04)}
  100%{background:#198754;color:#fff;transform:scale(1)}
}
.btn-success.did-save{animation:saveOk .4s cubic-bezier(.25,1,.5,1) both}

/* ── SCARD BOTTOM ACCENT LINE ────────────────── */
.scard::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:var(--amber);transform:scaleX(0);transform-origin:center;
  transition:transform .35s cubic-bezier(.25,1,.5,1)}
.scard:hover::after{transform:scaleX(.6)}
.scard.t-red::after{background:var(--red)}
.scard.t-yellow::after{background:var(--yellow)}
.scard.t-orange::after{background:var(--orange)}

/* ── ECARD HOVER ─────────────────────────────── */
.ecard{transition:border-color .2s,transform .2s cubic-bezier(.25,1,.5,1),box-shadow .2s}
.ecard:hover{transform:translateX(-2px);
  box-shadow:2px 0 0 var(--amber-d),0 4px 12px rgba(100,60,0,.15)}

/* ── SEARCH + FILTER BAR ─────────────────────── */
.srch-bar{padding:.55rem .9rem;border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;background:var(--head)}
.srch-wrap{position:relative;display:flex;align-items:center;min-width:160px;max-width:250px;flex:1}
.srch-input{background:var(--bg);border:1px solid var(--border);color:var(--text);
  border-radius:7px;padding:.38rem .75rem .38rem 2.2rem;font-family:'Tajawal',sans-serif;
  font-size:.82rem;width:100%;outline:none;transition:border-color .2s,box-shadow .2s;direction:rtl}
.srch-input:focus{border-color:var(--amber);box-shadow:0 0 0 2px rgba(200,135,60,.15)}
.srch-input::placeholder{color:var(--muted)}
.srch-ico{position:absolute;left:.6rem;color:var(--muted);pointer-events:none;font-size:.75rem}
.srch-kbd{position:absolute;left:2rem;color:var(--muted);font-size:.6rem;
  border:1px solid var(--border);border-radius:3px;padding:1px 4px;line-height:1;
  opacity:.7;pointer-events:none;transition:opacity .2s}
.srch-input:focus~.srch-kbd{opacity:0}
.fbtns{display:flex;gap:.3rem}
.fbtn{background:transparent;border:1px solid var(--border);color:var(--muted);
  border-radius:6px;padding:.28rem .6rem;font-family:'Tajawal',sans-serif;
  font-size:.72rem;cursor:pointer;transition:.15s;white-space:nowrap}
.fbtn:hover{background:var(--hover);color:var(--text)}
.fbtn.fbtn-active{background:rgba(200,135,60,.12);color:var(--amber-l);border-color:var(--amber-d)}
.fbtn.fbtn-r.fbtn-active{background:rgba(196,82,82,.15);color:var(--red);border-color:rgba(196,82,82,.3)}
.fbtn.fbtn-w.fbtn-active{background:rgba(200,144,64,.15);color:var(--yellow);border-color:rgba(200,144,64,.3)}
.fbtn.fbtn-g.fbtn-active{background:rgba(90,171,120,.15);color:var(--green);border-color:rgba(90,171,120,.3)}
.srch-res{color:var(--muted);font-size:.71rem;margin-right:auto;white-space:nowrap}

/* ── SORTABLE HEADERS ────────────────────────── */
th.sortable{cursor:pointer;user-select:none;transition:color .15s}
th.sortable:hover{color:var(--text)!important}
th.sortable::after{content:' ⇅';color:var(--muted);font-size:.6rem}
th.sort-asc::after{content:' ↑';color:var(--amber-l)!important}
th.sort-desc::after{content:' ↓';color:var(--amber-l)!important}

/* ── REFRESH COUNTDOWN ───────────────────────── */
.rf-count{color:var(--sub);font-size:.78rem;font-variant-numeric:tabular-nums;transition:color .3s}
.rf-count.soon{color:var(--yellow)}

/* ── COPY HINT ON TITLE ──────────────────────── */
td.t-title{cursor:pointer;transition:color .15s;line-height:1.5;max-width:560px;word-break:break-word}
td.t-title:hover{color:var(--amber-l)}

/* ── BULK SELECTION ──────────────────────────── */
.cb-cell{width:30px;padding:0 .4rem!important;text-align:center}
.cb-row{width:15px;height:15px;cursor:pointer;accent-color:var(--amber);border-radius:3px}
tr.sel-row{background:rgba(200,135,60,.07)!important}
tr.sel-row:hover{background:rgba(200,135,60,.12)!important}

/* ── BULK TOOLBAR ────────────────────────────── */
#bulkBar{
  position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%) translateY(80px);
  background:var(--card);border:1px solid var(--amber-d);border-radius:12px;
  padding:.6rem .9rem;display:flex;align-items:center;gap:.6rem;
  box-shadow:0 8px 32px rgba(100,60,0,.25);z-index:500;
  transition:transform .3s cubic-bezier(.25,1,.5,1),opacity .25s;
  opacity:0;pointer-events:none;white-space:nowrap
}
#bulkBar.show{transform:translateX(-50%) translateY(0);opacity:1;pointer-events:all}
#bulkBar .blbl{color:var(--amber-l);font-size:.82rem;font-weight:700;min-width:90px}
#bulkBar select{background:var(--bg);border:1px solid var(--border);color:var(--text);
  border-radius:7px;padding:.3rem .65rem;font-family:'Tajawal',sans-serif;font-size:.82rem;outline:none}
#bulkBar select:focus{border-color:var(--amber)}
#bulkBar .bapply{background:var(--amber);border:none;color:#fff;border-radius:7px;
  padding:.3rem .85rem;font-family:'Tajawal',sans-serif;font-size:.82rem;font-weight:700;
  cursor:pointer;transition:.15s}
#bulkBar .bapply:hover{background:var(--amber-l)}
#bulkBar .bapply:disabled{opacity:.5;cursor:not-allowed}
#bulkBar .bcancel{background:transparent;border:1px solid var(--border);color:var(--muted);
  border-radius:7px;padding:.3rem .65rem;font-family:'Tajawal',sans-serif;font-size:.78rem;
  cursor:pointer;transition:.15s}
#bulkBar .bcancel:hover{background:var(--hover);color:var(--text)}

/* ── REDUCED MOTION FALLBACK (Accessibility) ─── */
@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{
    animation-duration:.01ms!important;
    animation-iteration-count:1!important;
    transition-duration:.01ms!important;
  }
}

/* ══════════════════════════════════════════════
   MOBILE RESPONSIVE
   ══════════════════════════════════════════════ */
@media(max-width:768px){
  body{font-size:15px}

  /* ── TOPBAR ─────────────────── */
  .topbar{padding:.55rem .7rem;gap:.35rem;flex-wrap:wrap;max-width:100%;overflow-x:hidden}
  .brand-sub,.ts{display:none}
  .brand{font-size:.95rem;gap:.4rem;min-width:0}
  .tnav{gap:.15rem;overflow-x:auto;flex-wrap:nowrap;max-width:100%;
    scrollbar-width:none;-ms-overflow-style:none}
  .tnav::-webkit-scrollbar{display:none}
  .tnav a{font-size:.74rem;padding:.4rem .45rem;flex-shrink:0;
    min-height:40px;display:inline-flex;align-items:center;
    touch-action:manipulation}

  /* ── LAYOUT ─────────────────── */
  .page-wrap{padding:.65rem .65rem!important}

  /* ── STATS GRID ─────────────── */
  .stats-grid{grid-template-columns:1fr 1fr;gap:.5rem;margin-bottom:.6rem}
  .scard,.stat-hero{padding:.95rem 1rem}
  .snum{font-size:2.4rem;letter-spacing:-1px}
  .stat-hero .snum{font-size:clamp(2.8rem,8.5vw,3.8rem);letter-spacing:-1.5px}
  .slbl{font-size:.59rem;letter-spacing:1px}

  /* ── PANEL ──────────────────── */
  .phead{padding:.6rem .85rem;font-size:.81rem}
  .pbody{padding:.55rem .65rem}

  /* ── SEARCH BAR → 2 rows ────── */
  .srch-bar{flex-direction:column;align-items:stretch;padding:.5rem .65rem;gap:.38rem}
  .srch-wrap{max-width:100%;min-width:0}
  .srch-input{font-size:.9rem;padding:.48rem .75rem .48rem 2.2rem;height:42px}
  .srch-kbd{display:none}
  .fbtns{overflow-x:auto;flex-wrap:nowrap;gap:.25rem;padding-bottom:1px;
    scrollbar-width:none;-ms-overflow-style:none;justify-content:flex-start}
  .fbtns::-webkit-scrollbar{display:none}
  .fbtn{flex-shrink:0;padding:.35rem .65rem;font-size:.76rem;
    min-height:38px;touch-action:manipulation}
  .srch-res{text-align:center;font-size:.7rem}

  /* ── TABLE → CARD VIEW ──────── */
  .t-wrap{overflow:visible}
  table{display:block}
  thead{display:none}
  tbody{display:block;padding:.3rem .4rem .5rem}

  tbody tr{
    display:grid;
    grid-template-areas:
      "title title title title"
      "days  eng   .     act";
    grid-template-columns:auto auto 1fr auto;
    margin-bottom:.42rem;
    border:1px solid var(--border);
    border-radius:10px;
    padding:.75rem .85rem .65rem;
    gap:.38rem .5rem;
    background:var(--hover);
    box-shadow:none!important;
    transform:none!important;
  }
  /* Color accent: right edge (RTL leading side) */
  tbody tr.ru{border-right:3px solid var(--red)}
  tbody tr.rw{border-right:3px solid var(--yellow)}
  tbody tr.ro{border-right:3px solid var(--green)}
  tbody tr.rg{border-right:3px solid var(--border)}
  tbody tr.miss{opacity:.45!important}

  /* Hide: checkbox col, row# col, date col */
  tbody td:nth-child(1),
  tbody td:nth-child(2),
  tbody td:nth-child(4){display:none!important}

  /* Title → full top row */
  tbody td:nth-child(3){
    grid-area:title;
    display:block!important;
    font-size:.88rem;
    line-height:1.45;
    padding:0;
    border:none;
    white-space:normal;
    color:var(--text);
  }
  /* Show submission date under title via data-date attr */
  tbody td.t-title::after{
    content:attr(data-date);
    display:block;
    font-size:.7rem;
    color:var(--muted);
    margin-top:.22rem;
    font-weight:400;
  }

  /* Days badge → bottom-right section */
  tbody td:nth-child(5){
    grid-area:days;
    display:flex!important;
    align-items:center;
    padding:0;border:none;
  }
  /* Engineer chip → bottom-center */
  tbody td:nth-child(6){
    grid-area:eng;
    display:flex!important;
    align-items:center;
    padding:0;border:none;
  }
  /* Action buttons → bottom-right */
  tbody td:nth-child(7){
    grid-area:act;
    display:flex!important;
    align-items:center;
    gap:5px;
    padding:0;border:none;
  }

  /* Bigger touch targets */
  .abtn{width:42px;height:42px;font-size:1rem;border-radius:9px}
  .abtn:active{transform:scale(.85)!important}

  /* Engineer load panel */
  .eavatar{width:30px;height:30px;font-size:.8rem}
  .ecard{padding:.55rem .7rem;margin-bottom:.38rem}

  /* ── MODALS → slide from bottom ─ */
  .modal-dialog{
    margin:0!important;
    position:fixed!important;
    bottom:0!important;left:0!important;right:0!important;
    width:100%!important;max-width:100%!important;
    transform:none!important;
  }
  .modal.fade .modal-dialog{transform:translateY(100%)!important;transition:transform .3s cubic-bezier(.25,1,.5,1)!important}
  .modal.show .modal-dialog{transform:translateY(0)!important}
  .modal-content{border-radius:18px 18px 0 0!important;border-bottom:none!important;
    padding-bottom:env(safe-area-inset-bottom,0)}
  .modal-body{max-height:62vh;overflow-y:auto;-webkit-overflow-scrolling:touch}

  /* ── BULK TOOLBAR ────────────── */
  #bulkBar{
    width:calc(100% - 1.2rem);
    flex-wrap:wrap;
    justify-content:space-between;
    bottom:.6rem;
    padding:.55rem .7rem;
    gap:.35rem;
    border-radius:10px;
  }
  #bulkBar .blbl{
    order:-1;width:100%;
    border-bottom:1px solid var(--border);
    padding-bottom:.3rem;min-width:auto;
  }
  #bulkBar select{flex:1;min-width:130px;font-size:.85rem}
  #bulkBar .bapply,#bulkBar .bcancel{min-height:40px;touch-action:manipulation}

  /* Chart */
  #dChart{max-height:155px!important}
}

/* ── Very small phones ≤400px ───── */
@media(max-width:400px){
  .page-wrap{padding:.5rem!important}
  .stats-grid{gap:.35rem}
  .scard,.stat-hero{padding:.8rem .85rem}
  .snum{font-size:2rem;letter-spacing:-.5px}
  .stat-hero .snum{font-size:clamp(2.2rem,9.5vw,3rem)}
  .abtn{width:40px;height:40px}
  .topbar{padding:.55rem .7rem}
  tbody tr{padding:.65rem .75rem .55rem}
  tbody td:nth-child(3){font-size:.84rem}
}

/* ── MINI STATS ROW ──────────────── */
.mini-stats{display:flex;gap:.6rem;margin-bottom:1rem;flex-wrap:wrap}
.mstat{background:var(--card);border:1px solid var(--border);border-radius:9px;
  padding:.55rem 1rem;display:flex;align-items:center;gap:.55rem;flex:1;min-width:140px}
.mstat-ico{font-size:1.3rem;line-height:1}
.mstat-info{display:flex;flex-direction:column}
.mstat-num{font-size:1.4rem;font-weight:900;line-height:1;letter-spacing:-1px}
.mstat-lbl{font-size:.68rem;color:var(--muted);font-weight:600;letter-spacing:.3px;margin-top:2px}
@media(max-width:768px){
  .mini-stats{gap:.4rem}
  .mstat{padding:.45rem .7rem;min-width:110px}
  .mstat-num{font-size:1.15rem}
}

/* ── GUARANTEES + CALENDAR (v5.6) ── */
.g-row{display:flex;gap:.55rem;align-items:flex-start;padding:.45rem .5rem;border-radius:9px;
  margin-bottom:.4rem;text-decoration:none;border:1px solid var(--border);background:var(--card);transition:.15s}
.g-row:hover{background:var(--hover);transform:translateX(-2px)}
.g-badge{flex-shrink:0;font-size:.66rem;font-weight:800;padding:.18rem .5rem;border-radius:6px;white-space:nowrap;margin-top:.1rem}
.g-red .g-badge{background:rgba(200,40,40,.12);color:var(--red);border:1px solid rgba(200,40,40,.3)}
.g-amber .g-badge{background:rgba(184,106,0,.13);color:var(--amber-l);border:1px solid rgba(184,106,0,.3)}
.g-green .g-badge{background:rgba(36,120,72,.12);color:var(--green);border:1px solid rgba(36,120,72,.28)}
.g-info{display:flex;flex-direction:column;min-width:0}
.g-title{font-size:.78rem;font-weight:700;color:var(--amber-d);line-height:1.35}
.g-owner{font-size:.68rem;color:var(--muted)}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:3px;text-align:center}
.cal-h{font-size:.64rem;font-weight:800;color:var(--amber);padding:.15rem 0}
.cal-d{font-size:.72rem;font-weight:600;padding:.28rem 0;border-radius:7px;color:var(--sub)}
.cal-empty{visibility:hidden}
.cal-today{outline:2px solid var(--amber-l);outline-offset:-2px;font-weight:900;color:var(--amber)}
.cal-r{background:rgba(200,40,40,.16);color:var(--red);font-weight:800}
.cal-y{background:rgba(212,160,23,.22);color:#7a5800;font-weight:800}
.cal-gr{background:rgba(36,120,72,.14);color:var(--green);font-weight:800}
.cal-g{background:rgba(184,106,0,.22);color:var(--amber-d);font-weight:900;box-shadow:inset 0 0 0 1px rgba(184,106,0,.4)}

/* ── OWNER DISTRIBUTION ──────────── */
.owner-row{display:flex;align-items:center;gap:.5rem;margin-bottom:.42rem}
.owner-name{font-size:.8rem;color:var(--sub);min-width:0;flex:1;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.owner-bar-wrap{width:70px;flex-shrink:0}
.owner-bar{height:5px;border-radius:3px;background:rgba(160,112,0,.18);overflow:hidden}
.owner-bar-fill{height:100%;border-radius:3px;background:var(--amber-l);
  transform-origin:right;transform:scaleX(0);
  transition:transform .7s cubic-bezier(.25,1,.5,1)}
.owner-cnt{font-size:.8rem;font-weight:700;color:var(--amber);min-width:18px;text-align:left}

/* ── PRINT ──────────────────────── */
@media print{
  .topbar,.srch-bar,.abtn,#bulkBar,#tw,.tnav,.mini-stats,
  .col-lg-4,.fbtn,#cbAll,.cb-cell,thead th:last-child,
  tbody td:last-child,tbody td:first-child{display:none!important}
  body{background:#fff!important;color:#000!important;font-size:11pt}
  .panel,.scard{background:#fff!important;border-color:#ccc!important;opacity:1!important}
  .stats-grid{grid-template-columns:repeat(4,1fr)!important}
  .snum{color:#000!important}
  .phead{background:#f0f0f0!important;border-color:#ccc!important}
  thead tr{background:#f0f0f0!important}
  tbody tr{break-inside:avoid}
  table{width:100%!important}
  .col-12,.col-lg-8{width:100%!important;max-width:100%!important}
  .echip{background:#eee!important;color:#000!important;border-color:#aaa!important}
  .db{background:#eee!important;border-color:#aaa!important;color:#000!important}
  @page{margin:1.5cm}
}
/* about dropdown */
.about-wrap{position:relative;display:inline-flex}
.about-btn{background:rgba(255,255,255,.1);border:1px solid rgba(255,200,100,.25);color:rgba(255,215,140,.85);padding:.3rem .75rem;border-radius:8px;cursor:pointer;font-family:'Tajawal',sans-serif;font-size:.82rem;transition:.15s;display:flex;align-items:center;gap:.35rem}
.about-btn:hover{background:rgba(255,255,255,.18);color:#fff}
.about-drop{position:absolute;top:calc(100% + 10px);left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#3d1800 0%,#6e3200 60%,#8a4800 100%);border:1px solid rgba(200,160,40,.4);border-radius:12px;padding:1.1rem 1.4rem;min-width:200px;text-align:center;z-index:300;box-shadow:0 10px 40px rgba(0,0,0,.45)}
.about-drop::before{content:'';position:absolute;top:-7px;left:50%;transform:translateX(-50%);border:7px solid transparent;border-bottom-color:#3d1800}
.about-heart{font-size:2.2rem;margin-bottom:.5rem;line-height:1}
.about-line{color:rgba(255,220,150,.85);font-size:.88rem;line-height:1.7}
.about-name{color:#ffd060;font-weight:800;font-size:1rem;margin-top:.55rem;letter-spacing:.3px}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <div class="brand">
    <div style="background:#fff;border-radius:9px;padding:5px 12px;display:inline-flex;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,.22);flex-shrink:0">
      <img src="{{ logo_uri }}" alt="{{ co.name_ar }}" style="height:44px;width:auto;display:block">
    </div>
    <span>{{ co.system_title }}</span>
    <span class="brand-sub">لوحة المنافسات</span>
    <div class="pulse" title="النظام يعمل"></div>
  </div>
  <div class="tnav">
    <a href="/results" class="hi">📊 سجل النتائج</a>
    <a href="/engineer-view">👷 المهندسين</a>
    <a href="/owners">🏢 الجهات</a>
    <span class="ts">{{ refreshed }}</span>
    <div class="about-wrap">
      <button class="about-btn" onclick="toggleAboutD(event)">عن ▾</button>
      <div id="aboutDropD" class="about-drop" style="display:none">
        <div class="about-heart">❤️</div>
        <div class="about-line">صُنع بكل حب</div>
        <div class="about-line">من فريق العروض الفنية</div>
        <div class="about-line">لشركة {{ co.short_ar }}</div>
        <div class="about-name">م. يوسف سليم</div>
      </div>
    </div>
    <a href="/logout">خروج ↩</a>
  </div>
</div>

<div class="page-wrap" style="padding:1.25rem 1.5rem;max-width:1700px;margin:0 auto">

  <!-- STAT CARDS -->
  <div class="stats-grid">
    <div class="scard t-amber stat-hero">
      <div class="slbl">المنافسات النشطة</div>
      <div class="snum" style="color:var(--amber)">{{ total_active }}</div>
    </div>
    <div class="scard t-orange" {% if pending_count %}onclick="openPending()" style="cursor:pointer" title="اضغط لعرض المنافسات بانتظار الاعتماد"{% endif %}>
      <div class="slbl">بانتظار الاعتماد {% if pending_count %}<span style="font-size:.65rem;color:var(--orange);opacity:.8">← اضغط للعرض</span>{% endif %}</div>
      <div class="snum" style="color:{% if pending_count %}var(--orange){% else %}var(--muted){% endif %}">{{ pending_count }}</div>
    </div>
    <div class="scard t-red">
      <div class="slbl">حرجة ≤ 3 أيام</div>
      <div class="snum" style="color:{% if urgent %}var(--red){% else %}var(--muted){% endif %}">{{ urgent }}</div>
    </div>
    <div class="scard t-yellow">
      <div class="slbl">تنبيه 4–7 أيام</div>
      <div class="snum" style="color:{% if warning %}var(--yellow){% else %}var(--muted){% endif %}">{{ warning }}</div>
    </div>
  </div>

  <!-- MINI STATS ROW -->
  <div class="mini-stats">
    <div class="mstat">
      <span class="mstat-ico">⌛</span>
      <div class="mstat-info">
        <span class="mstat-num" style="color:{% if today_count %}var(--red){% else %}var(--muted){% endif %}">{{ today_count }}</span>
        <span class="mstat-lbl">تنتهي اليوم</span>
      </div>
    </div>
    <div class="mstat">
      <span class="mstat-ico">⏰</span>
      <div class="mstat-info">
        <span class="mstat-num" style="color:{% if expired %}var(--red){% else %}var(--muted){% endif %}">{{ expired }}</span>
        <span class="mstat-lbl">منتهية التاريخ</span>
      </div>
    </div>
    <div class="mstat">
      <span class="mstat-ico">📤</span>
      <div class="mstat-info">
        <span class="mstat-num" style="color:{% if submitted_upload %}var(--orange){% else %}var(--muted){% endif %}">{{ submitted_upload }}</span>
        <span class="mstat-lbl">مرفوعة للقسم</span>
      </div>
    </div>
    <div class="mstat">
      <span class="mstat-ico">🌐</span>
      <div class="mstat-info">
        <span class="mstat-num" style="color:{% if uploaded_platform %}var(--green){% else %}var(--muted){% endif %}">{{ uploaded_platform }}</span>
        <span class="mstat-lbl">منشورة على المنصة</span>
      </div>
    </div>
    <div class="mstat">
      <span class="mstat-ico">✅</span>
      <div class="mstat-info">
        <span class="mstat-num" style="color:{% if ok_count %}var(--green){% else %}var(--muted){% endif %}">{{ ok_count }}</span>
        <span class="mstat-lbl">مريحة &gt; 7 أيام</span>
      </div>
    </div>
    <div class="mstat">
      <span class="mstat-ico">🗂️</span>
      <div class="mstat-info">
        <span class="mstat-num" style="color:var(--muted)">{{ closed_count }}</span>
        <span class="mstat-lbl">مغلقة (أرشيف)</span>
      </div>
    </div>
  </div>

  <div class="row g-3">

    <!-- TENDERS TABLE -->
    <div class="col-12 col-lg-8">
      <div class="panel">
        <div class="phead">
          <span>المنافسات النشطة
            <span id="tCount" style="color:var(--sub);font-weight:500;font-size:.84rem">&nbsp;({{ tenders|length }})</span>
          </span>
          <span style="display:flex;align-items:center;gap:.4rem">
            <span class="rf-count" id="rfCnt"></span>
            <a href="/export/csv" title="تصدير Excel/CSV" style="display:inline-flex;align-items:center;gap:.25rem;
               padding:.25rem .6rem;background:rgba(36,120,72,.1);color:var(--green);
               border:1px solid rgba(36,120,72,.25);border-radius:6px;font-size:.75rem;
               font-weight:700;text-decoration:none;transition:.15s"
               onmouseover="this.style.background='rgba(36,120,72,.18)'"
               onmouseout="this.style.background='rgba(36,120,72,.1)'">
              ⬇️ تصدير
            </a>
            <button onclick="window.print()" title="طباعة" style="display:inline-flex;align-items:center;gap:.25rem;
               padding:.25rem .6rem;background:rgba(26,90,154,.1);color:var(--blue);
               border:1px solid rgba(26,90,154,.25);border-radius:6px;font-size:.75rem;
               font-weight:700;cursor:pointer;transition:.15s;font-family:'Tajawal',sans-serif"
               onmouseover="this.style.background='rgba(26,90,154,.18)'"
               onmouseout="this.style.background='rgba(26,90,154,.1)'">
              🖨️ طباعة
            </button>
          </span>
        </div>
        <div class="srch-bar">
          <div class="srch-wrap">
            <input type="text" id="srch" class="srch-input" placeholder="بحث بالعنوان أو المهندس..." oninput="doSearch(this.value)" autocomplete="off">
            <span class="srch-ico">🔍</span>
            <span class="srch-kbd">/</span>
          </div>
          <div class="fbtns">
            <button class="fbtn fbtn-active" id="fball" onclick="setFilt('all')">الكل</button>
            <button class="fbtn fbtn-r" id="fbr" onclick="setFilt('r')">🔴 حرجة</button>
            <button class="fbtn fbtn-w" id="fbw" onclick="setFilt('w')">🟡 تنبيه</button>
            <button class="fbtn fbtn-g" id="fbg" onclick="setFilt('g')">🟢 مريحة</button>
          </div>
          <span class="srch-res" id="srchRes"></span>
        </div>
        <div class="t-wrap">
          <table>
            <thead>
              <tr>
                <th class="cb-cell"><input type="checkbox" class="cb-row" id="cbAll" title="تحديد الكل" onchange="toggleAll(this)"></th>
                <th style="width:28px">#</th>
                <th class="sortable" data-col="2" onclick="sortTbl(2)">اسم المنافسة</th>
                <th class="sortable" data-col="3" style="width:105px" onclick="sortTbl(3)">تاريخ الإغلاق</th>
                <th class="sortable" data-col="4" style="width:72px;text-align:center" onclick="sortTbl(4)">المتبقي</th>
                <th class="sortable" data-col="5" style="width:90px" onclick="sortTbl(5)">المهندس</th>
                <th style="width:60px;text-align:center">إجراء</th>
              </tr>
            </thead>
            <tbody>
              {% for t in tenders %}
              {% if t.badge == 'danger' %}{% set rc='ru' %}
              {% elif t.badge == 'warning' %}{% set rc='rw' %}
              {% elif t.badge == 'success' %}{% set rc='ro' %}
              {% else %}{% set rc='rg' %}{% endif %}
              <tr class="{{ rc }}{% if t.missing_seen_count and t.missing_seen_count > 0 %} miss{% endif %}" data-id="{{ t.id }}">
                <td class="cb-cell"><input type="checkbox" class="cb-row row-cb" onchange="onRowCb()" data-id="{{ t.id }}"></td>
                <td style="color:var(--sub);font-size:.8rem;font-weight:500">{{ loop.index }}</td>
                <td class="t-title" data-full="{{ t.title|e }}"
                    data-date="{{ t.submission_date[:10] if t.submission_date and t.submission_date != 'N/A' else '' }}"
                    onclick="cpTitle(this)" title="{{ t.title|e }}">
                  {{ t.title }}
                  {% if t.missing_seen_count and t.missing_seen_count > 0 %}
                  <span title="اختفت من البوابة {{ t.missing_seen_count }} مرة متتالية — ستُغلق تلقائياً بعد انتهاء الموعد"
                    style="background:rgba(168,78,26,.13);color:#a84e1a;border:1px solid rgba(168,78,26,.25);
                           border-radius:4px;padding:1px 6px;font-size:.63rem;margin-right:3px;
                           font-weight:600;white-space:nowrap">
                    ⚠️ غائبة {{ t.missing_seen_count }}×
                  </span>
                  {% endif %}
                  {% if t.uploaded_to_platform %}<span title="منشورة على المنصة" style="font-size:.72rem;margin-right:2px">🌐</span>
                  {% elif t.submitted_to_upload %}<span title="مرفوعة لقسم الرفع" style="font-size:.72rem;margin-right:2px">📤</span>
                  {% elif t.submitted_to_review %}<span title="قُدِّمت للمراجعة" style="font-size:.72rem;margin-right:2px">📄</span>{% endif %}
                  {% if t.is_extended %}<span title="مُمدَّدة" style="font-size:.72rem;margin-right:2px">🔄</span>{% endif %}
                </td>
                <td style="color:var(--sub);font-size:.83rem;white-space:nowrap">
                  {{ t.submission_date[:10] if t.submission_date and t.submission_date != 'N/A' else '—' }}
                </td>
                <td style="text-align:center">
                  {% if t.days_left is not none %}
                  {% if t.badge=='danger' %}{% set dc='db-r' %}{% elif t.badge=='warning' %}{% set dc='db-w' %}{% elif t.badge=='success' %}{% set dc='db-g' %}{% else %}{% set dc='db-s' %}{% endif %}
                  <span class="db {{ dc }}">
                    {% if t.days_left < 0 %}منتهية
                    {% elif t.days_left == 0 %}اليوم
                    {% elif t.days_left == 1 %}غداً
                    {% else %}{{ t.days_left }}ي{% endif %}
                  </span>
                  {% else %}<span style="color:var(--muted)">—</span>{% endif %}
                </td>
                <td>
                  {% if t.assigned_engineer %}<span class="echip">{{ t.assigned_engineer }}</span>
                  {% else %}<span style="color:var(--muted)">—</span>{% endif %}
                </td>
                <td style="text-align:center">
                  <div style="display:inline-flex;gap:3px">
                    <a class="abtn" href="/tender/{{ t.id }}" title="تفاصيل وملاحظات"
                       style="text-decoration:none;display:inline-flex;align-items:center;justify-content:center">📋</a>
                    <button class="abtn ae" data-t="{{ t.title|e }}" onclick="openEdit({{ t.id }}, this.dataset.t)" title="تعديل">✏️</button>
                    <button class="abtn ar" data-t="{{ t.title|e }}" onclick="openResult({{ t.id }}, this.dataset.t)" title="تسجيل نتيجة">📝</button>
                  </div>
                </td>
              </tr>
              {% else %}
              <tr><td colspan="7" style="text-align:center;color:var(--muted);padding:2.5rem">لا توجد منافسات نشطة</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- RIGHT PANEL -->
    <div class="col-12 col-lg-4">

      <!-- DYNAMIC CHART -->
      <div class="panel mb-3">
        <div class="phead" style="gap:.5rem;flex-wrap:wrap">
          <div style="position:relative;flex:1;min-width:0;display:flex;align-items:center">
            <select id="chartSel" onchange="switchChart(this.value)" style="
              width:100%;appearance:none;-webkit-appearance:none;
              background:rgba(122,94,40,.12);
              border:1.5px solid var(--amber);border-radius:8px;
              color:var(--text);
              font-family:'Tajawal',sans-serif;font-size:.84rem;font-weight:700;
              cursor:pointer;outline:none;
              padding:.3rem 2rem .3rem .7rem;
              box-shadow:0 1px 3px rgba(0,0,0,.08);
              transition:background .2s,border-color .2s">
              <option value="tenders">📈 توزيع المنافسات</option>
              <option value="owners">🏢 توزيع الجهات المالكة</option>
              <option value="engineers">👷 حمل المهندسين</option>
              <option value="overview">📊 نشطة مقابل مغلقة</option>
              <option value="status_pct">📉 نسبة الضغط</option>
              <option value="trend">📅 الاتجاه اليومي (14 يوم)</option>
            </select>
            <span style="position:absolute;left:.55rem;top:50%;transform:translateY(-50%);
              pointer-events:none;font-size:.65rem;color:var(--amber);line-height:1">▼</span>
          </div>
          <span id="chartSub" style="color:var(--muted);font-size:.72rem;white-space:nowrap">{{ total_active }} نشطة</span>
        </div>
        <div class="pbody" style="padding:.75rem 1rem;transition:all .3s ease">
          <canvas id="dChart"></canvas>
        </div>
      </div>

      <!-- GUARANTEES (v5.6) -->
      <div class="panel mb-3">
        <div class="phead">
          <span>🛡️ الضمانات الابتدائية القادمة</span>
          <span style="color:var(--muted);font-size:.72rem">{{ guarantees|length }}</span>
        </div>
        <div class="pbody" style="padding:.6rem .8rem">
          {% if guarantees %}
            {% for g in guarantees %}
            <a href="/tender/{{ g.id }}" class="g-row {{ g.cls }}">
              <span class="g-badge">{{ g.label }}</span>
              <span class="g-info">
                <span class="g-title">{{ g.title[:46] }}{% if g.title|length > 46 %}…{% endif %}</span>
                <span class="g-owner">{{ g.owner[:30] }} · استحقاق {{ g.due }}{% if g.auto %} (تلقائي){% endif %}</span>
              </span>
            </a>
            {% endfor %}
          {% else %}
            <div style="color:var(--muted);font-size:.8rem;text-align:center;padding:.6rem">لا ضمانات مستحقة قريباً ✓</div>
          {% endif %}
        </div>
      </div>

      <!-- MONTH CALENDAR (v5.6) -->
      <div class="panel mb-3">
        <div class="phead">
          <span>📅 {{ cal.label }}</span>
          <span style="color:var(--muted);font-size:.62rem">🔴 ≤3 · 🟡 ≤7 · 🟢 مريحة · 🛡️ ضمان</span>
        </div>
        <div class="pbody" style="padding:.55rem .7rem">
          <div class="cal-grid">
            {% for h in ['ح','ن','ث','ر','خ','ج','س'] %}<span class="cal-h">{{ h }}</span>{% endfor %}
            {% for w in cal.weeks %}{% for d in w %}
              {% if d == 0 %}<span class="cal-d cal-empty">·</span>
              {% else %}{% set lvl = cal.marks.get(d, 0) %}<span class="cal-d {% if d == cal.today %}cal-today {% endif %}{% if lvl == 4 %}cal-g{% elif lvl == 3 %}cal-r{% elif lvl == 2 %}cal-y{% elif lvl == 1 %}cal-gr{% endif %}">{{ d }}</span>
              {% endif %}
            {% endfor %}{% endfor %}
          </div>
        </div>
      </div>

      <!-- OWNER DISTRIBUTION -->
      {% if owner_dist %}
      <div class="panel mb-3">
        <div class="phead">
          <span>🏢 توزيع الجهات المالكة</span>
          <span style="color:var(--muted);font-size:.72rem">{{ owner_dist|length }} جهة</span>
        </div>
        <div class="pbody">
          {% set max_count = owner_dist.values()|list|max if owner_dist else 1 %}
          {% for owner_name, cnt in owner_dist.items() %}
          <div class="owner-row">
            <span class="owner-name" title="{{ owner_name }}">{{ owner_name[:28] }}{% if owner_name|length > 28 %}…{% endif %}</span>
            <div class="owner-bar-wrap">
              <div class="owner-bar">
                <div class="owner-bar-fill" data-w="{{ (cnt / max_count * 100)|round|int }}"></div>
              </div>
            </div>
            <span class="owner-cnt">{{ cnt }}</span>
          </div>
          {% endfor %}
        </div>
      </div>
      {% endif %}

      <!-- ENGINEERS -->
      <div class="panel">
        <div class="phead">
          <span>👷 حمل المهندسين</span>
          <span style="color:var(--muted);font-size:.72rem">{{ engineers|length }} مهندس</span>
        </div>
        <div class="pbody">
          {% set acolors = ['#388bfd','#a371f7','#d29922','#f85149','#3fb950','#e3b341','#58a6ff','#ffa657'] %}
          {% for eng in engineers %}
          {% set ld = eng_load.get(eng.name,{}) %}
          {% set pct = ld.get('pct',0) %}
          {% set hx  = ld.get('hex','#3fb950') %}
          {% set ai  = loop.index0 % 8 %}
          <div class="ecard">
            <div style="display:flex;align-items:center;gap:.65rem">
              <div class="eavatar" style="background:{{ acolors[ai] }}">{{ eng.name[2:3] if eng.name.startswith('ال') else eng.name[:1] }}</div>
              <div style="flex:1;min-width:0">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                  <span style="font-weight:600;font-size:.88rem">{{ eng.name }}</span>
                  <span style="color:var(--sub);font-size:.82rem;font-weight:600">{{ ld.get('count',0) }}/{{ ld.get('capacity',5) }}</span>
                </div>
                <div class="ebar">
                  <div class="ebar-fill" data-w="{{ pct }}" style="background:{{ hx }}"></div>
                </div>
              </div>
              <span style="font-size:.82rem;font-weight:700;color:{{ hx }};min-width:34px;text-align:left">{{ pct }}%</span>
            </div>
          </div>
          {% else %}
          <p style="color:var(--muted);text-align:center;padding:1rem">لا يوجد مهندسون</p>
          {% endfor %}
        </div>
      </div>

    </div>
  </div>
</div>

<!-- EDIT MODAL -->
<div class="modal fade" id="editModal" tabindex="-1" role="dialog" aria-modal="true" aria-labelledby="editModalLabel">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h6 id="editModalLabel" class="modal-title" style="font-size:.95rem">✏️ تعديل المنافسة</h6>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="إغلاق"></button>
      </div>
      <div class="modal-body">
        <p id="modalTitle" style="color:var(--muted);font-size:.82rem;margin-bottom:1rem;padding:.5rem .75rem;background:var(--hover);border-radius:7px;border:1px solid var(--border)"></p>
        <div class="mb-3">
          <label class="form-label">👷 المهندس المسؤول</label>
          <select id="engSelect" class="form-select"></select>
          <button type="button" id="lockBtn" onclick="toggleEngineerLock()" title="قفل/فتح تعيين المهندس" style="margin-top:.5rem;padding:.45rem .8rem;border-radius:7px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.06);color:#aaa;cursor:pointer;font-size:.88rem;width:100%;text-align:center;transition:background .15s,color .15s,border-color .15s">🔓 تعيين مفتوح — انقر للقفل</button>
        </div>
        <div>
          <label class="form-label">📅 تاريخ الإغلاق</label>
          <input type="date" id="dateInput" class="form-control">
          <button type="button" id="dateLockBtn" onclick="toggleDateLock()" title="قفل/فتح تاريخ التقديم" style="margin-top:.5rem;padding:.45rem .8rem;border-radius:7px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.06);color:#aaa;cursor:pointer;font-size:.88rem;width:100%;text-align:center;transition:background .15s,color .15s,border-color .15s">🔓 تاريخ مفتوح — انقر للقفل</button>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">إلغاء</button>
        <button id="saveBtn" class="btn btn-success btn-sm px-4" onclick="saveEdit()">💾 حفظ</button>
      </div>
    </div>
  </div>
</div>

<!-- RESULT MODAL -->
<div class="modal fade" id="resultModal" tabindex="-1" role="dialog" aria-modal="true" aria-labelledby="resultModalLabel">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h6 id="resultModalLabel" class="modal-title" style="font-size:.95rem">📝 تسجيل النتيجة</h6>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="إغلاق"></button>
      </div>
      <div class="modal-body">
        <p id="resultTitle" style="color:var(--muted);font-size:.82rem;margin-bottom:1rem;padding:.5rem .75rem;background:var(--hover);border-radius:7px;border:1px solid var(--border)"></p>
        <div class="mb-3">
          <label class="form-label">هل قدّمنا عرضاً؟</label>
          <div style="display:flex;gap:.5rem">
            <button id="btnYes" onclick="setSubmit(true)" type="button" class="btn btn-sm btn-outline-success" style="flex:1">✅ نعم، قدّمنا</button>
            <button id="btnNo"  onclick="setSubmit(false)" type="button" class="btn btn-sm btn-outline-secondary" style="flex:1">❌ لم نقدّم</button>
          </div>
        </div>
        <div id="resultSection" class="mb-3">
          <label class="form-label">النتيجة</label>
          <div style="display:flex;gap:.4rem;flex-wrap:wrap">
            <button type="button" class="btn btn-sm btn-outline-success result-btn" onclick="setResult('won')">🏆 فزنا</button>
            <button type="button" class="btn btn-sm btn-outline-danger result-btn" onclick="setResult('lost')">❌ خسرنا</button>
            <button type="button" class="btn btn-sm btn-outline-warning result-btn" onclick="setResult('pending')">⏳ معلق</button>
            <button type="button" class="btn btn-sm btn-outline-secondary result-btn" onclick="setResult('unknown')">⚪ لم تُعلن</button>
            <button type="button" class="btn btn-sm btn-outline-secondary result-btn" onclick="setResult('cancelled')">🚫 ملغي</button>
          </div>
        </div>
        <div id="priceSection" class="row g-2 mb-3">
          <div class="col-6">
            <label class="form-label">سعرنا المقدَّم (ريال)</label>
            <input type="number" id="ourPrice" class="form-control" placeholder="0.00" step="0.01">
          </div>
          <div class="col-6">
            <label class="form-label">سعر الفائز (اختياري)</label>
            <input type="number" id="winPrice" class="form-control" placeholder="0.00" step="0.01">
          </div>
        </div>
        <div>
          <label class="form-label">ملاحظات</label>
          <textarea id="resultNotes" class="form-control" rows="2" placeholder="أي تفاصيل إضافية..."></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">إلغاء</button>
        <button id="saveResultBtn" class="btn btn-success btn-sm px-4" onclick="saveResult()">💾 حفظ النتيجة</button>
      </div>
    </div>
  </div>
</div>

<!-- PENDING TENDERS MODAL -->
<div class="modal fade" id="pendingModal" tabindex="-1" role="dialog" aria-modal="true" aria-labelledby="pendingModalLabel">
  <div class="modal-dialog modal-dialog-centered modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h6 id="pendingModalLabel" class="modal-title" style="font-size:.95rem">⏳ المنافسات بانتظار الاعتماد
          <span style="background:rgba(168,78,26,.15);color:var(--orange);border-radius:20px;
                padding:1px 8px;font-size:.78rem;margin-right:.5rem;font-weight:700">{{ pending_count }}</span>
        </h6>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="إغلاق"></button>
      </div>
      <div class="modal-body" style="padding:.75rem">
        {% if pending_tenders %}
        <div style="overflow-x:auto">
          <table style="width:100%;border-collapse:collapse">
            <thead>
              <tr style="background:var(--head);border-bottom:1px solid var(--border)">
                <th style="padding:.5rem .75rem;font-size:.78rem;color:var(--sub);font-weight:700;text-align:right">اسم المنافسة</th>
                <th style="padding:.5rem .75rem;font-size:.78rem;color:var(--sub);font-weight:700;width:110px">نوع التغيير</th>
                <th style="padding:.5rem .75rem;font-size:.78rem;color:var(--sub);font-weight:700;width:115px">المهندس المقترح</th>
                <th style="padding:.5rem .75rem;font-size:.78rem;color:var(--sub);font-weight:700;width:100px">تاريخ الإغلاق</th>
                <th style="padding:.5rem .75rem;font-size:.78rem;color:var(--sub);font-weight:700;width:130px;text-align:center">إجراء</th>
              </tr>
            </thead>
            <tbody>
              {% for p in pending_tenders %}
              <tr id="prow-{{ p.id }}" style="border-bottom:1px solid rgba(180,140,40,.2)">
                <td style="padding:.5rem .75rem;font-size:.84rem;color:var(--text)">
                  <span title="{{ p.title|e }}">{{ p.title }}</span>
                  {% if p.approval_stage == 'awaiting_engineer' %}
                  <br><span style="background:rgba(200,144,64,.12);color:var(--yellow);border-radius:4px;padding:0 5px;font-size:.68rem;font-weight:700">🔧 بانتظار موافقة المهندس</span>
                  {% elif p.approval_stage == 'awaiting_manager' %}
                  <br><span style="background:rgba(26,90,154,.12);color:var(--blue);border-radius:4px;padding:0 5px;font-size:.68rem;font-weight:700">👔 بانتظار موافقة المدير</span>
                  {% endif %}
                </td>
                <td style="padding:.5rem .75rem">
                  {% if p.change_type == 'NEW_TENDER' or p.change_type == 'NEW' %}
                  <span style="background:rgba(26,90,154,.1);color:var(--blue);border-radius:4px;padding:1px 6px;font-size:.72rem;font-weight:700;border:1px solid rgba(26,90,154,.2)">جديدة</span>
                  {% elif 'DATE' in (p.change_type or '') %}
                  <span style="background:rgba(200,144,64,.1);color:var(--yellow);border-radius:4px;padding:1px 6px;font-size:.72rem;font-weight:700;border:1px solid rgba(200,144,64,.2)">تعديل تاريخ</span>
                  {% elif 'ENG' in (p.change_type or '') %}
                  <span style="background:rgba(100,60,160,.1);color:var(--purple);border-radius:4px;padding:1px 6px;font-size:.72rem;font-weight:700;border:1px solid rgba(100,60,160,.2)">تعيين مهندس</span>
                  {% else %}
                  <span style="background:rgba(139,148,158,.1);color:var(--muted);border-radius:4px;padding:1px 6px;font-size:.72rem;border:1px solid var(--border)">{{ p.change_type or '—' }}</span>
                  {% endif %}
                </td>
                <td style="padding:.5rem .75rem">
                  {% if p.suggested_engineer %}
                  <span style="color:var(--amber-l);font-size:.8rem;font-weight:600">{{ p.suggested_engineer }}</span>
                  {% else %}<span style="color:var(--muted)">—</span>{% endif %}
                </td>
                <td style="padding:.5rem .75rem;font-size:.8rem;color:var(--sub)">
                  {{ (p.submission_date or '')[:10] or '—' }}
                </td>
                <td style="padding:.5rem .75rem;text-align:center">
                  <div style="display:inline-flex;gap:.3rem">
                    <button onclick="approvePending({{ p.id }}, '{{ p.suggested_engineer or '' }}')"
                      style="background:rgba(36,120,72,.12);color:var(--green);border:1px solid rgba(36,120,72,.3);
                             border-radius:6px;padding:.25rem .6rem;font-size:.75rem;font-weight:700;
                             cursor:pointer;font-family:'Tajawal',sans-serif;transition:.15s"
                      onmouseover="this.style.background='rgba(36,120,72,.22)'"
                      onmouseout="this.style.background='rgba(36,120,72,.12)'">✅ اعتماد</button>
                    <button onclick="rejectPending({{ p.id }})"
                      style="background:rgba(176,40,40,.08);color:var(--red);border:1px solid rgba(176,40,40,.25);
                             border-radius:6px;padding:.25rem .6rem;font-size:.75rem;font-weight:700;
                             cursor:pointer;font-family:'Tajawal',sans-serif;transition:.15s"
                      onmouseover="this.style.background='rgba(176,40,40,.18)'"
                      onmouseout="this.style.background='rgba(176,40,40,.08)'">❌ رفض</button>
                  </div>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% else %}
        <p style="text-align:center;color:var(--muted);padding:2rem">لا توجد منافسات بانتظار الاعتماد</p>
        {% endif %}
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">إغلاق</button>
      </div>
    </div>
  </div>
</div>

<!-- BULK ASSIGN TOOLBAR -->
<div id="bulkBar">
  <span class="blbl" id="bulkLbl">0 محددة</span>
  <select id="bulkEng">
    <option value="">— اختر مهندساً —</option>
    {% for eng in engineers %}
    <option value="{{ eng.name }}">{{ eng.name }}</option>
    {% endfor %}
  </select>
  <button class="bapply" onclick="applyBulk()">✅ تعيين</button>
  <button class="bcancel" onclick="clearSel()">✕ إلغاء</button>
</div>

<div id="tw"><div id="toast" class="tmsg"></div></div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
// ── DYNAMIC CHART ENGINE ─────────────────────────────
const _pal = ['#388bfd','#a371f7','#d29922','#f85149','#3fb950','#e3b341','#58a6ff','#ffa657','#79c0ff','#d2a8ff'];
const _pal2 = _pal.map(c => c + 'b0'); // semi-transparent version

const _ownerData   = {{ owner_dist | tojson }};
const _engLoadData = {{ eng_load | tojson }};
const _engNames    = [{% for e in engineers %}'{{ e.name }}',{% endfor %}];
const _dailyTrend  = {{ daily_trend | tojson }};

const _chartSets = {
  tenders: {
    sub:'{{ total_active }} نشطة',
    ctype:'doughnut', cutout:true,
    labels:['حرجة ≤3ي','تنبيه 4-7ي','مريحة >7ي','منتهية التاريخ'],
    data:[{{ urgent }},{{ warning }},{{ ok_count }},{{ expired }}],
    bg:['rgba(248,81,73,.65)','rgba(227,179,65,.65)','rgba(63,185,80,.65)','rgba(139,148,158,.35)'],
    bdr:['#f85149','#e3b341','#3fb950','#8b949e'],
  },
  owners: {
    sub:Object.keys(_ownerData).length+' جهة',
    ctype:'bar', horiz:true,
    labels:Object.keys(_ownerData).map(k=>k.length>22?k.slice(0,22)+'…':k),
    data:Object.values(_ownerData),
    bg:Object.keys(_ownerData).map((_,i)=>_pal2[i%_pal.length]),
    bdr:Object.keys(_ownerData).map((_,i)=>_pal[i%_pal.length]),
  },
  engineers: {
    sub:_engNames.length+' مهندس',
    ctype:'bar', horiz:false,
    labels:_engNames,
    data:_engNames.map(n=>(_engLoadData[n]||{}).count||0),
    bg:_engNames.map(n=>{const h=(_engLoadData[n]||{}).hex||'#3fb950';return h+'b0';}),
    bdr:_engNames.map(n=>(_engLoadData[n]||{}).hex||'#3fb950'),
    cap:_engNames.map(n=>(_engLoadData[n]||{}).capacity||5),
  },
  overview: {
    sub:'{{ total_active + closed_count }} إجمالي',
    ctype:'doughnut', cutout:true,
    labels:['نشطة','مغلقة (أرشيف)'],
    data:[{{ total_active }},{{ closed_count }}],
    bg:['rgba(63,185,80,.65)','rgba(139,148,158,.35)'],
    bdr:['#3fb950','#8b949e'],
  },
  status_pct: {
    sub:'مؤشر الضغط',
    ctype:'bar', horiz:false,
    labels:_engNames,
    data:_engNames.map(n=>(_engLoadData[n]||{}).pct||0),
    bg:_engNames.map(n=>{const p=(_engLoadData[n]||{}).pct||0;
      return p>=85?'rgba(248,81,73,.65)':p>=60?'rgba(227,179,65,.65)':'rgba(63,185,80,.65)';}),
    bdr:_engNames.map(n=>(_engLoadData[n]||{}).hex||'#3fb950'),
    isPercent:true,
  },
  trend: {
    sub:_dailyTrend.data.reduce((a,b)=>a+b,0)+' منافسة جديدة',
    ctype:'line',
    labels:_dailyTrend.labels,
    data:_dailyTrend.data,
    bg:'rgba(56,139,253,.15)',
    bdr:'#388bfd',
  },
};

let _chartInst = null;

function switchChart(type) {
  const ds = _chartSets[type];
  if (!ds) return;
  const canvas = document.getElementById('dChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (_chartInst) { _chartInst.destroy(); _chartInst = null; }

  // Adjust canvas height
  if (ds.horiz) canvas.style.maxHeight = Math.max(130, ds.labels.length * 30) + 'px';
  else if (ds.ctype === 'bar') canvas.style.maxHeight = '185px';
  else canvas.style.maxHeight = '210px';

  const isDoughnut = ds.ctype === 'doughnut';
  const isLine = ds.ctype === 'line';
  let cfg;
  if (isLine) {
    cfg = {
      type:'line',
      data:{ labels:ds.labels, datasets:[{
        data:ds.data, label:'منافسات جديدة',
        borderColor:ds.bdr, backgroundColor:ds.bg,
        fill:true, tension:.3, borderWidth:2,
        pointRadius:3, pointBackgroundColor:ds.bdr,
      }]},
      options:{
        animation:{duration:550,easing:'easeOutQuart'},
        plugins:{
          legend:{display:false},
          tooltip:{callbacks:{label:c=>` ${c.raw} منافسة`}}
        },
        scales:{
          x:{ticks:{color:'#7a5e28',font:{family:'Tajawal',size:9}},
            grid:{color:'transparent'}},
          y:{beginAtZero:true,ticks:{color:'#7a5e28',font:{family:'Tajawal',size:10},stepSize:1},
            grid:{color:'rgba(180,140,40,.12)'}}
        }
      }
    };
  } else if (isDoughnut) {
    cfg = {
      type:'doughnut',
      data:{ labels:ds.labels, datasets:[{
        data:ds.data, backgroundColor:ds.bg, borderColor:ds.bdr,
        borderWidth:1.5, hoverOffset:7
      }]},
      options:{
        cutout:'70%',
        animation:{duration:550,easing:'easeOutQuart'},
        plugins:{
          legend:{position:'bottom',labels:{color:'#7a5e28',font:{family:'Tajawal',size:11},boxWidth:10,padding:12}},
          tooltip:{callbacks:{label:c=>` ${c.label}: ${c.raw} منافسة`}}
        }
      }
    };
  } else {
    // Build datasets — add capacity line for engineers if available
    const datasets = [{
      data:ds.data,
      backgroundColor:ds.bg,
      borderColor:ds.bdr,
      borderWidth:1.5,
      borderRadius:5,
      borderSkipped:false,
      label:'المنافسات'
    }];
    if (ds.cap) {
      datasets.push({
        type:'line',
        data:ds.cap,
        label:'الطاقة القصوى',
        borderColor:'rgba(138,72,0,.5)',
        borderDash:[5,4],
        borderWidth:1.5,
        pointRadius:3,
        pointBackgroundColor:'rgba(138,72,0,.6)',
        fill:false,
        tension:0,
      });
    }
    cfg = {
      type:'bar',
      data:{ labels:ds.labels, datasets},
      options:{
        indexAxis: ds.horiz ? 'y' : 'x',
        animation:{duration:450,easing:'easeOutQuart'},
        plugins:{
          legend:{display:!!ds.cap,
            labels:{color:'#7a5e28',font:{family:'Tajawal',size:10},boxWidth:10}},
          tooltip:{callbacks:{label:c=>` ${c.raw}${ds.isPercent?'%':' منافسة'}`}}
        },
        scales:{
          x:{ticks:{color:'#7a5e28',font:{family:'Tajawal',size:10},
              maxRotation:ds.horiz?0:35},
            grid:{color:'rgba(180,140,40,.12)'},
            ...(ds.isPercent?{max:100}:{})},
          y:{ticks:{color:'#4a3810',font:{family:'Tajawal',size:10}},
            grid:{color:ds.horiz?'rgba(180,140,40,.12)':'transparent'},
            ...(ds.isPercent?{max:100}:{})}
        }
      }
    };
  }
  _chartInst = new Chart(ctx, cfg);
  const sub = document.getElementById('chartSub');
  if (sub) { sub.style.opacity='0'; setTimeout(()=>{sub.textContent=ds.sub;sub.style.opacity='1';},150); }
}

// Init on load
switchChart('tenders');

// ── ENTRANCE ANIMATION ENGINE ─────────────────────────────
(function(){
  const E4 = t => 1 - Math.pow(1-t, 4);

  // 1. Stat cards stagger in + number count-up
  document.querySelectorAll('.scard').forEach((card, i) => {
    const delay = 40 + i * 90;
    card.style.animation = `fadeUp .5s cubic-bezier(.25,1,.5,1) ${delay}ms both`;
    const num = card.querySelector('.snum');
    if (num) {
      const target = parseInt(num.textContent.trim(), 10) || 0;
      if (target > 0) {
        const orig = num.textContent.trim();
        num.textContent = '0';
        const s = performance.now(), dur = 900;
        const tick = n => {
          const p = Math.min((n - s) / dur, 1);
          num.textContent = Math.round(target * E4(p));
          if (p < 1) requestAnimationFrame(tick);
          else num.textContent = orig;
        };
        setTimeout(() => requestAnimationFrame(tick), delay + 20);
      }
    }
  });

  // 2. Panels fade in after cards
  document.querySelectorAll('.panel').forEach((p, i) => {
    p.style.animation = `fadeIn .42s ease-out ${300 + i * 70}ms both`;
  });

  // 3. Table rows stagger in — translateY on mobile (cards), translateX on desktop (table)
  const isMobileView = window.matchMedia('(max-width:768px)').matches;
  document.querySelectorAll('tbody tr').forEach((tr, i) => {
    const delay = 330 + Math.min(i, 17) * 22;
    const isMiss = tr.classList.contains('miss');
    tr.style.opacity = '0';
    tr.style.transform = isMobileView ? 'translateY(10px)' : 'translateX(6px)';
    setTimeout(() => {
      tr.style.transition = 'opacity .28s ease, transform .38s cubic-bezier(.22,1,.36,1)';
      tr.style.opacity = isMiss ? '0.45' : '1';
      tr.style.transform = 'translate(0,0)';
      setTimeout(() => {
        tr.style.transition = isMobileView ? '' : 'background .1s';
      }, 420);
    }, delay);
  });

  // 4. Engineer bars: GPU-accelerated scaleX
  document.querySelectorAll('.ebar-fill[data-w]').forEach((el, i) => {
    setTimeout(() => {
      el.style.transform = 'scaleX(' + (parseInt(el.dataset.w, 10) / 100) + ')';
    }, 520 + i * 70);
  });

  // 5. Owner distribution bars
  document.querySelectorAll('.owner-bar-fill[data-w]').forEach((el, i) => {
    setTimeout(() => {
      el.style.transform = 'scaleX(' + (parseInt(el.dataset.w, 10) / 100) + ')';
    }, 600 + i * 50);
  });
})();

// ── SEARCH + FILTER ──────────────────────────────────
let _filt='all';
function doSearch(q){_applyView(q,_filt);}
function setFilt(f){
  _filt=f;
  document.querySelectorAll('.fbtn').forEach(b=>b.classList.remove('fbtn-active'));
  const btn=document.getElementById('fb'+f);
  if(btn)btn.classList.add('fbtn-active');
  _applyView(document.getElementById('srch').value.trim(),f);
}
function _titleHas(t,q){
  // Arabic word-boundary: match only when query is not followed by another Arabic letter
  if(!t.includes(q))return false;
  let idx=t.indexOf(q);
  while(idx>=0){
    const after=t.charCodeAt(idx+q.length);
    if(isNaN(after)||after<0x0600||after>0x06ff)return true;
    idx=t.indexOf(q,idx+1);
  }
  return false;
}
function _applyView(q,f){
  q=(q||'').toLowerCase();
  let vis=0,total=0;
  document.querySelectorAll('tbody tr').forEach(tr=>{
    total++;
    const titleEl=tr.querySelector('.t-title')||tr.cells[2];
    const title=(titleEl?.textContent||'').toLowerCase();
    const eng=(tr.querySelector('.echip')?.textContent||'').toLowerCase();
    const mQ=!q||_titleHas(title,q)||eng.includes(q);
    const mF=f==='all'||(f==='r'&&tr.classList.contains('ru'))
             ||(f==='w'&&tr.classList.contains('rw'))
             ||(f==='g'&&tr.classList.contains('ro'));
    const show=mQ&&mF;
    tr.style.display=show?'':'none';
    // Uncheck hidden rows so they're excluded from bulk actions
    if(!show){const cb=tr.querySelector('.row-cb');if(cb&&cb.checked){cb.checked=false;tr.classList.remove('sel-row');}}
    if(show)vis++;
  });
  onRowCb();
  const res=document.getElementById('srchRes');
  if(res){
    const txt=(q||f!=='all')?`${vis} من ${total} نتيجة`:'';
    if(res.textContent!==txt){
      res.style.opacity='0';
      setTimeout(()=>{res.textContent=txt;res.style.opacity='1';},120);
    }
  }
  const tc=document.getElementById('tCount');
  if(tc)tc.textContent=` (${vis})`;
}

// ── SORT ─────────────────────────────────────────────
let _sCol=-1,_sDir=1;
function sortTbl(col){
  if(_sCol===col)_sDir*=-1; else{_sCol=col;_sDir=1;}
  document.querySelectorAll('th.sortable').forEach(h=>{
    h.classList.remove('sort-asc','sort-desc');
    if(+h.dataset.col===col)h.classList.add(_sDir>0?'sort-asc':'sort-desc');
  });
  const tb=document.querySelector('tbody');
  [...tb.querySelectorAll('tr')].sort((a,b)=>{
    const av=(a.cells[col]?.textContent||'').trim();
    const bv=(b.cells[col]?.textContent||'').trim();
    const an=parseFloat(av),bn=parseFloat(bv);
    if(!isNaN(an)&&!isNaN(bn))return(an-bn)*_sDir;
    return av.localeCompare(bv,'ar')*_sDir;
  }).forEach(r=>tb.appendChild(r));
}

// ── COPY TITLE ───────────────────────────────────────
function cpTitle(td){
  const t=td.dataset.full||td.textContent.trim();
  // Flash animation — restart via reflow
  td.classList.remove('flashing');
  void td.offsetWidth;
  td.classList.add('flashing');
  setTimeout(()=>td.classList.remove('flashing'),560);
  if(navigator.clipboard){navigator.clipboard.writeText(t).then(()=>toast('✅ تم نسخ العنوان'));}
  else{const i=document.createElement('input');i.value=t;document.body.appendChild(i);i.select();document.execCommand('copy');document.body.removeChild(i);toast('✅ تم نسخ العنوان');}
}

// ── TOPBAR SCROLL ELEVATION ───────────────────────────
(function(){
  const tb=document.querySelector('.topbar');
  if(!tb)return;
  const onScroll=()=>tb.classList.toggle('elevated',window.scrollY>6);
  window.addEventListener('scroll',onScroll,{passive:true});
  onScroll();
})();

// ── KEYBOARD SHORTCUTS ───────────────────────────────
document.addEventListener('keydown',e=>{
  const active=document.activeElement;
  const inInput=active.tagName==='INPUT'||active.tagName==='TEXTAREA'||active.tagName==='SELECT';
  if(e.key==='/'&&!inInput){e.preventDefault();const s=document.getElementById('srch');if(s){s.focus();s.select();}}
  if(e.key==='Escape'&&active===document.getElementById('srch')){document.getElementById('srch').value='';doSearch('');active.blur();}
});

// ── TAB BADGE ────────────────────────────────────────
(function(){const u={{ urgent }};if(u>0)document.title=`(${u}🔴) {{ co.short_ar }} — المنافسات`;})();

// ── REFRESH COUNTDOWN ────────────────────────────────
(function(){
  let s=300;const el=document.getElementById('rfCnt');if(!el)return;
  const t=()=>{
    if(s<=0){el.textContent='جاري التحديث...';return;}
    const m=Math.floor(s/60),sc=s%60;
    el.textContent=`تحديث: ${m}:${sc<10?'0':''}${sc}`;
    el.className='rf-count'+(s<=30?' soon':'');
    s--;setTimeout(t,1000);
  };t();
})();

// ── POPULATE FILTER BUTTON COUNTS ────────────────────
(function(){
  let ru=0,rw=0,ro=0;
  document.querySelectorAll('tbody tr').forEach(tr=>{
    if(tr.classList.contains('ru'))ru++;
    else if(tr.classList.contains('rw'))rw++;
    else if(tr.classList.contains('ro'))ro++;
  });
  const fbr=document.getElementById('fbr');
  const fbw=document.getElementById('fbw');
  const fbg=document.getElementById('fbg');
  if(fbr)fbr.textContent=`🔴 حرجة${ru?' ('+ru+')':''}`;
  if(fbw)fbw.textContent=`🟡 تنبيه${rw?' ('+rw+')':''}`;
  if(fbg)fbg.textContent=`🟢 مريحة${ro?' ('+ro+')':''}`;
})();

// ── BULK ASSIGN ──────────────────────────────────────
function onRowCb(){
  const all=document.querySelectorAll('.row-cb');
  const checked=[...all].filter(c=>c.checked&&c.closest('tr').style.display!=='none');
  const bb=document.getElementById('bulkBar');
  const lbl=document.getElementById('bulkLbl');
  const ca=document.getElementById('cbAll');
  if(lbl)lbl.textContent=checked.length+' محددة';
  if(bb)bb.classList.toggle('show',checked.length>0);
  if(ca){
    const vis=[...all].filter(c=>c.closest('tr').style.display!=='none');
    ca.indeterminate=checked.length>0&&checked.length<vis.length;
    ca.checked=vis.length>0&&checked.length===vis.length;
  }
}
function toggleAll(cb){
  const vis=document.querySelectorAll('tbody tr');
  vis.forEach(tr=>{
    if(tr.style.display==='none')return;
    const c=tr.querySelector('.row-cb');
    if(c)c.checked=cb.checked;
    tr.classList.toggle('sel-row',cb.checked);
  });
  onRowCb();
}
document.querySelectorAll('.row-cb').forEach(c=>{
  c.addEventListener('change',function(){
    const tr=this.closest('tr');
    if(tr)tr.classList.toggle('sel-row',this.checked);
    onRowCb();
  });
});
function clearSel(){
  document.querySelectorAll('.row-cb').forEach(c=>{c.checked=false;});
  document.querySelectorAll('tbody tr').forEach(tr=>tr.classList.remove('sel-row'));
  const ca=document.getElementById('cbAll');if(ca){ca.checked=false;ca.indeterminate=false;}
  const bb=document.getElementById('bulkBar');if(bb)bb.classList.remove('show');
  const lbl=document.getElementById('bulkLbl');if(lbl)lbl.textContent='0 محددة';
}
function applyBulk(){
  const eng=document.getElementById('bulkEng').value;
  if(!eng){toast('اختر مهندساً أولاً',1);return;}
  const ids=[...document.querySelectorAll('.row-cb:checked')].map(c=>+c.dataset.id).filter(Boolean);
  if(!ids.length){toast('لم تحدد أي منافسة',1);return;}
  requirePin(()=>{
    const btn=document.querySelector('#bulkBar .bapply');
    if(btn){btn.disabled=true;btn.textContent='⏳';}
    fetch('/api/bulk_assign',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({engineer:eng,ids:ids})
    }).then(r=>r.json()).then(d=>{
      if(d.ok){toast(d.message||'✅ تم التعيين');clearSel();setTimeout(()=>location.reload(),1800);}
      else toast(d.error||'فشل',1);
    }).catch(()=>toast('خطأ في الاتصال',1))
    .finally(()=>{if(btn){btn.disabled=false;btn.textContent='✅ تعيين';}});
  });
}

let cid=null, didSub=null, resVal='pending';
const M  = new bootstrap.Modal(document.getElementById('editModal'));
const RM = new bootstrap.Modal(document.getElementById('resultModal'));

function setSubmit(v){
  didSub=v;
  document.getElementById('btnYes').className='btn btn-sm '+(v?'btn-success':'btn-outline-success')+' flex-fill';
  document.getElementById('btnNo').className='btn btn-sm '+(!v?'btn-secondary':'btn-outline-secondary')+' flex-fill';
  document.getElementById('resultSection').style.display=v?'':'none';
  document.getElementById('priceSection').style.display=v?'':'none';
}
function setResult(v){
  resVal=v;
  document.querySelectorAll('.result-btn').forEach(b=>b.classList.toggle('active',b.getAttribute('onclick').includes("'"+v+"'")));
}
function openResult(id,t){
  cid=id;didSub=null;resVal='pending';
  document.getElementById('resultTitle').textContent=t;
  ['ourPrice','winPrice'].forEach(i=>document.getElementById(i).value='');
  document.getElementById('resultNotes').value='';
  setSubmit(null);
  document.getElementById('resultSection').style.display='';
  document.getElementById('priceSection').style.display='';
  fetch('/api/result/'+id).then(r=>r.json()).then(d=>{
    if(d.existing){const ex=d.existing;setSubmit(ex.did_submit===1);setResult(ex.result||'pending');
      if(ex.our_price)document.getElementById('ourPrice').value=ex.our_price;
      if(ex.winning_price)document.getElementById('winPrice').value=ex.winning_price;
      if(ex.notes)document.getElementById('resultNotes').value=ex.notes;}
    RM.show();
  }).catch(()=>RM.show());
}
function saveResult(){
  if(didSub===null){toast('حدد هل قدّمنا أم لا',1);return;}
  const b=document.getElementById('saveResultBtn');b.disabled=true;b.textContent='⏳';
  fetch('/api/result/'+cid+'/save',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({did_submit:didSub,result:resVal,
      our_price:document.getElementById('ourPrice').value,
      win_price:document.getElementById('winPrice').value,
      notes:document.getElementById('resultNotes').value})
  }).then(r=>r.json()).then(d=>{if(d.ok){RM.hide();toast('✅ تم حفظ النتيجة');}else toast(d.error||'فشل',1);})
  .catch(()=>toast('خطأ في الاتصال',1)).finally(()=>{b.disabled=false;b.textContent='💾 حفظ النتيجة';});
}
function openEdit(id,t){
  requirePin(()=>{
    cid=id;document.getElementById('modalTitle').textContent=t;
    document.getElementById('engSelect').innerHTML='<option>جاري التحميل...</option>';
    document.getElementById('dateInput').value='';
    fetch('/api/tender/'+id).then(r=>r.json()).then(d=>{
      const s=document.getElementById('engSelect');
      s.innerHTML='<option value="">— لا تغيير —</option>';
      d.engineers.forEach(n=>{const o=document.createElement('option');o.value=n;o.textContent=n;if(n===d.engineer)o.selected=true;s.appendChild(o);});
      if(d.date)document.getElementById('dateInput').value=d.date;
      const _dlb=document.getElementById('dateLockBtn');
      if(_dlb){_dlb.textContent=d.date_locked?'🔒 تاريخ مقفول — انقر للفتح':'🔓 تاريخ مفتوح — انقر للقفل';_dlb.style.borderColor=d.date_locked?'#ffc107':'rgba(255,255,255,.25)';_dlb.style.color=d.date_locked?'#ffc107':'#aaa';}
      const _lb=document.getElementById('lockBtn');
      if(_lb){_lb.textContent=d.locked?'🔒 تعيين مقفول — انقر للفتح':'🔓 تعيين مفتوح — انقر للقفل';_lb.style.borderColor=d.locked?'#ffc107':'rgba(255,255,255,.25)';_lb.style.color=d.locked?'#ffc107':'#aaa';}
      M.show();
    }).catch(()=>toast('خطأ في التحميل',1));
  });
}

// ── فتح نافذة التعديل تلقائياً لو جاي رابط من صفحة التفاصيل (?edit=<id>) ──
// ملحوظة: استدعاء openEdit() مؤجَّل عبر setTimeout عمداً -- لو اتنادى فوراً هنا
// (قبل نهاية تنفيذ السكربت بالكامل) بيطلع خطأ TDZ حقيقي لأن requirePin() بيستخدم
// "let _pinCb" المُعرَّفة لاحقاً أسفل الملف -- ثبتنا الخطأ ده فعلياً على السيرفر الحي.
(function(){
  const _p = new URLSearchParams(location.search);
  const _eid = _p.get('edit');
  if(_eid){
    setTimeout(function(){ openEdit(parseInt(_eid,10), ''); }, 400);
    const _u = new URL(location.href);
    _u.searchParams.delete('edit');
    history.replaceState({}, '', _u.pathname + _u.search);
  }
})();

  function toggleDateLock(){
    if(!cid)return;
    fetch('/api/tender/'+cid+'/toggle-date-lock',{method:'POST'})
      .then(r=>r.json()).then(d=>{
        const btn=document.getElementById('dateLockBtn');
        if(btn){btn.textContent=d.locked?'🔒 تاريخ مقفول — انقر للفتح':'🔓 تاريخ مفتوح — انقر للقفل';btn.style.borderColor=d.locked?'#ffc107':'rgba(255,255,255,.2)';btn.style.color=d.locked?'#ffc107':'#aaa';}
        toast(d.locked?'🔒 التاريخ مقفول — لن يتغير تلقائياً':'🔓 التاريخ مفتوح',0);
      }).catch(()=>toast('خطأ',1));
  }
  
  function toggleEngineerLock(){
    if(!cid)return;
    fetch('/api/tender/'+cid+'/toggle-lock',{method:'POST'})
      .then(r=>r.json()).then(d=>{
        const btn=document.getElementById('lockBtn');
        if(btn){
          btn.textContent=d.locked?'🔒 تعيين مقفول — انقر للفتح':'🔓 تعيين مفتوح — انقر للقفل';
          btn.style.borderColor=d.locked?'#ffc107':'rgba(255,255,255,.25)';
          btn.style.color=d.locked?'#ffc107':'#aaa';
        }
        toast(d.locked?'🔒 تعيين المهندس مقفول — لن يتغير تلقائياً':'🔓 تعيين المهندس مفتوح',0);
      }).catch(()=>toast('خطأ في الاتصال',1));
  }
  function saveEdit(){
  const eng=document.getElementById('engSelect').value;
  const dt=document.getElementById('dateInput').value;
  if(!eng&&!dt){toast('لم تقم بأي تعديل',1);return;}
  const b=document.getElementById('saveBtn');b.disabled=true;b.textContent='⏳';
  fetch('/api/tender/'+cid+'/update',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({engineer:eng,date:dt})})
  .then(r=>r.json()).then(d=>{
    if(d.ok){
      // Success animation on button before closing modal
      b.textContent='✅ تم';b.classList.add('did-save');
      setTimeout(()=>{M.hide();toast('✅ تم الحفظ');setTimeout(()=>location.reload(),1600);},550);
    } else toast(d.error||'فشل',1);
  })
  .catch(()=>toast('خطأ في الاتصال',1))
  .finally(()=>{setTimeout(()=>{b.disabled=false;b.textContent='💾 حفظ';b.classList.remove('did-save');},600);});
}
let _toastTimer=null;
function toast(m,err=0){
  const t=document.getElementById('toast');
  if(_toastTimer)clearTimeout(_toastTimer);
  t.textContent=m;
  t.className='tmsg'+(err?' err':'');
  void t.offsetWidth;
  t.classList.add('on');
  _toastTimer=setTimeout(()=>{
    t.style.transform='translateY(8px) scale(.95)';
    t.style.opacity='0';
    setTimeout(()=>{t.className='tmsg'+(err?' err':'');t.style.transform='';t.style.opacity='';},300);
  }, err?3500:2800);
}

// ── PENDING MODAL ─────────────────────────────────
const PM = new bootstrap.Modal(document.getElementById('pendingModal'));
function openPending(){ PM.show(); }

function approvePending(pid, eng) {
  requirePin(()=>{
    if (!confirm('اعتماد هذه المنافسة وتعيين المهندس: ' + (eng || '—') + '؟')) return;
    fetch('/api/pending/' + pid + '/approve', {method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'approve'})
    }).then(r=>r.json()).then(d=>{
      if(d.ok){
        const row=document.getElementById('prow-'+pid);
        if(row){row.style.opacity='.3';row.style.pointerEvents='none';}
        toast('✅ تم الاعتماد');
        setTimeout(()=>{PM.hide();location.reload();},1800);
      } else toast(d.error||'فشل',1);
    }).catch(()=>toast('خطأ في الاتصال',1));
  });
}

function rejectPending(pid) {
  requirePin(()=>{
    if (!confirm('رفض هذا الطلب؟')) return;
    fetch('/api/pending/' + pid + '/approve', {method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action:'reject'})
    }).then(r=>r.json()).then(d=>{
      if(d.ok){
        const row=document.getElementById('prow-'+pid);
        if(row){row.style.opacity='.3';row.style.pointerEvents='none';}
        toast('🗑️ تم الرفض');
        setTimeout(()=>{PM.hide();location.reload();},1800);
      } else toast(d.error||'فشل',1);
    }).catch(()=>toast('خطأ في الاتصال',1));
  });
}

// ── PIN GATE ──────────────────────────────────────────
const _PIN='1010';
let _pinCb=null;
function requirePin(fn){
  if(sessionStorage.getItem('pinOk')==='1'){fn();return;}
  _pinCb=fn;
  const m=document.getElementById('pinModal');
  m.style.display='flex';
  document.getElementById('pinInput').value='';
  document.getElementById('pinErr').textContent='';
  setTimeout(()=>document.getElementById('pinInput').focus(),80);
}
function _pinOk(){
  const v=document.getElementById('pinInput').value;
  if(v===_PIN){
    sessionStorage.setItem('pinOk','1');
    document.getElementById('pinModal').style.display='none';
    if(_pinCb){const f=_pinCb;_pinCb=null;f();}
  } else {
    document.getElementById('pinErr').textContent='كلمة المرور غير صحيحة ❌';
    document.getElementById('pinInput').value='';
    document.getElementById('pinInput').focus();
  }
}
function _pinCancel(){
  document.getElementById('pinModal').style.display='none';
  _pinCb=null;
}

// ─── ABOUT MENU (DASHBOARD) ───────────────────────────────
function toggleAboutD(e){
  e.stopPropagation();
  const d=document.getElementById('aboutDropD');
  d.style.display=d.style.display==='none'?'block':'none';
}
document.addEventListener('click',()=>{
  const d=document.getElementById('aboutDropD');
  if(d)d.style.display='none';
});
</script>
<!-- COPYRIGHT FOOTER -->
<div style="text-align:center;padding:1rem;color:rgba(255,255,255,.82);font-size:.68rem;font-family:'Tajawal',sans-serif;letter-spacing:.3px">
  Copyright 2026 &copy; Your Name &mdash; <a href="https://example.com" target="_blank" style="color:rgba(255,255,255,.6);text-decoration:none">example.com</a>
</div>

<!-- PIN GATE MODAL -->
<div id="pinModal" style="display:none;position:fixed;inset:0;z-index:9999;
  background:rgba(30,20,4,.82);align-items:center;justify-content:center">
  <div style="background:var(--card);border:2px solid var(--amber);border-radius:16px;
    padding:1.75rem 1.5rem;width:min(300px,88vw);text-align:center;
    box-shadow:0 12px 40px rgba(0,0,0,.4)">
    <div style="font-size:2rem;margin-bottom:.3rem">🔐</div>
    <div style="font-weight:800;font-size:1rem;margin-bottom:.2rem;color:var(--text)">مطلوب كلمة المرور</div>
    <div style="color:var(--muted);font-size:.77rem;margin-bottom:1rem">أدخل كلمة مرور التعديل للمتابعة</div>
    <input type="password" id="pinInput" maxlength="6"
      style="width:100%;text-align:center;font-size:1.5rem;letter-spacing:.4rem;
        padding:.55rem;border:1.5px solid var(--border);border-radius:8px;
        background:var(--bg);color:var(--text);outline:none;direction:ltr;
        transition:border-color .2s"
      placeholder="••••"
      onfocus="this.style.borderColor='var(--amber)'"
      onblur="this.style.borderColor='var(--border)'"
      onkeydown="if(event.key==='Enter')_pinOk()">
    <div id="pinErr" style="color:var(--red);font-size:.75rem;margin-top:.35rem;min-height:1rem"></div>
    <div style="display:flex;gap:.6rem;margin-top:.85rem">
      <button onclick="_pinOk()" style="flex:1;background:linear-gradient(135deg,#8a4800,#b06000);
        color:#fff4d8;border:none;border-radius:9px;padding:.55rem;cursor:pointer;
        font-family:'Tajawal',sans-serif;font-size:.95rem;font-weight:700">تأكيد</button>
      <button onclick="_pinCancel()" style="flex:1;background:transparent;color:var(--muted);
        border:1px solid var(--border);border-radius:9px;padding:.55rem;cursor:pointer;
        font-family:'Tajawal',sans-serif;font-size:.95rem">إلغاء</button>
    </div>
  </div>
</div>
</body></html>"""


RESULTS_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ co.short_ar }} — سجل النتائج</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css">
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{--bg:{{ co.theme_bg }};--card:{{ co.theme_card }};--hover:{{ co.theme_hover }};--head:{{ co.theme_head }};--border:#c8a028;--border2:#a07820;--text:#1e1404;--sub:#4a3810;--muted:#7a5e28;--amber:{{ co.theme_primary }};--amber-l:{{ co.theme_primary_l }};--amber-d:{{ co.theme_primary_d }};--blue:#1a5a9a;--green:#247848;--yellow:#a06800;--red:#b02828;--orange:#a84e1a}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:'Tajawal',sans-serif;font-size:14px;margin:0}
.topbar{background:linear-gradient(135deg,#5a2800 0%,#8a4800 55%,#b06000 100%);border-bottom:2px solid #6e3200;padding:.9rem 1.5rem;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:200;color:#fff4d8}
.brand{font-weight:900;font-size:1.15rem;display:flex;align-items:center;gap:.55rem;letter-spacing:-.2px;color:#fff4d8}
.tnav a{color:rgba(255,215,140,.8);text-decoration:none;font-size:.83rem;padding:.3rem .65rem;border-radius:7px;transition:.15s}
.tnav a:hover{background:rgba(255,255,255,.12);color:#fff}
.tnav a.hi{color:#ffd060}
.tnav{display:flex;align-items:center;gap:.5rem}
.stats-grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:1rem;margin-bottom:1rem}
@media(max-width:900px){.stats-grid{grid-template-columns:1fr 1fr}}
.scard{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1.5rem 1.75rem;position:relative;overflow:hidden;transition:.2s;cursor:default;text-align:right}
.scard:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(100,60,0,.2)}
.scard.t-green{border-color:rgba(90,171,120,.3)}
.scard.t-red{border-color:rgba(196,82,82,.3)}
.scard.t-yellow{border-color:rgba(200,144,64,.3)}
.scard.t-blue{border-color:rgba(126,179,232,.3)}
.stat-hero{padding:2.2rem 2rem}
.snum{font-size:3.5rem;font-weight:900;line-height:.9;letter-spacing:-2px;margin-top:.35rem}
.stat-hero .snum{font-size:clamp(4.2rem,5.5vw,6rem);letter-spacing:-3px}
.slbl{color:var(--sub);font-size:.78rem;letter-spacing:.4px;margin-bottom:.3rem;font-weight:600}
.panel{background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden}
.phead{background:var(--head);border-bottom:1px solid var(--border);border-right:3px solid var(--amber);padding:.75rem 1rem;font-weight:700;font-size:.84rem;display:flex;align-items:center;justify-content:space-between}
.pbody{padding:.85rem}
table{width:100%;border-collapse:collapse}
thead tr{background:var(--head);border-bottom:1px solid var(--border)}
thead th{padding:.55rem .8rem;font-weight:700;font-size:.82rem;color:var(--sub);text-transform:uppercase;letter-spacing:.3px;white-space:nowrap}
tbody tr{border-bottom:1px solid rgba(180,140,40,.25);transition:background .1s}
tbody tr:hover{background:var(--hover)}
tbody td{padding:.5rem .8rem;vertical-align:middle;font-size:.88rem}
.rbadge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:.74rem;font-weight:700}
.rb-won{background:rgba(63,185,80,.15);color:var(--green);border:1px solid rgba(63,185,80,.3)}
.rb-lost{background:rgba(248,81,73,.15);color:var(--red);border:1px solid rgba(248,81,73,.3)}
.rb-pend{background:rgba(227,179,65,.15);color:var(--yellow);border:1px solid rgba(227,179,65,.3)}
.rb-canc{background:rgba(139,148,158,.1);color:var(--muted);border:1px solid var(--border)}
.ecard{background:var(--hover);border:1px solid var(--border);border-radius:10px;padding:.7rem .85rem;margin-bottom:.55rem}
.eavatar{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.9rem;color:#fff;flex-shrink:0}
.ebar{height:5px;border-radius:3px;background:rgba(160,112,0,.18);margin-top:5px;overflow:hidden}
.ebar-fill{height:100%;width:100%;border-radius:3px;transform-origin:right center;transform:scaleX(0);transition:transform .75s cubic-bezier(.25,1,.5,1)}
.win-ring{width:100px;height:100px;margin:0 auto .5rem}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.scard{opacity:0}.panel{opacity:0}
tbody tr{transition:background .1s}
/* v5.7.4: rows are NEVER hidden by CSS — see dashboard note */
/* v5.7.3: same exemption — dynamic modal rows must never start invisible */
.modal tbody tr{opacity:1!important;transform:none!important;animation:none!important}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
/* ════ v5.8.0 MOBILE: results table -> cards ════ */
@media(max-width:768px){
  body{font-size:15px}
  .topbar{flex-wrap:wrap;padding:.55rem .8rem;gap:.35rem}
  .topbar a{min-height:40px;display:inline-flex;align-items:center;font-size:.78rem}
  .stats-grid{grid-template-columns:1fr 1fr!important;gap:.5rem}
  .scard{padding:1rem 1.1rem}
  .snum{font-size:2.4rem}
  .stat-hero .snum{font-size:clamp(2.6rem,9vw,3.6rem)}
  .rfilt{gap:.35rem}
  .rfbtn{min-height:38px;display:inline-flex;align-items:center;touch-action:manipulation}
  .rsrch{min-width:100%;max-width:100%}
  /* the main results table becomes stacked cards */
  #resTable table, .panel table.rmain{display:block}
  table thead{display:none}
  table tbody{display:block}
  table tbody tr.rrow{
    display:block;border:1px solid var(--border);border-radius:11px;
    padding:.7rem .85rem;margin-bottom:.6rem;background:var(--card);
    box-shadow:0 1px 4px rgba(120,70,0,.06)}
  table tbody tr.rrow td{
    display:flex;justify-content:space-between;align-items:center;gap:.6rem;
    padding:.28rem 0;border:none;text-align:right!important;font-size:.85rem}
  table tbody tr.rrow td[data-label]::before{
    content:attr(data-label);color:var(--muted);font-size:.72rem;font-weight:700;flex-shrink:0}
  /* first cell = title, full width, no label, bold */
  table tbody tr.rrow td:first-child{
    display:block;border-bottom:1px solid var(--border);padding-bottom:.45rem;margin-bottom:.25rem;
    font-weight:700;color:var(--amber-d);line-height:1.5}
  table tbody tr.rrow td .wchip{margin-right:.3rem}
  /* touch-friendly edit button */
  table tbody tr.rrow td[data-label="تعديل"] button{width:38px!important;height:38px!important}
}
/* clickable cards */
.scard.clickable{cursor:pointer}
.scard.clickable:hover{transform:translateY(-5px)!important;box-shadow:0 14px 36px rgba(100,60,0,.28)!important}
.scard.clickable:active{transform:translateY(-1px)!important}
.scard-hint{font-size:.65rem;color:var(--muted);margin-top:.55rem;opacity:.75;letter-spacing:.2px}
/* about dropdown */
.about-wrap{position:relative;display:inline-flex}
.about-btn{background:rgba(255,255,255,.1);border:1px solid rgba(255,200,100,.25);color:rgba(255,215,140,.85);padding:.3rem .75rem;border-radius:7px;font-family:'Tajawal',sans-serif;font-size:.82rem;cursor:pointer;transition:.15s;white-space:nowrap}
.about-btn:hover{background:rgba(255,255,255,.18);color:#fff}
.about-drop{position:absolute;top:calc(100% + 10px);left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#3d1800 0%,#6e3200 60%,#8a4800 100%);border:1px solid rgba(255,200,80,.25);border-radius:14px;padding:1.4rem 1.6rem;min-width:260px;z-index:9998;box-shadow:0 12px 40px rgba(0,0,0,.5);animation:fadeIn .18s ease;text-align:center}
.about-drop::before{content:'';position:absolute;top:-7px;left:50%;transform:translateX(-50%);border:7px solid transparent;border-bottom:7px solid rgba(255,200,80,.25);border-top:none}
.about-heart{font-size:2.2rem;margin-bottom:.5rem;line-height:1}
.about-line{color:rgba(255,220,150,.85);font-size:.88rem;line-height:1.7}
.about-name{color:#ffd060;font-weight:800;font-size:1rem;margin-top:.55rem;letter-spacing:.3px}

/* ── Real-time indicator ───────────────────────────────── */
.rt-indicator{display:inline-flex;align-items:center;gap:.35rem;font-size:.72rem;
  color:rgba(255,215,140,.7);padding:.25rem .6rem;border-radius:12px;
  background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1)}
#rt-dot{display:inline-block;width:8px;height:8px;border-radius:50%;
  background:#e34949;transition:.4s}
/* ── Toast notification ────────────────────────────────── */
#rt-toast{position:fixed;bottom:1.4rem;left:50%;
  transform:translateX(-50%) translateY(80px);
  background:#1e1404;color:#ffd88a;padding:.65rem 1.3rem;border-radius:10px;
  font-size:.85rem;font-weight:600;border:1px solid rgba(200,160,40,.35);
  z-index:9999;pointer-events:none;white-space:nowrap;max-width:90vw;
  transition:transform .35s cubic-bezier(.22,1,.36,1),opacity .35s;opacity:0}
#rt-toast.rt-toast-show{transform:translateX(-50%) translateY(0);opacity:1}
#rt-toast.rt-warn{border-color:rgba(255,80,80,.4);color:#ff9a9a}
</style>
</head>
<body>

<div class="topbar">
  <div class="brand">
    <div style="background:#fff;border-radius:9px;padding:5px 12px;display:inline-flex;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,.22);flex-shrink:0">
      <img src="{{ logo_uri }}" alt="{{ co.name_ar }}" style="height:44px;width:auto;display:block">
    </div>
    <span>{{ co.system_title }}</span>
    <span class="brand-sub">سجل النتائج</span>
  </div>
  <div class="tnav">
    <a href="/" class="hi">← اللوحة الرئيسية</a>
    <a href="/engineer-view">👷 المهندسين</a>
    <a href="/owners">🏢 الجهات</a>
    <div class="about-wrap">
      <button class="about-btn" onclick="toggleAbout(event)">عن ▾</button>
      <div id="aboutDrop" class="about-drop" style="display:none">
        <div class="about-heart">❤️</div>
        <div class="about-line">صُنع بكل حب</div>
        <div class="about-line">من فريق العروض الفنية</div>
        <div class="about-line">لشركة {{ co.short_ar }}</div>
        <div class="about-name">م. يوسف سليم</div>
      </div>
    </div>
    <a href="/logout">
    <span class="rt-indicator"><span id="rt-dot"></span><span id="rt-lbl">...</span></span>خروج ↩</a>
  </div>
</div>

<div style="padding:1.25rem 1.5rem;max-width:1700px;margin:0 auto">

  <!-- STATS -->
  <div class="stats-grid">
    <div class="scard {% if win_rate>=60 %}t-green{% elif win_rate>=30 %}t-yellow{% else %}t-red{% endif %} stat-hero clickable" onclick="showList('won')" title="اضغط لعرض قائمة الفوز">
      <div class="slbl">نسبة الفوز — من النتائج المعروفة</div>
      <div class="snum" style="color:{% if decided == 0 %}var(--muted){% elif win_rate>=60 %}var(--green){% elif win_rate>=30 %}var(--yellow){% else %}var(--red){% endif %}">{% if decided %}{{ win_rate }}%{% else %}—{% endif %}</div>
      <div class="scard-hint">{% if decided %}من {{ decided }} نتيجة معروفة ({{ won }} فوز / {{ lost }} خسارة){% else %}لا نتائج معروفة بعد — النتائج نادراً ما تُعلن{% endif %}</div>
    </div>
    <div class="scard t-green clickable" onclick="showList('won')" title="اضغط لعرض قائمة الفوز">
      <div class="slbl">فوز مؤكد</div>
      <div class="snum" style="color:var(--green)">{{ won }}</div>
      <div class="scard-hint">🏆 اضغط للتفاصيل</div>
    </div>
    <div class="scard t-yellow clickable" onclick="showList('submitted')" title="اضغط لعرض قائمة العروض المقدمة">
      <div class="slbl">قدّمنا عرضاً</div>
      <div class="snum" style="color:var(--yellow)">{{ submits }}</div>
      <div class="scard-hint">📤 اضغط للتفاصيل</div>
    </div>
    <div class="scard t-blue clickable" onclick="showList('all')" title="اضغط لعرض جميع المسجلات">
      <div class="slbl">إجمالي المسجّلة</div>
      <div class="snum" style="color:var(--blue)">{{ total }}</div>
      <div class="scard-hint">📋 اضغط للتفاصيل</div>
    </div>
  </div>

  <style>
  .qbtn{border-radius:7px;padding:.25rem .6rem;font-size:.7rem;font-weight:800;cursor:pointer;
    font-family:'Tajawal',sans-serif;transition:.15s;border:1px solid}
  .qwin{background:rgba(36,120,72,.1);color:var(--green);border-color:rgba(36,120,72,.35)}
  .qwin:hover{background:rgba(36,120,72,.22)}
  .qlose{background:rgba(200,40,40,.08);color:var(--red);border-color:rgba(200,40,40,.3)}
  .qlose:hover{background:rgba(200,40,40,.18)}
  .qunk{background:rgba(120,110,90,.08);color:var(--muted);border-color:rgba(120,110,90,.3)}
  .qunk:hover{background:rgba(120,110,90,.18)}
  .rb-unk{background:rgba(120,110,90,.12);color:var(--muted);border:1px solid rgba(120,110,90,.28)}
  .rfilt{display:flex;gap:.45rem;align-items:center;flex-wrap:wrap;margin-bottom:.9rem}
  .rfbtn{border-radius:999px;padding:.3rem .85rem;font-size:.75rem;font-weight:700;cursor:pointer;
    font-family:'Tajawal',sans-serif;border:1px solid var(--border);background:var(--card);color:var(--sub);transition:.15s}
  .rfbtn:hover{background:var(--hover)}
  .rfbtn.on{background:rgba(184,106,0,.15);color:var(--amber);border-color:rgba(184,106,0,.45)}
  .rsrch{flex:1;min-width:180px;max-width:320px;border:1px solid var(--border);border-radius:999px;
    padding:.32rem .9rem;font-size:.78rem;font-family:'Tajawal',sans-serif;background:var(--card);color:inherit;outline:none}
  .wchip{font-size:.6rem;font-weight:700;margin-top:2px;display:block}
  </style>

  {% if followup %}
  <div class="panel mb-3" style="border-color:rgba(200,40,40,.35)">
    <div class="phead" style="background:rgba(200,40,40,.07)">
      <span>⏰ متابعة مطلوبة — عروض بلا نتيجة منذ 3 أسابيع فأكثر</span>
      <span style="color:var(--red);font-weight:800;font-size:.85rem">{{ followup|length }}</span>
    </div>
    <div class="pbody" style="padding:.5rem .95rem">
      {% for f in followup %}
      <div style="display:flex;align-items:center;gap:.6rem;padding:.42rem .1rem;
                  {% if not loop.last %}border-bottom:1px dashed var(--border);{% endif %}flex-wrap:wrap">
        <span style="background:rgba(200,40,40,.1);color:var(--red);border:1px solid rgba(200,40,40,.3);
                     border-radius:6px;padding:.14rem .5rem;font-size:.68rem;font-weight:800;white-space:nowrap">
          ⏳ {{ f.waiting_days }} يوم</span>
        <span style="flex:1;font-size:.8rem;font-weight:600;min-width:220px">{{ f.title }}</span>
        <span style="color:var(--muted);font-size:.72rem">{{ (f.owner or '')[:26] }}</span>
        <span style="display:flex;gap:.35rem">
          <button class="qbtn qwin"  onclick="quickRes({{ f.rec_id }},'won')">🏆 فزنا</button>
          <button class="qbtn qlose" onclick="quickRes({{ f.rec_id }},'lost')">❌ خسرنا</button>
          <button class="qbtn qunk"  onclick="quickRes({{ f.rec_id }},'unknown')" title="الجهة لم تعلن النتيجة — أقفل المتابعة">⚪ لم تُعلن</button>
        </span>
      </div>
      {% endfor %}
      <div style="font-size:.7rem;color:var(--muted);padding-top:.45rem">
        💡 النتائج لا تُعلن دائماً في السوق — إن عرفت سجّلها، وإن تعذر فاضغط «لم تُعلن» لإقفال المتابعة بلا إزعاج. النسب تُحسب من المعروف فقط</div>
    </div>
  </div>
  {% endif %}

  <div class="rfilt">
    <button class="rfbtn on" id="rf-all"     onclick="resFilt('all')">الكل ({{ rows|length }})</button>
    <button class="rfbtn" id="rf-pending" onclick="resFilt('pending')">⏳ معلقة ({{ pending_res }})</button>
    <button class="rfbtn" id="rf-won"     onclick="resFilt('won')">🏆 فوز ({{ won }})</button>
    <button class="rfbtn" id="rf-lost"    onclick="resFilt('lost')">❌ خسارة ({{ lost }})</button>
    <button class="rfbtn" id="rf-unknown" onclick="resFilt('unknown')">⚪ لم تُعلن ({{ unknown }})</button>
    <button class="rfbtn" id="rf-nosub"   onclick="resFilt('nosub')">لم نقدّم</button>
    <input class="rsrch" id="rSrch" placeholder="🔍 بحث بالاسم أو الجهة..." oninput="resFilt(null)">
  </div>

  <div class="row g-3">

    <!-- ENGINEER WIN RATES + CHART -->
    <div class="col-12 col-md-4">
      <div class="panel mb-3">
        <div class="phead">📊 نسبة فوز — دونات</div>
        <div class="pbody" style="padding:.75rem 1rem">
          <canvas id="winChart" style="max-height:190px"></canvas>
        </div>
      </div>
      <div class="panel mb-3">
        <div class="phead">📈 الخط الزمني — آخر 8 أشهر</div>
        <div class="pbody" style="padding:.7rem .9rem;height:185px">
          <canvas id="tlChart"></canvas>
        </div>
      </div>
      <div class="panel">
        <div class="phead">👷 نسبة فوز كل مهندس</div>
        <div class="pbody">
          {% set acolors = ['#388bfd','#a371f7','#d29922','#f85149','#3fb950','#e3b341','#58a6ff','#ffa657'] %}
          {% if eng_stats %}
          {% for name, s in eng_stats.items()|sort(attribute='1.rate',reverse=True) %}
          {% set ai = loop.index0 % 8 %}
          <div class="ecard">
            <div style="display:flex;align-items:center;gap:.65rem">
              <div class="eavatar" style="background:{{ acolors[ai] }}">{{ name[2:3] if name.startswith('ال') else name[:1] }}</div>
              <div style="flex:1;min-width:0">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                  <span style="font-weight:600;font-size:.87rem">{{ name }}</span>
                  <span style="color:var(--sub);font-size:.82rem;font-weight:600"
                        title="فوز/معروفة النتيجة — وإجمالي المقدمة {{ s.submitted }}">{{ s.won }}/{{ s.decided }}{% if s.submitted > s.decided %} <span style="color:var(--muted);font-size:.7rem">({{ s.submitted }})</span>{% endif %}</span>
                </div>
                <div class="ebar">
                  <div class="ebar-fill" data-w="{{ s.rate }}" style="background:{{ s.hex }}"></div>
                </div>
              </div>
              <span style="font-size:.82rem;font-weight:700;color:{{ s.hex }};min-width:34px;text-align:left">{{ s.rate }}%</span>
            </div>
          </div>
          {% endfor %}
          {% else %}
          <p style="color:var(--muted);text-align:center;padding:1rem">لا توجد بيانات بعد</p>
          {% endif %}
        </div>
      </div>

      {% if owner_stats %}
      <div class="panel" style="margin-top:1rem">
        <div class="phead">🏢 نسبة الفوز حسب الجهة</div>
        <div class="pbody">
          {% for o in owner_stats %}
          <div class="owner-row">
            <span class="owner-name" title="{{ o.name }}">{{ o.name[:26] }}{% if o.name|length > 26 %}…{% endif %}</span>
            <span style="color:var(--sub);font-size:.72rem;font-weight:700;white-space:nowrap"
                  title="فوز/معروفة النتيجة — وإجمالي المقدمة {{ o.submitted }}">{{ o.won }}/{{ o.decided }}{% if o.submitted > o.decided %} <span style="color:var(--muted);font-size:.62rem">({{ o.submitted }})</span>{% endif %}</span>
            <span style="min-width:38px;text-align:left;font-size:.78rem;font-weight:800;
              color:{% if o.rate >= 50 %}var(--green){% elif o.rate > 0 %}var(--yellow){% else %}var(--muted){% endif %}">{{ o.rate }}%</span>
          </div>
          {% endfor %}
        </div>
      </div>
      {% endif %}
    </div>

    <!-- RESULTS TABLE -->
    <div class="col-12 col-md-8">
      <div class="panel">
        <div class="phead">
          <span>📋 آخر النتائج المسجّلة</span>
          <span style="color:var(--muted);font-size:.72rem">{{ rows|length }} سجل
            <span style="font-size:.6rem;opacity:.65;background:rgba(138,72,0,.1);border:1px solid var(--border);
                  border-radius:5px;padding:1px 6px;margin-right:.45rem" title="إصدار الصفحة التي يعرضها متصفحك الآن">v{{ version }}</span>
          </span>
        </div>
        <div style="overflow-x:auto">
          <table class="rmain">
            <thead>
              <tr>
                <th>المنافسة</th>
                <th style="width:95px;text-align:center">النتيجة</th>
                <th style="width:98px;text-align:center">تاريخ التقديم</th>
                <th style="width:115px">سعرنا</th>
                <th style="width:115px">سعر الفائز</th>
                <th style="width:80px">المهندس</th>
                <th style="width:50px;text-align:center">تعديل</th>
              </tr>
            </thead>
            <tbody>
              {% for r in rows %}
              {% if r.result=='won' %}{% set bc='rb-won' %}{% set ic='🏆 فوز' %}
              {% elif r.result=='lost' %}{% set bc='rb-lost' %}{% set ic='❌ خسارة' %}
              {% elif r.result=='cancelled' %}{% set bc='rb-canc' %}{% set ic='🚫 ملغي' %}
              {% elif r.result=='unknown' %}{% set bc='rb-unk' %}{% set ic='⚪ لم تُعلن' %}
              {% else %}{% set bc='rb-pend' %}{% set ic='⏳ معلق' %}{% endif %}
              <tr class="rrow" data-res="{{ r.result or 'pending' }}" data-sub="{{ 1 if r.did_submit else 0 }}"
                  data-t="{{ ((r.title or '') ~ ' ' ~ (r.owner or ''))|e }}">
                <td>
                  <span title="{{ (r.title or '')|e }}" style="line-height:1.5;word-break:break-word">{{ r.title or '—' }}</span>
                  {% if not r.did_submit %}<span style="background:rgba(139,148,158,.1);color:var(--muted);border-radius:4px;padding:1px 5px;font-size:.65rem;margin-right:3px">لم نقدّم</span>{% endif %}
                </td>
                <td data-label="النتيجة" style="text-align:center"><span class="rbadge {{ bc }}">{{ ic }}</span>
                  {% if r.waiting_days is not none and r.waiting_days >= 21 %}
                  <span class="wchip" style="color:var(--red)">منذ {{ r.waiting_days }} يوم ⚠️</span>
                  {% elif r.waiting_days is not none and r.waiting_days > 0 %}
                  <span class="wchip" style="color:var(--muted)">منذ {{ r.waiting_days }} يوم</span>
                  {% endif %}
                </td>
                <td data-label="تاريخ التقديم" style="text-align:center;font-size:.78rem;color:var(--sub)">
                  {% if r.submission_date and r.submission_date != 'N/A' %}
                    {{ r.submission_date[:10] }}
                  {% else %}—{% endif %}
                </td>
                <td data-label="سعرنا" style="color:var(--muted)">{% if r.our_price %}{{ "{:,.0f}".format(r.our_price) }} ﷼{% else %}—{% endif %}</td>
                <td data-label="سعر الفائز" style="color:var(--muted)">{% if r.winning_price %}{{ "{:,.0f}".format(r.winning_price) }} ﷼{% else %}—{% endif %}
                  {% if r.price_gap is not none %}
                  <span class="wchip" style="color:{% if r.price_gap > 0 %}var(--red){% else %}var(--green){% endif %}"
                        title="الفرق بين سعرنا وسعر الفائز">فرقنا {{ '%+.1f'|format(r.price_gap) }}%</span>
                  {% endif %}
                </td>
                <td data-label="المهندس">{% if r.assigned_engineer %}<span style="color:var(--amber-l);font-size:.79rem">{{ r.assigned_engineer }}</span>{% else %}—{% endif %}</td>
                <td data-label="تعديل" style="text-align:center">
                  {% if r.master_id %}
                  <button data-t="{{ (r.title or '')|e }}" onclick="openResEdit({{ r.master_id }}, this.dataset.t)"
                    style="width:28px;height:28px;border:1px solid var(--border);background:transparent;
                           color:var(--muted);border-radius:7px;cursor:pointer;
                           display:inline-flex;align-items:center;justify-content:center;
                           font-size:.78rem;transition:.15s"
                    onmouseover="this.style.background='rgba(88,166,255,.1)';this.style.color='var(--blue)';this.style.borderColor='rgba(88,166,255,.4)'"
                    onmouseout="this.style.background='transparent';this.style.color='var(--muted)';this.style.borderColor='var(--border)'"
                    title="تعديل النتيجة">✏️</button>
                  {% else %}—{% endif %}
                </td>
              </tr>
              {% else %}
              <tr><td colspan="7" style="text-align:center;color:var(--muted);padding:2.5rem">
                لم يتم تسجيل أي نتائج بعد<br>
                <span style="font-size:.8rem">استخدم زر 📝 في اللوحة الرئيسية لتسجيل أول نتيجة</span>
              </td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- RESULT EDIT MODAL -->
<div class="modal fade" id="reModal" tabindex="-1" role="dialog" aria-modal="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content" style="background:var(--card);border:1px solid var(--border);color:var(--text)">
      <div class="modal-header" style="background:var(--head);border-bottom:1px solid var(--border)">
        <h6 class="modal-title" style="font-size:.95rem">✏️ تعديل نتيجة المنافسة</h6>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="إغلاق"></button>
      </div>
      <div class="modal-body">
        <p id="reTitle" style="color:var(--muted);font-size:.82rem;margin-bottom:1rem;padding:.5rem .75rem;background:var(--hover);border-radius:7px;border:1px solid var(--border)"></p>
        <div class="mb-3">
          <label style="color:var(--muted);font-size:.81rem;display:block;margin-bottom:.3rem">هل قدّمنا عرضاً؟</label>
          <div style="display:flex;gap:.5rem">
            <button id="reBtnYes" onclick="reSetSubmit(true)" type="button" class="btn btn-sm btn-outline-success" style="flex:1">✅ نعم، قدّمنا</button>
            <button id="reBtnNo"  onclick="reSetSubmit(false)" type="button" class="btn btn-sm btn-outline-secondary" style="flex:1">❌ لم نقدّم</button>
          </div>
        </div>
        <div class="mb-3">
          <label style="color:var(--muted);font-size:.81rem;display:block;margin-bottom:.3rem">النتيجة</label>
          <div style="display:flex;gap:.4rem;flex-wrap:wrap">
            <button type="button" class="btn btn-sm btn-outline-success re-result-btn" onclick="reSetResult('won')">🏆 فزنا</button>
            <button type="button" class="btn btn-sm btn-outline-danger re-result-btn" onclick="reSetResult('lost')">❌ خسرنا</button>
            <button type="button" class="btn btn-sm btn-outline-warning re-result-btn" onclick="reSetResult('pending')">⏳ معلق</button>
            <button type="button" class="btn btn-sm btn-outline-secondary re-result-btn" onclick="reSetResult('unknown')">⚪ لم تُعلن</button>
            <button type="button" class="btn btn-sm btn-outline-secondary re-result-btn" onclick="reSetResult('cancelled')">🚫 ملغي</button>
          </div>
        </div>
        <div class="row g-2 mb-3">
          <div class="col-6">
            <label style="color:var(--muted);font-size:.81rem;display:block;margin-bottom:.3rem">سعرنا المقدَّم (ريال)</label>
            <input type="number" id="reOurPrice" style="width:100%;background:var(--bg);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:.45rem .75rem;font-family:'Tajawal',sans-serif" placeholder="0.00" step="0.01">
          </div>
          <div class="col-6">
            <label style="color:var(--muted);font-size:.81rem;display:block;margin-bottom:.3rem">سعر الفائز (اختياري)</label>
            <input type="number" id="reWinPrice" style="width:100%;background:var(--bg);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:.45rem .75rem;font-family:'Tajawal',sans-serif" placeholder="0.00" step="0.01">
          </div>
        </div>
        <div>
          <label style="color:var(--muted);font-size:.81rem;display:block;margin-bottom:.3rem">ملاحظات</label>
          <textarea id="reNotes" style="width:100%;background:var(--bg);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:.5rem .75rem;font-family:'Tajawal',sans-serif;resize:vertical" rows="2" placeholder="أي تفاصيل إضافية..."></textarea>
        </div>
      </div>
      <div class="modal-footer" style="border-top:1px solid var(--border)">
        <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">إلغاء</button>
        <button id="reSaveBtn" class="btn btn-success btn-sm px-4" onclick="reSave()">💾 حفظ</button>
      </div>
    </div>
  </div>
</div>
<div id="reToastWrap" style="position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%);z-index:9999">
  <div id="reToast" style="background:#e8f5ea;color:var(--green);border:1px solid rgba(36,120,72,.3);
    padding:.6rem 1.5rem;border-radius:10px;font-size:.87rem;box-shadow:0 6px 28px rgba(100,60,0,.15);
    opacity:0;transform:translateY(12px) scale(.96);
    transition:opacity .28s cubic-bezier(.22,1,.36,1),transform .32s cubic-bezier(.22,1,.36,1);
    pointer-events:none;white-space:nowrap"></div>
</div>

<!-- LIST MODAL -->
<div class="modal fade" id="listModal" tabindex="-1" role="dialog" aria-modal="true">
  <div class="modal-dialog modal-dialog-centered modal-lg">
    <div class="modal-content" style="background:var(--card);border:1px solid var(--border);color:var(--text);border-radius:14px;overflow:hidden">
      <div class="modal-header" style="background:var(--head);border-bottom:1px solid var(--border);padding:.85rem 1.1rem">
        <h6 class="modal-title" id="listModalTitle" style="font-size:.95rem;font-weight:800;margin:0">📋 القائمة</h6>
        <button type="button" class="btn-close" data-bs-dismiss="modal" style="filter:invert(.4) sepia(1) saturate(2) hue-rotate(0deg)" aria-label="إغلاق"></button>
      </div>
      <div class="modal-body p-0">
        <div style="overflow-x:auto;max-height:58vh">
          <table style="width:100%;border-collapse:collapse">
            <thead>
              <tr style="background:var(--head);position:sticky;top:0;z-index:1;border-bottom:1px solid var(--border)">
                <th style="padding:.6rem .9rem;font-size:.78rem;color:var(--sub);font-weight:700;white-space:nowrap">#</th>
                <th style="padding:.6rem .9rem;font-size:.78rem;color:var(--sub);font-weight:700">المنافسة</th>
                <th style="padding:.6rem .9rem;font-size:.78rem;color:var(--sub);font-weight:700;text-align:center;width:105px">النتيجة</th>
                <th style="padding:.6rem .9rem;font-size:.78rem;color:var(--sub);font-weight:700;text-align:center;width:95px">تاريخ التقديم</th>
                <th style="padding:.6rem .9rem;font-size:.78rem;color:var(--sub);font-weight:700;width:80px">المهندس</th>
              </tr>
            </thead>
            <tbody id="listModalBody"></tbody>
          </table>
        </div>
      </div>
      <div class="modal-footer" style="border-top:1px solid var(--border);padding:.65rem 1.1rem;display:flex;align-items:center;justify-content:space-between">
        <span id="listModalCount" style="color:var(--muted);font-size:.79rem;font-weight:600"></span>
        <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal" style="font-family:'Tajawal',sans-serif">إغلاق</button>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
function quickRes(rec, res){
  const label = res === 'won' ? 'فوز 🏆' : (res === 'lost' ? 'خسارة ❌' : 'لم تُعلن ⚪ (إقفال المتابعة)');
  if(!confirm('تأكيد تسجيل النتيجة: ' + label + '؟')) return;
  fetch('/api/result-rec/' + rec + '/quick', {method:'POST',
    headers:{'Content-Type':'application/json'}, body: JSON.stringify({result:res})})
    .then(r => r.json()).then(j => { if(j.ok) location.reload(); else alert('تعذر الحفظ'); })
    .catch(() => alert('خطأ في الاتصال'));
}
let _rf = 'all';
function resFilt(f){
  if(f !== null){ _rf = f;
    document.querySelectorAll('.rfbtn').forEach(b => b.classList.remove('on'));
    const btn = document.getElementById('rf-' + f); if(btn) btn.classList.add('on');
  }
  const q = (document.getElementById('rSrch').value || '').trim();
  document.querySelectorAll('tr.rrow').forEach(tr => {
    const res = tr.dataset.res, sub = tr.dataset.sub, txt = tr.dataset.t || '';
    let show = true;
    if(_rf === 'pending') show = (res === 'pending' && sub === '1');
    else if(_rf === 'won') show = (res === 'won');
    else if(_rf === 'lost') show = (res === 'lost');
    else if(_rf === 'unknown') show = (res === 'unknown');
    else if(_rf === 'nosub') show = (sub === '0');
    if(show && q) show = txt.includes(q);
    tr.style.display = show ? '' : 'none';
  });
}
new Chart(document.getElementById('tlChart').getContext('2d'), {
  type:'bar',
  data:{labels:{{ timeline.labels|tojson }}, datasets:[
    {label:'قدّمنا', data:{{ timeline.sub|tojson }},  backgroundColor:'rgba(184,106,0,.5)',  borderRadius:4},
    {label:'فوز',    data:{{ timeline.won|tojson }},  backgroundColor:'rgba(36,120,72,.85)', borderRadius:4},
    {label:'خسارة',  data:{{ timeline.lost|tojson }}, backgroundColor:'rgba(200,40,40,.75)', borderRadius:4}]},
  options:{maintainAspectRatio:false,
    plugins:{legend:{position:'bottom', labels:{font:{family:'Tajawal', size:10}, boxWidth:10}}},
    scales:{y:{beginAtZero:true, ticks:{precision:0, font:{size:10}}},
            x:{ticks:{font:{size:9}}}}}
});
new Chart(document.getElementById('winChart').getContext('2d'), {
  type:'doughnut',
  data:{
    labels:['فوز','خسارة','معلق/غير مقدّم'],
    datasets:[{
      data:[{{ won }}, {{ lost }}, Math.max(0, {{ total }}-{{ won }}-{{ lost }})],
      backgroundColor:['rgba(63,185,80,.65)','rgba(248,81,73,.65)','rgba(139,148,158,.25)'],
      borderColor:['#3fb950','#f85149','#484f58'],
      borderWidth:1.5,hoverOffset:6
    }]
  },
  options:{
    cutout:'70%',
    plugins:{
      legend:{position:'bottom',labels:{color:'#7a5e28',font:{family:'Tajawal',size:11},boxWidth:10,padding:12}},
      tooltip:{callbacks:{label:c=>` ${c.label}: ${c.raw}`}}
    }
  }
});

// ── RESULT EDIT (re-uses openResult flow via master_id) ─
let reCid=null, reDidSub=null, reResVal='pending';

function openResEdit(masterId, title){
  requirePin(()=>{
    reCid = masterId; reDidSub = null; reResVal = 'pending';
    document.getElementById('reTitle').textContent = title;
    ['reOurPrice','reWinPrice'].forEach(i=>document.getElementById(i).value='');
    document.getElementById('reNotes').value='';
    reSetSubmit(null);
    fetch('/api/result/'+masterId).then(r=>r.json()).then(d=>{
      if(d.existing){
        const ex=d.existing;
        reSetSubmit(ex.did_submit===1);
        reSetResult(ex.result||'pending');
        if(ex.our_price)document.getElementById('reOurPrice').value=ex.our_price;
        if(ex.winning_price)document.getElementById('reWinPrice').value=ex.winning_price;
        if(ex.notes)document.getElementById('reNotes').value=ex.notes;
      }
      new bootstrap.Modal(document.getElementById('reModal')).show();
    }).catch(()=>new bootstrap.Modal(document.getElementById('reModal')).show());
  });
}
function reSetSubmit(v){
  reDidSub=v;
  document.getElementById('reBtnYes').className='btn btn-sm '+(v?'btn-success':'btn-outline-success')+' flex-fill';
  document.getElementById('reBtnNo').className='btn btn-sm '+(!v?'btn-secondary':'btn-outline-secondary')+' flex-fill';
}
function reSetResult(v){
  reResVal=v;
  document.querySelectorAll('.re-result-btn').forEach(b=>b.classList.toggle('active',b.getAttribute('onclick').includes("'"+v+"'")));
}
function reSave(){
  if(reDidSub===null){reToast('حدد هل قدّمنا أم لا',1);return;}
  const b=document.getElementById('reSaveBtn');b.disabled=true;b.textContent='⏳';
  fetch('/api/result/'+reCid+'/save',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({did_submit:reDidSub,result:reResVal,
      our_price:document.getElementById('reOurPrice').value,
      win_price:document.getElementById('reWinPrice').value,
      notes:document.getElementById('reNotes').value})
  }).then(r=>r.json()).then(d=>{
    if(d.ok){
      bootstrap.Modal.getInstance(document.getElementById('reModal')).hide();
      reToast('✅ تم الحفظ');
      setTimeout(()=>location.reload(),1600);
    } else reToast(d.error||'فشل',1);
  }).catch(()=>reToast('خطأ في الاتصال',1))
  .finally(()=>{b.disabled=false;b.textContent='💾 حفظ';});
}
let _reTT;
function reToast(m,err=0){
  const t=document.getElementById('reToast');
  if(!t)return;
  if(_reTT)clearTimeout(_reTT);
  t.textContent=m;t.className='tmsg'+(err?' err':'');
  void t.offsetWidth; t.classList.add('on');
  _reTT=setTimeout(()=>{t.style.opacity='0';setTimeout(()=>{t.className='tmsg'+(err?' err':'');t.style.opacity='';},300);},err?3500:2800);
}

// ── ROWS DATA (all records for list modals) ──────────
const ALL_ROWS = {{ rows | tojson }};

// ── SHOW LIST MODAL ───────────────────────────────────
function showList(filter){
 try {
  const titles = {
    all:       '📋 إجمالي المسجّلة',
    submitted: '📤 قدّمنا عرضاً',
    won:       '🏆 فوز مؤكد'
  };
  let filtered;
  if      (filter === 'won')       filtered = ALL_ROWS.filter(r => r.result === 'won');
  else if (filter === 'submitted') filtered = ALL_ROWS.filter(r => r.did_submit);
  else                             filtered = ALL_ROWS;

  document.getElementById('listModalTitle').textContent = titles[filter] || '📋 القائمة';
  document.getElementById('listModalCount').textContent  = filtered.length + ' سجل';

  const rLabel = {won:'🏆 فوز', lost:'❌ خسارة', pending:'⏳ معلق', cancelled:'🚫 ملغي', unknown:'⚪ لم تُعلن'};
  const rColor = {won:'var(--green)', lost:'var(--red)', pending:'var(--yellow)', cancelled:'var(--muted)', unknown:'var(--muted)'};

  const tbody = document.getElementById('listModalBody');
  tbody.textContent = '';
  const mkTd = (styles) => { const td = document.createElement('td'); td.style.cssText = styles; return td; };
  if(!filtered.length){
    const tr = document.createElement('tr');
    tr.style.setProperty('opacity', '1', 'important');
    const td = mkTd('text-align:center;padding:2.5rem;color:#9a8a60;font-size:.88rem');
    td.colSpan = 5; td.textContent = 'لا توجد سجلات في هذه الفئة';
    tr.appendChild(td); tbody.appendChild(tr);
  } else {
    filtered.forEach((r, i) => {
      try {
        const res = r.result || 'pending';
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid rgba(180,140,40,.2)';
        tr.style.setProperty('opacity', '1', 'important');
        tr.style.setProperty('transform', 'none', 'important');
        const td1 = mkTd('padding:.48rem .9rem;color:#9a8a60;font-size:.74rem;vertical-align:middle');
        td1.textContent = String(i + 1);
        const td2 = mkTd('padding:.48rem .9rem;font-size:.84rem;vertical-align:middle;color:#1e1404;line-height:1.5;word-break:break-word');
        td2.textContent = r.title || '—';
        if(!r.did_submit){
          const ns = document.createElement('span');
          ns.style.cssText = 'background:rgba(139,148,158,.12);color:#9a8a60;border-radius:4px;padding:1px 5px;font-size:.62rem;margin-right:5px;white-space:nowrap';
          ns.textContent = 'لم نقدّم';
          td2.appendChild(ns);
        }
        const td3 = mkTd('padding:.48rem .9rem;text-align:center;vertical-align:middle');
        const chip = document.createElement('span');
        const colMap = {won:'#247848', lost:'#c22828', pending:'#8a6400', cancelled:'#9a8a60', unknown:'#8a8070'};
        const c = colMap[res] || '#9a8a60';
        chip.style.cssText = 'display:inline-block;padding:2px 9px;border-radius:12px;font-size:.71rem;font-weight:700;white-space:nowrap;color:' + c + ';background:' + c + '22;border:1px solid ' + c + '44';
        chip.textContent = rLabel[res] || res;
        td3.appendChild(chip);
        const td4 = mkTd('padding:.48rem .9rem;text-align:center;font-size:.76rem;color:#6a5a30;vertical-align:middle');
        td4.textContent = (r.submission_date && r.submission_date !== 'N/A') ? String(r.submission_date).substring(0,10) : '—';
        const td5 = mkTd('padding:.48rem .9rem;font-size:.8rem;color:#b86a00;vertical-align:middle');
        td5.textContent = r.assigned_engineer || '—';
        tr.append(td1, td2, td3, td4, td5);
        tbody.appendChild(tr);
      } catch(rowErr) {
        const tr = document.createElement('tr');
        tr.style.setProperty('opacity', '1', 'important');
        const td = mkTd('color:#c22828;padding:.4rem .9rem;font-size:.7rem');
        td.colSpan = 5; td.textContent = 'تعذر عرض سجل: ' + rowErr.message;
        tr.appendChild(td); tbody.appendChild(tr);
      }
    });
  }
  new bootstrap.Modal(document.getElementById('listModal')).show();
 } catch(e) {
   console.error('showList failed:', e);
   try {
     const tb = document.getElementById('listModalBody');
     if (tb) {
       tb.textContent = '';
       const tr = document.createElement('tr');
       const td = document.createElement('td');
       td.colSpan = 5;
       td.style.cssText = 'color:#c22828;padding:1.2rem;font-size:.75rem;text-align:right;direction:rtl;line-height:1.8';
       td.textContent = '🐞 خطأ في العرض داخل متصفحك: [' + (e.name||'Error') + '] ' + e.message
                      + ' — التقط صورة لهذه الرسالة وأرسلها للدعم. المتصفح: '
                      + navigator.userAgent.substring(0, 90);
       tr.appendChild(td); tb.appendChild(tr);
     }
     new bootstrap.Modal(document.getElementById('listModal')).show();
   } catch(_) {}
 }
}

// ── ABOUT MENU ────────────────────────────────────────
function toggleAbout(e){
  e.stopPropagation();
  const d = document.getElementById('aboutDrop');
  d.style.display = d.style.display === 'none' ? 'block' : 'none';
}
document.addEventListener('click', () => {
  const d = document.getElementById('aboutDrop');
  if(d) d.style.display = 'none';
});

// ── Results page entrance animations ──────────────────
(function(){
  const E4 = t => 1 - Math.pow(1-t, 4);

  document.querySelectorAll('.scard').forEach((c, i) => {
    c.style.animation = `fadeUp .5s cubic-bezier(.25,1,.5,1) ${40+i*90}ms both`;
    const num = c.querySelector('.snum');
    if (num) {
      const raw = num.textContent.trim();
      const target = parseInt(raw, 10) || 0;
      if (target > 0) {
        num.textContent = '0';
        const s = performance.now(), dur = 850;
        const tick = n => {
          const p = Math.min((n-s)/dur, 1);
          num.textContent = Math.round(target * E4(p)) + (raw.endsWith('%') ? '%' : '');
          if (p < 1) requestAnimationFrame(tick);
          else num.textContent = raw;
        };
        setTimeout(() => requestAnimationFrame(tick), 40 + i*90 + 20);
      }
    }
  });

  document.querySelectorAll('.panel').forEach((p, i) => {
    p.style.animation = `fadeIn .42s ease-out ${300+i*70}ms both`;
  });

  document.querySelectorAll('tbody tr').forEach((tr, i) => {
    const d = 330 + Math.min(i, 15) * 25;
    tr.style.opacity = '0';
    tr.style.transform = 'translateX(6px)';
    setTimeout(() => {
      tr.style.transition = 'opacity .28s ease, transform .35s cubic-bezier(.25,1,.5,1)';
      tr.style.opacity = '1';
      tr.style.transform = 'translateX(0)';
      setTimeout(() => { tr.style.transition = 'background .1s'; }, 400);
    }, d);
  });

  document.querySelectorAll('.ebar-fill[data-w]').forEach((el, i) => {
    setTimeout(() => {
      el.style.transform = 'scaleX(' + (parseInt(el.dataset.w, 10) / 100) + ')';
    }, 480 + i * 80);
  });
})();

// ── PIN GATE ──────────────────────────────────────────
const _PIN='1010';
let _pinCb=null;
function requirePin(fn){
  if(sessionStorage.getItem('pinOk')==='1'){fn();return;}
  _pinCb=fn;
  const m=document.getElementById('pinModal');
  m.style.display='flex';
  document.getElementById('pinInput').value='';
  document.getElementById('pinErr').textContent='';
  setTimeout(()=>document.getElementById('pinInput').focus(),80);
}
function _pinOk(){
  const v=document.getElementById('pinInput').value;
  if(v===_PIN){
    sessionStorage.setItem('pinOk','1');
    document.getElementById('pinModal').style.display='none';
    if(_pinCb){const f=_pinCb;_pinCb=null;f();}
  } else {
    document.getElementById('pinErr').textContent='كلمة المرور غير صحيحة ❌';
    document.getElementById('pinInput').value='';
    document.getElementById('pinInput').focus();
  }
}
function _pinCancel(){
  document.getElementById('pinModal').style.display='none';
  _pinCb=null;
}

</script>
<!-- COPYRIGHT FOOTER -->
<div style="text-align:center;padding:1rem;color:rgba(255,255,255,.82);font-size:.68rem;font-family:'Tajawal',sans-serif;letter-spacing:.3px">
  Copyright 2026 &copy; Your Name &mdash; <a href="https://example.com" target="_blank" style="color:rgba(255,255,255,.6);text-decoration:none">example.com</a>
</div>

<!-- PIN GATE MODAL -->
<div id="pinModal" style="display:none;position:fixed;inset:0;z-index:9999;
  background:rgba(30,20,4,.82);align-items:center;justify-content:center">
  <div style="background:var(--card);border:2px solid var(--amber);border-radius:16px;
    padding:1.75rem 1.5rem;width:min(300px,88vw);text-align:center;
    box-shadow:0 12px 40px rgba(0,0,0,.4)">
    <div style="font-size:2rem;margin-bottom:.3rem">🔐</div>
    <div style="font-weight:800;font-size:1rem;margin-bottom:.2rem;color:var(--text)">مطلوب كلمة المرور</div>
    <div style="color:var(--muted);font-size:.77rem;margin-bottom:1rem">أدخل كلمة مرور التعديل للمتابعة</div>
    <input type="password" id="pinInput" maxlength="6"
      style="width:100%;text-align:center;font-size:1.5rem;letter-spacing:.4rem;
        padding:.55rem;border:1.5px solid var(--border);border-radius:8px;
        background:var(--bg);color:var(--text);outline:none;direction:ltr;
        transition:border-color .2s"
      placeholder="••••"
      onfocus="this.style.borderColor='var(--amber)'"
      onblur="this.style.borderColor='var(--border)'"
      onkeydown="if(event.key==='Enter')_pinOk()">
    <div id="pinErr" style="color:var(--red);font-size:.75rem;margin-top:.35rem;min-height:1rem"></div>
    <div style="display:flex;gap:.6rem;margin-top:.85rem">
      <button onclick="_pinOk()" style="flex:1;background:linear-gradient(135deg,#8a4800,#b06000);
        color:#fff4d8;border:none;border-radius:9px;padding:.55rem;cursor:pointer;
        font-family:'Tajawal',sans-serif;font-size:.95rem;font-weight:700">تأكيد</button>
      <button onclick="_pinCancel()" style="flex:1;background:transparent;color:var(--muted);
        border:1px solid var(--border);border-radius:9px;padding:.55rem;cursor:pointer;
        font-family:'Tajawal',sans-serif;font-size:.95rem">إلغاء</button>
    </div>
  </div>
</div>
<div id="rt-toast"></div>

<script>
/* Real-time SSE Client */
(function(){
  var dot    = document.getElementById('rt-dot');
  var lbl    = document.getElementById('rt-lbl');
  var toastEl= document.getElementById('rt-toast');
  var toastT = null;

  function setStatus(ok){
    if(!dot||!lbl) return;
    dot.style.background = ok ? '#3fb850' : '#e34949';
    dot.style.boxShadow  = ok ? '0 0 0 3px rgba(63,184,80,.25)' : 'none';
    lbl.textContent      = ok ? 'مباشر' : 'غير متصل';
  }

  function showToast(msg, type){
    if(!toastEl) return;
    toastEl.textContent = msg;
    toastEl.className   = 'rt-toast-show rt-' + (type||'info');
    clearTimeout(toastT);
    toastT = setTimeout(function(){ toastEl.className=''; }, 5000);
  }

  function refreshStats(){
    fetch('/api/stats').then(function(r){ return r.json(); }).then(function(d){
      var el;
      if((el=document.getElementById('stat-active')))  el.textContent = d.active  || 0;
      if((el=document.getElementById('stat-pending'))) el.textContent = d.pending || 0;
      if((el=document.getElementById('stat-closed')))  el.textContent = d.closed  || 0;
    }).catch(function(){});
  }

  var LABELS = {
    'tender_approved': '✅ تمت الموافقة على مناقصة',
    'tender_rejected': '❌ تم رفض مناقصة',
    'new_tender':      '🆕 مناقصة جديدة اكتُشفت',
    'date_changed':    '📅 تغيير موعد مناقصة',
    'bot_paused':      '⏸️ البوت متوقف مؤقتاً',
    'bot_resumed':     '▶️ البوت يعمل مجدداً',
  };

  function connect(){
    var es = new EventSource('/api/stream');
    es.onopen = function(){ setStatus(true); };
    es.onmessage = function(e){
      try{
        var ev = JSON.parse(e.data);
        if(ev.type === 'ping' || ev.type === 'connected'){ setStatus(true); return; }
        var label = LABELS[ev.type] || ev.type;
        var detail = ev.data && ev.data.title ? ' — ' + ev.data.title.substring(0,30) : '';
        showToast(label + detail, ev.type.indexOf('reject') > -1 ? 'warn' : 'info');
        refreshStats();
      } catch(err){}
    };
    es.onerror = function(){
      setStatus(false);
      es.close();
      setTimeout(connect, 5000);
    };
  }

  connect();
  refreshStats();
  setInterval(refreshStats, 30000);
})();
</script>
</body></html>"""


ENGINEER_LOGIN_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>بوابة المهندس — {{ co.short_ar }}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1rem}
.card{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:2rem 1.5rem;width:100%;max-width:380px;text-align:center}
.logo{font-size:2.5rem;margin-bottom:.5rem}
h1{font-size:1.2rem;color:#ffc107;margin-bottom:.3rem}
.sub{color:#8b949e;font-size:.85rem;margin-bottom:1.5rem}
select,input{width:100%;padding:.75rem 1rem;border-radius:8px;border:1px solid #30363d;background:#0d1117;color:#e6edf3;font-size:1rem;margin-bottom:1rem;outline:none;text-align:right}
select:focus,input:focus{border-color:#ffc107}
.btn{width:100%;padding:.85rem;background:#ffc107;color:#000;border:none;border-radius:8px;font-size:1rem;font-weight:700;cursor:pointer;transition:.2s}
.btn:hover{background:#ffca2c}
.err{background:rgba(255,80,80,.15);border:1px solid rgba(255,80,80,.3);color:#f85149;padding:.6rem;border-radius:6px;margin-bottom:1rem;font-size:.9rem}
</style>
</head>
<body>
<div class="card">
  <div class="logo">👷</div>
  <h1>بوابة المهندس</h1>
  <div class="sub">{{ co.name_ar }}</div>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
{% if expired %}<div style="background:rgba(184,106,0,.12);border:1px solid rgba(184,106,0,.4);color:#8a4800;
  border-radius:9px;padding:.6rem .9rem;font-size:.85rem;font-weight:700;margin-bottom:.8rem;text-align:center">
  ⏳ انتهت الجلسة لعدم النشاط لأكثر من ساعتين — فضلاً سجّل الدخول من جديد</div>{% endif %}
  <form method="POST">
    <select name="name" required>
      <option value="">— اختر اسمك —</option>
      {% for eng in engineers %}<option value="{{ eng }}" {{ 'selected' if last_name==eng }}>{{ eng }}</option>{% endfor %}
    </select>
    <input type="password" name="pin" placeholder="كلمة المرور" required>
    <button class="btn" type="submit">دخول ←</button>
  </form>
</div>
</body></html>"""


ENGINEER_DASH_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>مناقصاتي — {{ eng_name }}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d1117;--card:#161b22;--border:#30363d;--muted:#8b949e;--gold:#ffc107;--red:#f85149;--green:#3fb950;--orange:#d29922}
body{background:var(--bg);color:#e6edf3;font-family:system-ui,sans-serif;padding:0 0 4rem}
.header{background:var(--card);border-bottom:1px solid var(--border);padding:.9rem 1rem;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10}
.header h1{font-size:1rem;color:var(--gold)}
.header .sub{font-size:.78rem;color:var(--muted)}
.logout{color:var(--muted);font-size:.8rem;text-decoration:none;padding:.3rem .6rem;border:1px solid var(--border);border-radius:6px}
.summary{display:flex;gap:.5rem;padding:.8rem 1rem;overflow-x:auto}
.stat{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:.6rem .9rem;text-align:center;min-width:80px;flex:1}
.stat .n{font-size:1.4rem;font-weight:700}
.stat .l{font-size:.72rem;color:var(--muted)}
.tenders{padding:.5rem 1rem;display:flex;flex-direction:column;gap:.75rem}
.tender-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1rem;position:relative;overflow:hidden}
.tender-card.urgent{border-color:var(--red)}
.tender-card.soon{border-color:var(--orange)}
.tender-card.done{opacity:.6}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:600;margin-bottom:.5rem}
.badge.red{background:rgba(248,81,73,.15);color:var(--red);border:1px solid rgba(248,81,73,.3)}
.badge.orange{background:rgba(210,153,34,.15);color:var(--orange);border:1px solid rgba(210,153,34,.3)}
.badge.green{background:rgba(63,185,80,.15);color:var(--green);border:1px solid rgba(63,185,80,.3)}
.badge.grey{background:rgba(139,148,158,.1);color:var(--muted);border:1px solid var(--border)}
.badge.gold{background:rgba(255,193,7,.15);color:var(--gold);border:1px solid rgba(255,193,7,.3)}
.title{font-size:.93rem;font-weight:600;line-height:1.4;margin-bottom:.3rem}
.meta{font-size:.78rem;color:var(--muted);margin-bottom:.8rem}
.actions{display:flex;gap:.5rem;flex-wrap:wrap}
.btn{padding:.5rem .9rem;border-radius:7px;border:1px solid var(--border);background:transparent;color:#e6edf3;cursor:pointer;font-size:.82rem;transition:.15s;flex:1;text-align:center}
.btn:hover{background:rgba(255,255,255,.06)}
.btn.active-submit{background:rgba(63,185,80,.2);border-color:var(--green);color:var(--green)}
.btn.active-no{background:rgba(248,81,73,.2);border-color:var(--red);color:var(--red)}
.btn.active-won{background:rgba(255,193,7,.2);border-color:var(--gold);color:var(--gold)}
.btn.active-lost{background:rgba(139,148,158,.15);border-color:var(--muted);color:var(--muted)}
.result-row{display:none;margin-top:.6rem;gap:.5rem}
.result-row.show{display:flex}
.empty{text-align:center;padding:3rem 1rem;color:var(--muted)}
.toast{position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%);background:#3fb950;color:#000;padding:.6rem 1.2rem;border-radius:20px;font-size:.85rem;font-weight:600;display:none;z-index:999}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>👷 {{ eng_name }}</h1>
    <div class="sub">{{ total }} منافسة مُعيّنة</div>
  </div>
  <a href="/engineer/logout" class="logout">خروج</a>
</div>

<div class="summary">
  <div class="stat"><div class="n" style="color:var(--red)">{{ urgent_count }}</div><div class="l">عاجل</div></div>
  <div class="stat"><div class="n" style="color:var(--orange)">{{ soon_count }}</div><div class="l">قريباً</div></div>
  <div class="stat"><div class="n" style="color:var(--green)">{{ submitted_count }}</div><div class="l">قدّمنا</div></div>
  <div class="stat"><div class="n" style="color:var(--gold)">{{ won_count }}</div><div class="l">فزنا</div></div>
</div>

<div class="tenders">
{% if not tenders %}
  <div class="empty">🎉 لا توجد منافسات مُعيّنة لك الآن</div>
{% endif %}
{% for t in tenders %}
<div class="tender-card {{ t.urgency_class }}" id="card-{{ t.id }}">
  {% if t.days_left is not none %}
    {% if t.days_left < 0 %}
      <span class="badge red">متأخر {{ (-t.days_left) }} يوم</span>
    {% elif t.days_left == 0 %}
      <span class="badge red">⚡ اليوم!</span>
    {% elif t.days_left == 1 %}
      <span class="badge orange">⚡ غداً</span>
    {% elif t.days_left <= 3 %}
      <span class="badge orange">{{ t.days_left }} أيام</span>
    {% elif t.days_left <= 7 %}
      <span class="badge gold">{{ t.days_left }} أيام</span>
    {% else %}
      <span class="badge grey">{{ t.days_left }} يوم</span>
    {% endif %}
  {% else %}
    <span class="badge grey">بدون تاريخ</span>
  {% endif %}
  {% if t.result == 'won' %}<span class="badge gold">🏆 فزنا</span>
  {% elif t.result == 'lost' %}<span class="badge grey">خسرنا</span>{% endif %}

  <div class="title">{{ t.title }}</div>
  <div class="meta">📅 {{ t.submission_date or '—' }} &nbsp;|&nbsp; {{ t.owner or '' }}</div>

  <div class="actions">
    <button class="btn {{ 'active-submit' if t.did_submit == 1 }}"
            onclick="setStatus({{ t.id }}, 'submit', this)"
            id="btn-submit-{{ t.id }}">✅ قدّمنا</button>
    <button class="btn {{ 'active-no' if t.did_submit == 0 and t.did_submit is not none }}"
            onclick="setStatus({{ t.id }}, 'no', this)"
            id="btn-no-{{ t.id }}">❌ لم نقدّم</button>
  </div>
  {% if t.did_submit == 1 %}
  <div class="result-row show" id="result-{{ t.id }}">
    <button class="btn {{ 'active-won' if t.result == 'won' }}"
            onclick="setStatus({{ t.id }}, 'won', this)"
            id="btn-won-{{ t.id }}">🏆 فزنا</button>
    <button class="btn {{ 'active-lost' if t.result == 'lost' }}"
            onclick="setStatus({{ t.id }}, 'lost', this)"
            id="btn-lost-{{ t.id }}">💔 خسرنا</button>
  </div>
  {% else %}
  <div class="result-row" id="result-{{ t.id }}">
    <button class="btn" onclick="setStatus({{ t.id }}, 'won', this)" id="btn-won-{{ t.id }}">🏆 فزنا</button>
    <button class="btn" onclick="setStatus({{ t.id }}, 'lost', this)" id="btn-lost-{{ t.id }}">💔 خسرنا</button>
  </div>
  {% endif %}
</div>
{% endfor %}
</div>
<div class="toast" id="toast"></div>
<script>
function toast(msg, ok=true){
  const t=document.getElementById('toast');
  t.textContent=msg; t.style.background=ok?'#3fb950':'#f85149';
  t.style.display='block'; setTimeout(()=>t.style.display='none',2200);
}
function setStatus(tid, action, btn){
  fetch('/api/eng/tender/'+tid+'/status',{
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({action})
  }).then(r=>r.json()).then(d=>{
    if(!d.ok){toast(d.error||'خطأ',false);return;}
    const card = document.getElementById('card-'+tid);
    const resRow = document.getElementById('result-'+tid);
    if(action==='submit'){
      document.getElementById('btn-submit-'+tid).className='btn active-submit';
      document.getElementById('btn-no-'+tid).className='btn';
      if(resRow)resRow.className='result-row show';
      toast('✅ تم تسجيل: قدّمنا');
    } else if(action==='no'){
      document.getElementById('btn-submit-'+tid).className='btn';
      document.getElementById('btn-no-'+tid).className='btn active-no';
      if(resRow)resRow.className='result-row';
      toast('تم: لم نقدّم');
    } else if(action==='won'){
      document.getElementById('btn-won-'+tid).className='btn active-won';
      document.getElementById('btn-lost-'+tid).className='btn';
      toast('🏆 تم تسجيل الفوز!');
    } else if(action==='lost'){
      document.getElementById('btn-won-'+tid).className='btn';
      document.getElementById('btn-lost-'+tid).className='btn active-lost';
      toast('تم تسجيل النتيجة');
    }
  }).catch(()=>toast('خطأ في الاتصال',false));
}
</script>
</body></html>"""


ENGINEER_VIEW_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>بوابة المهندسين — {{ co.short_ar }}</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#e6edf3;font-family:'Tajawal',system-ui,sans-serif;min-height:100vh}
:root{
  --bg:#0d1117;--card:#161b22;--border:#30363d;
  --amber:#ffc107;--amber-d:#7a5200;--head:#1c2128;
  --text:#e6edf3;--sub:#8b949e;--muted:#6e7681;
  --green:#3fb950;--red:#f85149;--orange:#d29922;
  --topbar:linear-gradient(135deg,#1c1100 0%,#2d1e00 100%)
}
/* TOP BAR */
.topbar{background:var(--topbar);border-bottom:1px solid #3d2e00;
  padding:.7rem 1.5rem;display:flex;align-items:center;
  justify-content:space-between;position:sticky;top:0;z-index:200}
.brand{display:flex;align-items:center;gap:.65rem;font-weight:900;
  font-size:1.1rem;color:#fff4d8}
.brand-sub{color:rgba(255,215,140,.7);font-weight:500;font-size:.83rem}
.tnav{display:flex;align-items:center;gap:.5rem}
.tnav a{color:rgba(255,215,140,.8);text-decoration:none;font-size:.83rem;
  padding:.3rem .65rem;border-radius:7px;transition:.15s}
.tnav a:hover{background:rgba(255,255,255,.12);color:#fff}
.tnav a.hi{color:#ffd060}
/* PAGE */
.page-wrap{padding:1.25rem 1.5rem;max-width:1400px;margin:0 auto}
/* FILTER BAR */
.filter-bar{display:flex;align-items:center;gap:.85rem;margin-bottom:1.25rem;flex-wrap:wrap}
.eng-select{padding:.55rem 1rem;border-radius:9px;border:1px solid var(--border);
  background:var(--card);color:var(--text);font-family:'Tajawal',sans-serif;
  font-size:.92rem;cursor:pointer;outline:none;min-width:200px;
  transition:border-color .15s}
.eng-select:hover,.eng-select:focus{border-color:var(--amber)}
.filter-lbl{color:var(--sub);font-size:.85rem;white-space:nowrap;font-weight:600}
.filter-cnt{color:var(--sub);font-size:.8rem;
  background:rgba(255,193,7,.1);border:1px solid rgba(255,193,7,.2);
  border-radius:20px;padding:2px 10px}
/* SECTION HEADER */
.sec-hdr{display:flex;align-items:center;gap:.6rem;margin-bottom:.85rem;
  padding-bottom:.5rem;border-bottom:1px solid var(--border)}
.sec-hdr h2{font-size:1rem;font-weight:700;color:var(--amber)}
.sec-hdr .sub{color:var(--sub);font-size:.8rem}
/* TENDER GRID */
.t-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1rem}
@media(max-width:600px){.t-grid{grid-template-columns:1fr}}
/* TENDER CARD */
.tcard{background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1rem 1.1rem;transition:.2s;position:relative;overflow:hidden}
.tcard:hover{border-color:rgba(255,193,7,.3);box-shadow:0 6px 20px rgba(0,0,0,.3)}
.tcard.urgent{border-left:3px solid var(--red)}
.tcard.soon{border-left:3px solid var(--orange)}
.tcard.normal{border-left:3px solid rgba(255,193,7,.4)}
.tcard.done{opacity:.7;border-left:3px solid var(--border)}
.tc-name{font-size:.9rem;font-weight:700;color:var(--text);margin-bottom:.4rem;
  line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tc-meta{display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:.75rem}
.tc-badge{font-size:.72rem;padding:2px 8px;border-radius:10px;font-weight:600}
.tc-badge.days-red{background:rgba(248,81,73,.15);color:#f85149}
.tc-badge.days-orange{background:rgba(210,153,34,.15);color:#d29922}
.tc-badge.days-green{background:rgba(63,185,80,.12);color:#3fb950}
.tc-badge.days-grey{background:rgba(110,118,129,.15);color:#6e7681}
.tc-badge.cat{background:rgba(255,193,7,.1);color:var(--amber)}
.tc-badge.locked{background:rgba(248,81,73,.12);color:#f85149}
.tc-status{font-size:.78rem;color:var(--sub);margin-bottom:.65rem}
.tc-status .st-val{font-weight:700}
.st-submitted{color:var(--amber)}
.st-won{color:var(--green)}
.st-lost{color:var(--red)}
.st-pending{color:var(--muted)}
/* ACTION BUTTONS */
.tc-actions{display:flex;gap:.5rem}
.act-btn{flex:1;padding:.45rem .3rem;border:1px solid;border-radius:8px;
  font-family:'Tajawal',sans-serif;font-size:.8rem;font-weight:700;cursor:pointer;
  transition:.2s;text-align:center}
.act-btn.submit{border-color:rgba(255,193,7,.4);background:rgba(255,193,7,.08);color:var(--amber)}
.act-btn.submit:hover,.act-btn.submit.sel{background:#ffc107;color:#000;border-color:#ffc107}
.act-btn.won{border-color:rgba(63,185,80,.4);background:rgba(63,185,80,.08);color:var(--green)}
.act-btn.won:hover,.act-btn.won.sel{background:#3fb950;color:#000;border-color:#3fb950}
.act-btn.lost{border-color:rgba(248,81,73,.4);background:rgba(248,81,73,.08);color:var(--red)}
.act-btn.lost:hover,.act-btn.lost.sel{background:#f85149;color:#fff;border-color:#f85149}
.act-btn:disabled{opacity:.45;cursor:default}
/* EMPTY STATE */
.empty{text-align:center;padding:3rem 1rem;color:var(--muted)}
.empty .icon{font-size:3rem;margin-bottom:.5rem}
/* TOAST */
#toast{position:fixed;bottom:1.5rem;right:1.5rem;z-index:9000;
  background:#2d2d2d;color:#fff;padding:.65rem 1.2rem;border-radius:10px;
  font-size:.84rem;box-shadow:0 4px 16px rgba(0,0,0,.4);
  opacity:0;transition:opacity .3s;pointer-events:none}
#toast.show{opacity:1}
/* STATS STRIP */
.stats-strip{display:flex;gap:1rem;margin-bottom:1.25rem;flex-wrap:wrap}
.ss-card{background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:.75rem 1.2rem;min-width:100px;text-align:center}
.ss-num{font-size:1.6rem;font-weight:900;color:var(--amber);line-height:1}
.ss-lbl{font-size:.72rem;color:var(--sub);margin-top:.2rem}
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <div class="brand">
    <span style="font-size:1.3rem">👷</span>
    <span>بوابة المهندسين</span>
    <span class="brand-sub">إدارة متابعة المنافسات</span>
  </div>
  <div class="tnav">
    <a href="/" class="hi">← اللوحة الرئيسية</a>
    <a href="/results">📊 النتائج</a>
    <a href="/logout">خروج ↩</a>
  </div>
</div>

<div class="page-wrap">

  <!-- STATS STRIP -->
  <div class="stats-strip">
    <div class="ss-card">
      <div class="ss-num">{{ total_tenders }}</div>
      <div class="ss-lbl">إجمالي المنافسات</div>
    </div>
    <div class="ss-card">
      <div class="ss-num" style="color:var(--orange)">{{ pending_tenders }}</div>
      <div class="ss-lbl">لم تُقدَّم بعد</div>
    </div>
    <div class="ss-card">
      <div class="ss-num" style="color:var(--amber)">{{ submitted_tenders }}</div>
      <div class="ss-lbl">تم التقديم</div>
    </div>
    <div class="ss-card">
      <div class="ss-num" style="color:var(--green)">{{ won_tenders }}</div>
      <div class="ss-lbl">فزنا</div>
    </div>
    <div class="ss-card">
      <div class="ss-num" style="color:var(--red)">{{ lost_tenders }}</div>
      <div class="ss-lbl">خسرنا</div>
    </div>
  </div>

  <!-- ENGINEER FILTER DROPDOWN -->
  <div class="filter-bar">
    <span class="filter-lbl">👷 المهندس:</span>
    <select class="eng-select" id="engSelect" onchange="filterEng(this.value)">
      <option value="__all__">📋 الكل — {{ total_tenders }} منافسة</option>
      {% for eng in engineers %}
      <option value="{{ eng }}">{{ eng }} — {{ eng_counts[eng] }} منافسة</option>
      {% endfor %}
    </select>
    <span class="filter-cnt" id="filterCnt"></span>
  </div>

  <!-- TENDER CARDS -->
  <div id="cardsGrid" class="t-grid">
    {% if tenders %}
    {% for t in tenders %}
    {% set days = t.days_left %}
    {% set urgency = 'urgent' if days is not none and days <= 3 else ('soon' if days is not none and days <= 7 else ('done' if t.result else 'normal')) %}
    {% set days_cls = 'days-red' if days is not none and days <= 3 else ('days-orange' if days is not none and days <= 7 else ('days-green' if days is not none and days > 7 else 'days-grey')) %}

    <div class="tcard {{ urgency }}" data-eng="{{ t.assigned_engineer or '' }}" id="tcard-{{ t.id }}">
      <a href="/tender/{{ t.id }}?from=engineer" class="tc-name" title="{{ t.title }}"
         style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
                overflow:hidden;text-decoration:none;color:inherit;
                transition:color .15s;cursor:pointer"
         onmouseover="this.style.color='#ffc107'"
         onmouseout="this.style.color=''">{{ t.title }}</a>

      <div class="tc-meta">
        {% if days is not none %}
        <span class="tc-badge {{ days_cls }}">
          {% if days < 0 %}انتهى{% elif days == 0 %}اليوم!{% elif days == 1 %}غداً!{% else %}{{ days }} يوم{% endif %}
        </span>
        {% endif %}
        {% if t.business_type %}
        <span class="tc-badge cat">{{ t.business_type }}</span>
        {% endif %}
        {% if t.engineer_locked %}
        <span class="tc-badge locked">🔒 مغلق</span>
        {% endif %}
        {% if t.assigned_engineer %}
        <span class="tc-badge" style="background:rgba(255,255,255,.07);color:var(--sub)">
          👤 {{ t.assigned_engineer }}
        </span>
        {% endif %}
      </div>

      <div class="tc-status">
        الحالة:
        {% if t.result == 'won' %}
          <span class="st-val st-won">✅ فزنا</span>
        {% elif t.result == 'lost' %}
          <span class="st-val st-lost">❌ خسرنا</span>
        {% elif t.did_submit %}
          <span class="st-val st-submitted">📤 تم التقديم</span>
        {% else %}
          <span class="st-val st-pending">⏳ لم تُقدَّم</span>
        {% endif %}
        {% if t.submission_date %}
        <span style="color:var(--muted);font-size:.72rem;margin-right:.4rem">
          — {{ t.submission_date }}
        </span>
        {% endif %}
      </div>

      <div class="tc-actions">
        <button class="act-btn submit {{ 'sel' if t.did_submit and not t.result }}"
                onclick="setStatus({{ t.id }}, 'submit', this)"
                {% if t.engineer_locked %}disabled title="المنافسة مغلقة"{% endif %}>
          📤 قدّمنا
        </button>
        <button class="act-btn won {{ 'sel' if t.result == 'won' }}"
                onclick="setStatus({{ t.id }}, 'won', this)"
                {% if t.engineer_locked %}disabled title="المنافسة مغلقة"{% endif %}>
          🏆 فزنا
        </button>
        <button class="act-btn lost {{ 'sel' if t.result == 'lost' }}"
                onclick="setStatus({{ t.id }}, 'lost', this)"
                {% if t.engineer_locked %}disabled title="المنافسة مغلقة"{% endif %}>
          ❌ خسرنا
        </button>
      </div>
    </div>
    {% endfor %}
    {% else %}
    <div class="empty" style="grid-column:1/-1">
      <div class="icon">👷</div>
      <div>لا توجد منافسات مسنَدة للمهندسين</div>
    </div>
    {% endif %}
  </div>

</div>

<!-- TOAST -->
<div id="toast"></div>

<script>
function filterEng(eng) {
  let visible = 0;
  document.querySelectorAll('.tcard').forEach(card => {
    const cardEng = (card.dataset.eng || '').trim();
    const match   = (eng === '__all__') || (cardEng === eng.trim());
    card.style.display = match ? '' : 'none';
    if (match) visible++;
  });
  const cnt = document.getElementById('filterCnt');
  if (cnt) cnt.textContent = (eng === '__all__') ? '' : visible + ' نتيجة';
}

function setStatus(tid, status, btn) {
  const card = document.getElementById('tcard-' + tid);
  const btns = card.querySelectorAll('.act-btn');
  btns.forEach(b => b.disabled = true);

  fetch('/api/eng/tender/' + tid + '/status', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({status: status})
  })
  .then(r => r.json())
  .then(d => {
    if (d.ok) {
      // تحديث الأزرار المحددة
      card.querySelectorAll('.act-btn').forEach(b => b.classList.remove('sel'));
      btn.classList.add('sel');
      // تحديث نص الحالة
      const stEl = card.querySelector('.tc-status');
      const statusMap = {
        'submit': '<span class="st-val st-submitted">📤 تم التقديم</span>',
        'won':    '<span class="st-val st-won">✅ فزنا</span>',
        'lost':   '<span class="st-val st-lost">❌ خسرنا</span>'
      };
      stEl.innerHTML = 'الحالة: ' + (statusMap[status] || '');
      // تحديث urgency class
      if (status === 'won' || status === 'lost') {
        card.classList.remove('urgent', 'soon', 'normal');
        card.classList.add('done');
      }
      showToast('✅ تم الحفظ');
    } else {
      showToast('⚠️ حدث خطأ: ' + (d.error || 'غير معروف'));
    }
  })
  .catch(() => showToast('⚠️ تعذر الاتصال بالخادم'))
  .finally(() => {
    btns.forEach(b => {
      if (!card.classList.contains('done')) b.disabled = false;
    });
  });
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2800);
}
</script>
</body></html>"""




OWNERS_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ذاكرة الجهات — {{ co.system_title }}</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:{{ co.theme_bg }};--card:{{ co.theme_card }};--hover:{{ co.theme_hover }};--head:{{ co.theme_head }};
  --amber:{{ co.theme_primary }};--amber-l:{{ co.theme_primary_l }};--amber-d:{{ co.theme_primary_d }};
  --red:#c22828;--green:#247848;--blue:#1a5a9a;--yellow:#d4a017;
  --muted:#9a8a60;--sub:#6a5a30;--border:rgba(138,72,0,.18);
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Tajawal',sans-serif;background:linear-gradient(160deg,#f7edc8 0%,#f3e3a8 45%,#eeda90 100%);
  min-height:100vh;color:#3a2400}
.topbar{background:linear-gradient(135deg,#5a2800 0%,#8a4800 55%,#b06000 100%);
  padding:.7rem 1.4rem;display:flex;align-items:center;gap:1rem;color:#ffe9b0;
  box-shadow:0 2px 18px rgba(60,20,0,.35);position:sticky;top:0;z-index:50}
.topbar img{height:34px;border-radius:7px;background:#fff;padding:2px}
.topbar b{font-size:1.05rem;color:#ffd97a}
.topbar a{color:#ffe9b0;text-decoration:none;font-size:.85rem;font-weight:600;
  padding:.3rem .7rem;border-radius:7px;transition:.15s}
.topbar a:hover{background:rgba(255,255,255,.12)}
.wrap{max-width:1250px;margin:1.2rem auto;padding:0 1rem}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.1rem}
@media(max-width:800px){.cards{grid-template-columns:1fr 1fr}}
.card{background:var(--card);border:1px solid var(--border);border-radius:13px;padding:.9rem 1.1rem;
  box-shadow:0 2px 10px rgba(120,70,0,.08)}
.card .n{font-size:1.7rem;font-weight:800;color:var(--amber)}
.card .l{font-size:.8rem;color:var(--sub);font-weight:600}
.panel{background:var(--card);border:1px solid var(--border);border-radius:13px;overflow:hidden;
  box-shadow:0 2px 12px rgba(120,70,0,.08)}
.phead{background:var(--head);padding:.7rem 1.1rem;font-weight:800;color:var(--amber-d);
  display:flex;justify-content:space-between;align-items:center;font-size:.95rem}
table{width:100%;border-collapse:collapse}
th{background:rgba(184,106,0,.08);color:var(--amber-d);font-size:.76rem;padding:.55rem .6rem;
  text-align:right;border-bottom:2px solid var(--border);white-space:nowrap}
td{padding:.55rem .6rem;border-bottom:1px solid rgba(138,72,0,.09);font-size:.82rem;vertical-align:middle}
tr:hover td{background:var(--hover)}
.score-wrap{display:flex;align-items:center;gap:.45rem;min-width:110px}
.score-bar{flex:1;height:7px;border-radius:4px;background:rgba(138,72,0,.12);overflow:hidden}
.score-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--amber-l),var(--amber))}
.score-n{font-weight:800;font-size:.8rem;color:var(--amber);min-width:26px}
.chip{font-size:.68rem;font-weight:800;padding:.2rem .55rem;border-radius:999px;white-space:nowrap}
.c-green{background:rgba(36,120,72,.13);color:var(--green);border:1px solid rgba(36,120,72,.3)}
.c-amber{background:rgba(184,106,0,.13);color:var(--amber-l);border:1px solid rgba(184,106,0,.3)}
.c-blue{background:rgba(26,90,154,.12);color:var(--blue);border:1px solid rgba(26,90,154,.3)}
.c-muted{background:rgba(120,110,80,.12);color:var(--muted);border:1px solid rgba(120,110,80,.25)}
.num{font-weight:700;text-align:center}
.dl-soon{color:var(--red);font-weight:800}
.dl-mid{color:var(--yellow);font-weight:700}
.foot{color:var(--sub);font-size:.72rem;text-align:center;padding:1rem}
/* ════ v5.8.0 MOBILE: owners table -> cards ════ */
@media(max-width:768px){
  .topbar{flex-wrap:wrap;padding:.55rem .8rem;gap:.35rem}
  .topbar a{min-height:40px;display:inline-flex;align-items:center}
  .cards{grid-template-columns:1fr 1fr!important;gap:.6rem}
  .card .n{font-size:1.45rem}
  table thead{display:none}
  table tbody{display:block}
  table tbody tr{
    display:block;border:1px solid var(--border);border-radius:11px;
    padding:.7rem .85rem;margin-bottom:.6rem;background:var(--card);
    box-shadow:0 1px 4px rgba(120,70,0,.06)}
  table tbody tr td{
    display:flex;justify-content:space-between;align-items:center;gap:.6rem;
    padding:.3rem 0;border:none;text-align:right!important;font-size:.85rem}
  table tbody tr td[data-label]::before{
    content:attr(data-label);color:var(--muted);font-size:.72rem;font-weight:700;flex-shrink:0}
  /* #index (first) hidden, name (second) = full-width bold header */
  table tbody tr td:first-child{display:none}
  table tbody tr td:nth-child(2){
    display:block;border-bottom:1px solid var(--border);padding-bottom:.45rem;margin-bottom:.25rem;
    font-weight:800;color:var(--amber-d);line-height:1.5}
  .score-wrap{min-width:0;flex:1;max-width:60%}
}
</style>
</head>
<body>
<div class="topbar">
  <img src="{{ logo_uri }}" alt="">
  <b>🏢 ذاكرة الجهات المالكة</b>
  <span style="flex:1"></span>
  <a href="/">🏠 اللوحة</a>
  <a href="/results">📊 سجل النتائج</a>
  <a href="/engineer-view">👷 المهندسين</a>
  <a href="/logout">خروج ↩</a>
</div>
<div class="wrap">
  <div class="cards">
    <div class="card"><div class="n">{{ s.total }}</div><div class="l">إجمالي الجهات المالكة</div></div>
    <div class="card"><div class="n">{{ s.active_org }}</div><div class="l">جهات بفرص جارية الآن</div></div>
    <div class="card"><div class="n">{{ s.winners }}</div><div class="l">جهات فزنا معها</div></div>
    <div class="card"><div class="n">{{ s.submissions }}</div><div class="l">إجمالي التقديمات المسجلة</div></div>
  </div>
  <div class="panel">
    <div class="phead">
      <span>محفظة الجهات — مرتبة بمؤشر الأولوية</span>
      <span style="font-size:.72rem;color:var(--sub)">آخر تحديث {{ refreshed }}</span>
    </div>
    <div style="overflow-x:auto">
    <table>
      <thead><tr>
        <th>#</th><th>الجهة المالكة</th><th>الأولوية</th><th>التصنيف</th>
        <th>جارية</th><th>قُدّمت</th><th>فوز</th><th>نسبة الفوز</th>
        <th>تمديدات</th><th>أقرب إغلاق</th>
      </tr></thead>
      <tbody>
        {% for o in owners %}
        <tr>
          <td style="color:var(--muted);font-size:.75rem">{{ loop.index }}</td>
          <td style="font-weight:700;color:var(--amber-d)" title="{{ o.name }}">{{ o.name }}</td>
          <td data-label="الأولوية"><div class="score-wrap">
            <span class="score-n">{{ o.score }}</span>
            <div class="score-bar"><div class="score-fill" style="width:{{ o.score }}%"></div></div>
          </div></td>
          <td data-label="التصنيف"><span class="chip {{ o.ccls }}">{{ o.cls }}</span></td>
          <td data-label="جارية" class="num" style="color:{% if o.active %}var(--amber){% else %}var(--muted){% endif %}">{{ o.active }}</td>
          <td data-label="قُدّمت" class="num">{{ o.submitted }}</td>
          <td data-label="فوز" class="num" style="color:{% if o.wins %}var(--green){% else %}var(--muted){% endif %}">{{ o.wins }}</td>
          <td data-label="نسبة الفوز" class="num">{% if o.win_rate is not none %}{{ o.win_rate }}%{% else %}—{% endif %}</td>
          <td data-label="تمديدات" class="num" title="عدد مرات تمديد هذه الجهة لمواعيدها تاريخياً">{% if o.ext %}🔮 {{ o.ext }}{% else %}—{% endif %}</td>
          <td data-label="أقرب إغلاق">{% if o.next_dl %}<span class="{% if o.days_next is not none and o.days_next <= 7 %}dl-soon{% elif o.days_next is not none and o.days_next <= 21 %}dl-mid{% endif %}">{{ o.next_dl }}{% if o.days_next is not none %} ({{ o.days_next }}ي){% endif %}</span>{% else %}—{% endif %}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    </div>
  </div>
  <div class="foot">{{ co.system_title }} لمتابعة المنافسات — ذاكرة الجهات مبنية آلياً من سجل النتائج وأحداث التمديد · 💚 {{ co.team_ar }}</div>
</div>
</body>
</html>"""
