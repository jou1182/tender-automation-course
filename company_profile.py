# -*- coding: utf-8 -*-
"""Company identity loader — single source of truth for all tenant-specific
branding. Reads company_profile.json; falls back to embedded generic defaults.
Import PROFILE anywhere: `from company_profile import PROFILE`."""
import json
from pathlib import Path

_DEFAULTS = {
    "name_ar": "شركة المقاولات النموذجية",
    "name_en": "SAMPLE CONTRACTING",
    "short_ar": "النموذجية",
    "system_title": "نظام متابعة المناقصات",
    "system_subtitle": "لوحة متابعة المنافسات",
    "team_ar": "فريق العروض الفنية",
    "department_ar": "قسم العروض الفنية",
    "portal_url": "https://your-portal.example.com",
    "portal_export_path": "/ar/tendering/export_to_excel_in_progress_tender/",
    "portal_cookie_domain": ".example.com",
    "theme_bg": "#b88800",
    "theme_card": "#fffde8",
    "theme_hover": "#fdf5c0",
    "theme_head": "#f5e870",
    "theme_primary": "#8a4800",
    "theme_primary_l": "#b86a00",
    "theme_primary_d": "#5e2e00",
    "footer_owner": "Your Name",
    "footer_url": "https://example.com",
    "ai_scope_ar": "المناقصات الحكومية السعودية ومنصة النموذجية",
    "engineers": [{"name": "مهندس", "capacity": 5}, {"name": "مهندس", "capacity": 5},
                  {"name": "مهندس", "capacity": 5}, {"name": "مهندس", "capacity": 5},
                  {"name": "مهندس", "capacity": 5}, {"name": "مهندس", "capacity": 5}],
    "dual_approval": False,
}

def load_profile():
    data = dict(_DEFAULTS)
    try:
        p = Path(__file__).parent / "company_profile.json"
        if p.exists():
            raw = json.loads(p.read_text(encoding="utf-8"))
            for k, v in raw.items():
                if k.startswith("_"):
                    continue
                if isinstance(v, bool):
                    data[k] = v
                elif isinstance(v, str) and v.strip():
                    data[k] = v
                elif isinstance(v, list):
                    data[k] = v
    except Exception:
        pass
    return data

PROFILE = load_profile()
