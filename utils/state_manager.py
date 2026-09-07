"""
مدير حالة الجلسة (Session State Manager) لتطبيق CareerHub AI
يدعم إدارة كائنات UserProfile الهيكلية، وتوحيد المهارات، والتكامل السحابي مع Supabase Auth.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import streamlit as st

from .models import UserProfile
from .skill_normalizer import normalize_skills
from .supabase_client import (
    is_supabase_configured,
    sign_in_user,
    sign_up_user,
    sign_out_user,
    save_profile_to_db,
    load_profile_from_db,
)

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

    # متغيرات المصادقة والتخزين السحابي (ST-05)
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None

    if "is_logged_in" not in st.session_state:
        st.session_state["is_logged_in"] = False

    if "cloud_synced" not in st.session_state:
        st.session_state["cloud_synced"] = False


def get_auth_user() -> Optional[Dict[str, Any]]:
    """الحصول على بيانات المستخدم المسجل حالياً."""
    return st.session_state.get("auth_user", None)


def is_user_logged_in() -> bool:
    """التحقق مما إذا كان المستخدم مسجل دخول."""
    return bool(st.session_state.get("is_logged_in", False) and st.session_state.get("auth_user"))


def set_auth_user(user_data: Optional[Dict[str, Any]]) -> None:
    """تعيين بيانات المستخدم المسجل."""
    if user_data:
        st.session_state["auth_user"] = user_data
        st.session_state["is_logged_in"] = True
    else:
        clear_auth_user()


def clear_auth_user() -> None:
    """مسح بيانات تسجيل الدخول والرجوع لوضع الزائر."""
    st.session_state["auth_user"] = None
    st.session_state["is_logged_in"] = False
    st.session_state["cloud_synced"] = False
    sign_out_user()


def get_user_profile() -> Optional[UserProfile]:
    """الحصول على بيانات السيرة الذاتية المعتمدة ككائن UserProfile."""
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
    اعتماد وحفظ بيانات السيرة الذاتية رسمياً في الجلسة مع توحيد المهارات.
    """
    if isinstance(profile_data, UserProfile):
        data_dict = profile_data.to_dict()
    else:
        data_dict = dict(profile_data)

    # 1. توحيد المهارات الرئيسية
    raw_skills = data_dict.get("skills", [])
    data_dict["skills"] = normalize_skills(raw_skills)

    # 2. توحيد تقنيات المشاريع
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
    """إعادة ضبط الجلسة ومسح بيانات السيرة الذاتية المؤقتة."""
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


def render_auth_sidebar() -> None:
    """
    عنصر واجهة موحد للمصادقة السحابية في الشريط الجانبي (Sidebar).
    يعمل في الصفحة الرئيسية وكافة الصفحات الفرعية.
    """
    st.sidebar.divider()
    st.sidebar.markdown("### ☁️ الحساب والمزامنة السحابية")

    supabase_active = is_supabase_configured()

    if not supabase_active:
        st.sidebar.caption("👤 **وضع الزائر (Guest Mode)**")
        st.sidebar.info("💡 وضع التخزين المؤقت مفعّل (الجلسة الحالية فقط).")
        return

    # إذا كان Supabase مفعلاً
    if is_user_logged_in():
        user = get_auth_user()
        user_email = user.get("email", "المستخدم") if user else "المستخدم"
        st.sidebar.success(f"🟢 مرحباً، **{user_email}**")

        col_s1, col_s2 = st.sidebar.columns(2)
        with col_s1:
            if st.sidebar.button("☁️ حفظ سحابياً", use_container_width=True, help="حفظ السيرة الذاتية الحالية في حسابك السحابي"):
                active_profile = get_user_profile()
                if active_profile and user:
                    success = save_profile_to_db(user["id"], active_profile.to_dict(), user.get("email"))
                    if success:
                        st.toast("☁️ تم حفظ السيرة الذاتية في السحابة بنجاح!", icon="✅")
                    else:
                        st.error("فشل الحفظ السحابي.")
                else:
                    st.warning("لا توجد سيرة ذاتية معتمدة لحفظها.")

        with col_s2:
            if st.sidebar.button("🔄 استرجاع السيرة", use_container_width=True, help="استرجاع السيرة الذاتية المحفوظة من حسابك"):
                if user:
                    loaded = load_profile_from_db(user["id"])
                    if loaded:
                        set_user_profile(loaded, demo_mode=False, show_toast=False)
                        st.toast("📥 تم استرجاع سيرتك الذاتية من السحابة بنجاح!", icon="🚀")
                        st.rerun()
                    else:
                        st.info("لا توجد سيرة ذاتية محفوظة مسبقاً في حسابك.")

        if st.sidebar.button("🚪 تسجيل الخروج", use_container_width=True):
            clear_auth_user()
            st.rerun()

    else:
        st.sidebar.caption("👤 **وضع الزائر (Guest Mode)**")
        with st.sidebar.expander("🔐 تسجيل الدخول / إنشاء حساب"):
            auth_mode = st.radio("العملية:", ["تسجيل الدخول", "حساب جديد"], horizontal=True)
            auth_email = st.text_input("البريد الإلكتروني:", key="sb_auth_email")
            auth_pass = st.text_input("كلمة المرور:", type="password", key="sb_auth_pass")

            if auth_mode == "تسجيل الدخول":
                if st.button("تسجيل الدخول", type="primary", use_container_width=True):
                    with st.spinner("جاري التحقق..."):
                        ok, msg, user_data = sign_in_user(auth_email, auth_pass)
                        if ok and user_data:
                            set_auth_user(user_data)
                            # فحص إذا كان للمستخدم بروفايل محفوظ مسبقاً
                            existing_profile = load_profile_from_db(user_data["id"])
                            if existing_profile:
                                set_user_profile(existing_profile, demo_mode=False, show_toast=False)
                            st.toast(f"مرحباً بك {auth_email}!", icon="👋")
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                if st.button("إنشاء الحساب", type="primary", use_container_width=True):
                    with st.spinner("جاري إنشاء الحساب..."):
                        ok, msg = sign_up_user(auth_email, auth_pass)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
