"""
مدير حالة الجلسة (Session State Manager) لتطبيق CareerHub AI
يدعم إدارة السير الذاتية، التعديل اليدوي، استخراج النصوص الخام، والـ Fallback الآمن.
"""

from datetime import datetime
from typing import Any, Dict, Optional
import streamlit as st

# بيانات تجريبية واقعية للـ Demo Mode (Full-Stack & Data/AI Engineer)
DEMO_PROFILE_DATA: Dict[str, Any] = {
    "full_name": "سارة أحمد النجار",
    "headline": "Senior Full-Stack & AI Systems Engineer",
    "summary": "مهندسة برمجيات وذكاء اصطناعي بخبرة 5 سنوات في بناء تطبيقات الويب المتكاملة وحلول RAG السحابية وتكامل النماذج اللغوية الكبيرة.",
    "skills": [
        "Python",
        "FastAPI",
        "React",
        "TypeScript",
        "PyTorch",
        "LangChain",
        "Docker",
        "PostgreSQL",
        "AWS",
        "Streamlit",
        "Git",
        "Redis"
    ],
    "experiences": [
        {
            "company": "تقنية المستقبل للذكاء الاصطناعي (Future Tech AI)",
            "title": "Lead AI & Full-Stack Engineer",
            "period": "2022-03 إلى current",
            "achievements": [
                "بناء وتطوير منصة محادثة ذكية بنظام RAG حسنت دقة استرجاع البيانات بنسبة 35% لـ 50 ألف مستخدم.",
                "تصميم واجهات مستخدم تفاعلية بـ React و Streamlit متصلة بـ Microservices قائمة على FastAPI.",
                "تقليل تكاليف الاستدلال السحابي (Inference Costs) بنسبة 25% عبر تقنيات Caching و Model Quantization."
            ]
        },
        {
            "company": "بيانات للحلول الرقمية (Digital Data Solutions)",
            "title": "Software Engineer",
            "period": "2019-07 إلى 2022-02",
            "achievements": [
                "تطوير وتوسيع بوابات الدفع الإلكتروني وربط قواعد بيانات PostgreSQL الموزعة.",
                "أتمتة خطوط معالجة وتدقيق البيانات (CI/CD Pipelines) باستخدام Docker و GitHub Actions."
            ]
        }
    ],
    "education": [
        {
            "university": "جامعة الملك فهد للبترول والمعادن",
            "degree": "بكالوريوس",
            "field": "هندسة البرمجيات وعلوم الحاسب",
            "year": "2019"
        }
    ],
    "projects": [
        {
            "name": "منظومة تقييم السير الذاتية الذكية (CareerHub AI)",
            "technologies": ["Python", "Streamlit", "Gemini API", "ChromaDB"],
            "description": "محرك ذكي لتحليل ومطابقة متطلبات الوظائف تلقائياً مع السير الذاتية بنظام ATS."
        },
        {
            "name": "محرك البحث الدلالي للمستندات الضخمة (Enterprise Semantic Search)",
            "technologies": ["LangChain", "OpenAI", "Pinecone", "FastAPI"],
            "description": "منصة بحث واسترجاع معرفي ذكي للوثائق المؤسسية والتقارير المالية."
        }
    ]
}


def init_session_state() -> None:
    """
    تهيئة حالة الجلسة (Session State) بشكل آمن ومركزي.
    تُستدعى في بداية كل صفحة لمنع أخطاء KeyError.
    """
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = None

    if "temp_draft_profile" not in st.session_state:
        st.session_state["temp_draft_profile"] = None

    if "raw_pdf_text" not in st.session_state:
        st.session_state["raw_pdf_text"] = None

    if "parse_status" not in st.session_state:
        # الحالات الممكنة: 'empty', 'parsing', 'success', 'manual_edit', 'error'
        st.session_state["parse_status"] = "empty"

    if "parsed_at" not in st.session_state:
        st.session_state["parsed_at"] = None

    if "demo_mode" not in st.session_state:
        st.session_state["demo_mode"] = False


def get_user_profile() -> Optional[Dict[str, Any]]:
    """الحصول على بيانات السيرة الذاتية المعتمدة الحالية."""
    return st.session_state.get("user_profile", None)


