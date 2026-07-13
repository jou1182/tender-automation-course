# -*- coding: utf-8 -*-
"""portal_adapter.py — العقد المعياري لأي منصة مناقصات جديدة.

كل منصة عربية مختلفة في آلية الدخول والتصدير. هذا الملف لا "يحل" الفروق —
بل يفرض عقداً واضحاً: أي منصة جديدة تنفّذ دالة واحدة إجبارية:

    fetch_to_file() -> bool   # اسحب المنافسات واكتبها كملف Excel قياسي، أرجع النجاح

هذا هو بالضبط ما يحتاجه محرك المقارنة (engine_core) — يقرأ نفس الملف القياسي
بعد النجاح. أي منصة API-based يمكنها أيضاً تنفيذ export_tenders() -> DataFrame.

المحوّل المرجعي (AlRawafPortalAdapter) يُغلّف export_in_progress.py الحي حرفياً
بلا أي تغيير في سلوكه — لذلك ربط هذا الملف بالمحرك = صفر تغيير سلوكي.

اختيار المنصة المفعّلة: مفتاح "portal_adapter" في company_profile.json
(الافتراضي: "alrawaf"). لإضافة منصة: أنشئ فئة ترث PortalAdapter، سجّلها في
_REGISTRY، وضع اسمها في ملف الهوية.
"""
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

# الأعمدة التي يتوقعها engine_core من أي منصة (ثابتة بالعربية لأنه نظامك الحالي)
REQUIRED_COLUMNS = [
    "رقم المنافسة", "اسم المنافسة", "المالك",
    "تاريخ التقديم", "نوع الأعمال", "القطاع",
]


class PortalAdapter(ABC):
    """العقد الذي تنفّذه أي منصة مناقصات."""

    platform_name: str = "منصة غير مسمّاة"

    @abstractmethod
    def fetch_to_file(self) -> bool:
        """اسحب المنافسات الحالية واكتبها كملف Excel قياسي في المسار المتوقّع
        (output/in_progress_tenders.xlsx). أرجع True عند النجاح، False عند الفشل.
        لا تُنفّذ منطق المقارنة هنا — هذا عمل engine_core حصراً."""
        raise NotImplementedError

    def export_tenders(self) -> pd.DataFrame:
        """(اختياري) يُرجع المنافسات كـ DataFrame — مفيد للمنصات القائمة على API.
        التنفيذ الافتراضي: يشغّل fetch_to_file ثم يقرأ الملف القياسي."""
        if not self.fetch_to_file():
            raise RuntimeError(f"فشل السحب من {self.platform_name}")
        target = Path(__file__).parent / "output" / "in_progress_tenders.xlsx"
        return pd.read_excel(target)

    def validate_columns(self, df: pd.DataFrame) -> list:
        return [c for c in REQUIRED_COLUMNS if c not in df.columns]


class AlRawafPortalAdapter(PortalAdapter):
    """المحوّل المرجعي — يُغلّف export_in_progress.py الحي بلا أي تعديل عليه."""

    platform_name = "الرواف"

    def fetch_to_file(self) -> bool:
        # سلوك مطابق تماماً للاستدعاء المباشر السابق: export_in_progress.main()
        import export_in_progress
        return bool(export_in_progress.main())


# ── سجل المنصات المتاحة ──
_REGISTRY = {
    "default": AlRawafPortalAdapter,   # المحوّل المرجعي (مثال قابل للاستبدال)
    "alrawaf": AlRawafPortalAdapter,
    # "etimad": EtimadPortalAdapter,   # تُضاف عند بناء محوّل اعتماد الفعلي
}


def get_active_portal() -> PortalAdapter:
    """يعيد محوّل المنصة المفعّلة حسب company_profile.json (الافتراضي: الرواف)."""
    key = "alrawaf"
    try:
        from company_profile import PROFILE
        key = (PROFILE.get("portal_adapter") or "alrawaf").strip().lower()
    except Exception:
        pass
    cls = _REGISTRY.get(key, AlRawafPortalAdapter)
    return cls()
