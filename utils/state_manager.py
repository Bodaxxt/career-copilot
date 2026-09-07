"""
مدير حالة الجلسة (Session State Manager) لتطبيق CareerHub AI
يدعم إدارة كائنات UserProfile الهيكلية (Pydantic v2)، وتوحيد المهارات عبر SkillNormalizer.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import streamlit as st

from .models import UserProfile
from .skill_normalizer import normalize_skills

# بيانات تجريبية واقعية ومحدثة للـ Demo Mode
DEMO_PROFILE_DATA: Dict[str, Any] = {
    "full_name": "سارة أحمد النجار",
    "headline": "Senior Full-Stack & AI Systems Engineer",
    "summary": "مهندسة برمجيات وذكاء اصطناعي بخبرة 5 سنوات في بناء تطبيقات الويب المتكاملة وحلول RAG السحابية وتكامل النماذج اللغوية الكبيرة.",
    "skills": [
        "python3",
        "fastapi",
        "reactjs",
        "typescript",
        "pytorch",
        "langchain",
        "k8s",
        "docker",
        "postgres",
        "aws",
        "streamlit",
        "git",
        "redis"
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
            "technologies": ["python", "streamlit", "gemini api", "chromadb"],
            "description": "محرك ذكي لتحليل ومطابقة متطلبات الوظائف تلقائياً مع السير الذاتية بنظام ATS."
        },
        {
            "name": "محرك البحث الدلالي للمستندات الضخمة (Enterprise Semantic Search)",
            "technologies": ["langchain", "openai api", "pinecone", "fastapi"],
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
        st.session_state["parse_status"] = "empty"

    if "normalized_skills_count" not in st.session_state:
        st.session_state["normalized_skills_count"] = 0

    if "parsed_at" not in st.session_state:
        st.session_state["parsed_at"] = None

    if "demo_mode" not in st.session_state:
        st.session_state["demo_mode"] = False


def get_user_profile() -> Optional[UserProfile]:
    """
    الحصول على بيانات السيرة الذاتية المعتمدة الحالية ككائن UserProfile.
    """
    raw_profile = st.session_state.get("user_profile", None)
    if raw_profile is None:
        return None
    if isinstance(raw_profile, UserProfile):
        return raw_profile
    if isinstance(raw_profile, dict):
        return UserProfile.from_dict(raw_profile)
    return None


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
    profile_data: Union[Dict[str, Any], UserProfile],
    demo_mode: bool = False,
    show_toast: bool = True
) -> UserProfile:
    """
    اعتماد وحفظ بيانات السيرة الذاتية رسمياً في الجلسة:
    1. توحيد وتنقية المهارات تلقائياً عبر SkillNormalizer.
    2. توحيد تقنيات المشاريع.
    3. التحقق الهيكلي عبر Pydantic v2 (UserProfile).
    4. حفظ الكائن والـ Dict في الجلسة وتحديث عدد المهارات الموحدة.
    """
    # تحويل البيانات إلى Dict قابل للتعديل
    if isinstance(profile_data, UserProfile):
        data_dict = profile_data.to_dict()
    else:
        data_dict = dict(profile_data)

    # 1. توحيد المهارات الرئيسية
    raw_skills = data_dict.get("skills", [])
    data_dict["skills"] = normalize_skills(raw_skills)

    # 2. توحيد تقنيات المشاريع إن وجدت
    projects = data_dict.get("projects", [])
    if isinstance(projects, list):
        for p in projects:
            if isinstance(p, dict) and "technologies" in p:
                p["technologies"] = normalize_skills(p.get("technologies", []))
            elif hasattr(p, "technologies"):
                p.technologies = normalize_skills(getattr(p, "technologies", []))

    # 3. التحقق الهيكلي عبر UserProfile
    profile_obj = UserProfile.from_dict(data_dict)

    # 4. الحفظ في Session State
    st.session_state["user_profile"] = profile_obj.to_dict()
    st.session_state["temp_draft_profile"] = profile_obj.to_dict()
    st.session_state["normalized_skills_count"] = len(profile_obj.skills)
    st.session_state["parsed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["demo_mode"] = demo_mode
    st.session_state["parse_status"] = "success"

    if show_toast:
        st.toast(
            f"✅ تم اعتماد السيرة الذاتية وتوحيد {len(profile_obj.skills)} مهارة بنجاح!",
            icon="🚀"
        )

    return profile_obj


def set_demo_mode() -> None:
    """تفعيل الوضع التجريبي وتعبئة بيانات افتراضية موحدة فوراً."""
    demo_raw_text = """--- سيرة ذاتية تجريبية ---
الاسم: سارة أحمد النجار
المسمى: Senior Full-Stack & AI Systems Engineer
الخبرات: Lead AI Engineer (2022-current), Software Engineer (2019-2022)
المهارات: python3, fastapi, reactjs, typescript, pytorch, langchain, k8s, docker, postgres, aws, redis
"""
    set_raw_pdf_text(demo_raw_text)
    set_user_profile(DEMO_PROFILE_DATA, demo_mode=True, show_toast=True)


def reset_session() -> None:
    """إعادة ضبط الجلسة ومسح كافة بيانات السيرة الذاتية."""
    st.session_state["user_profile"] = None
    st.session_state["temp_draft_profile"] = None
    st.session_state["raw_pdf_text"] = None
    st.session_state["parse_status"] = "empty"
    st.session_state["normalized_skills_count"] = 0
    st.session_state["parsed_at"] = None
    st.session_state["demo_mode"] = False


def require_cv_profile() -> UserProfile:
    """
    دالة حماية للصفحات الفرعية:
    تتحقق من وجود السيرة الذاتية، وتعرض تنبيهاً وتوقف تنفيذ الصفحة إذا لم تكن متوفرة.
    ترجع كائن UserProfile جاهز للاستخدام.
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