def get_temp_draft_profile() -> Optional[Dict[str, Any]]:
    """الحصول على مسودة البيانات قيد التعديل اليدوي."""
    return st.session_state.get("temp_draft_profile", None)


def set_temp_draft_profile(profile_dict: Optional[Dict[str, Any]]) -> None:
    """تعيين مسودة البيانات للتعديل اليدوي."""
    st.session_state["temp_draft_profile"] = profile_dict


def get_raw_pdf_text() -> Optional[str]:
    """الحصول على النص الخام المستخرج محلياً من ملف الـ PDF."""
    return st.session_state.get("raw_pdf_text", None)


def set_raw_pdf_text(text: Optional[str]) -> None:
    """حفظ النص الخام المستخرج محلياً في الجلسة."""
    st.session_state["raw_pdf_text"] = text


def get_parse_status() -> str:
    """معرفة حالة المعالجة الحالية."""
    return st.session_state.get("parse_status", "empty")


def set_parse_status(status: str) -> None:
    """تحديث حالة المعالجة ('empty', 'parsing', 'success', 'manual_edit', 'error')."""
    st.session_state["parse_status"] = status


def set_user_profile(
    profile_dict: Dict[str, Any], demo_mode: bool = False, show_toast: bool = True
) -> None:
    """
    اعتماد وحفظ بيانات السيرة الذاتية رسمياً في الجلسة.
    """
    st.session_state["user_profile"] = profile_dict
    st.session_state["temp_draft_profile"] = profile_dict
    st.session_state["parsed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["demo_mode"] = demo_mode
    st.session_state["parse_status"] = "success"

    if show_toast:
        st.toast(
            "✅ تم اعتماد السيرة الذاتية بنجاح! يمكنك الآن الانتقال لصفحات التقييم والوظائف.",
            icon="🚀"
        )


def set_demo_mode() -> None:
    """تفعيل الوضع التجريبي وتعبئة بيانات افتراضية فوراً."""
    demo_raw_text = """--- سيرة ذاتية تجريبية ---
الاسم: سارة أحمد النجار
المسمى: Senior Full-Stack & AI Systems Engineer
البريد: sara.alnajjar@example.com
الخبرات:
- Lead AI & Full-Stack Engineer في تقنية المستقبل للذكاء الاصطناعي (2022 - الحالي)
- Software Engineer في بيانات للحلول الرقمية (2019 - 2022)
التعليم: بكالوريوس هندسة برمجيات - جامعة الملك فهد للبترول والمعادن (2019)
المهارات: Python, FastAPI, React, TypeScript, PyTorch, LangChain, Docker, PostgreSQL, AWS
"""
    set_raw_pdf_text(demo_raw_text)
    set_user_profile(DEMO_PROFILE_DATA, demo_mode=True, show_toast=True)


def reset_session() -> None:
    """إعادة ضبط الجلسة ومسح كافة بيانات السيرة الذاتية المؤقتة والمعتمدة."""
    st.session_state["user_profile"] = None
    st.session_state["temp_draft_profile"] = None
    st.session_state["raw_pdf_text"] = None
    st.session_state["parse_status"] = "empty"
    st.session_state["parsed_at"] = None
    st.session_state["demo_mode"] = False


def require_cv_profile() -> Dict[str, Any]:
    """
    دالة حماية للصفحات الفرعية:
    تتحقق من وجود السيرة الذاتية، وتعرض تنبيهاً وتوقف تنفيذ الصفحة إذا لم تكن متوفرة.
    """
    profile = get_user_profile()
    if profile is None:
        st.warning("⚠️ يرجى رفع السيرة الذاتية أولاً من الصفحة الرئيسية أو تفعيل الوضع التجريبي.")
        st.info("💡 يمكنك العودة للصفحة الرئيسية عبر القائمة الجانبية 👈 أو تفعيل الوضع التجريبي بنقرة واحدة:")
        if st.button("🚀 تفعيل الوضع التجريبي فوراً (Demo Mode)", type="primary"):
            set_demo_mode()
            st.rerun()
        st.stop()
    return profile
