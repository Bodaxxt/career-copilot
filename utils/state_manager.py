"""
مدير حالة الجلسة (Session State Manager) لتطبيق CareerHub AI
يضمن تهيئة المتغيرات ومنع أخطاء KeyError عند التنقل المباشر بين الصفحات.
"""

from datetime import datetime
from typing import Any, Dict, Optional
import streamlit as st

# بيانات تجريبية جاهزة للـ Demo Mode
DEMO_PROFILE_DATA: Dict[str, Any] = {
    "full_name": "سارة أحمد النجار",
    "headline": "Senior Data Scientist & AI Engineer",
    "summary": "مهندسة ذكاء اصطناعي بخبرة 5 سنوات في بناء نماذج تعلم الآلة ومعالجة اللغات الطبيعية (NLP) وحلول RAG السحابية.",
    "skills": [
        "Python",
        "FastAPI",
        "Pytorch",
        "Tensorflow",
        "Langchain",
        "Docker",
        "PostgreSQL",
        "AWS",
        "Streamlit",
        "Git"
    ],
    "experiences": [
        {
            "company": "تقنية المستقبل للذكاء الاصطناعي",
            "title": "Lead AI Engineer",
            "period": "2022-03 إلى current",
            "achievements": [
                "قيادة فريق تطوير مساعد ذكي للشركات بنظام RAG حسّن دقة الإجابات بنسبة 35%.",
                "نشر وتوسيع نماذج التعلم العميق على Kubernetes لمعالجة أكثر من 100 ألف طلب يومياً.",
                "تقليل تكاليف الاستدلال السحابي بنسبة 25% عبر تقنيات Quantization و Caching."
            ]
        },
        {
            "company": "بيانات للحلول الرقمية",
            "title": "Data Scientist",
            "period": "2019-07 إلى 2022-02",
            "achievements": [
                "تطوير منظومة توصيات منتجات ذكية رفعت معدل التحويل بنسبة 18%.",
                "أتمتة خطوط معالجة وتدقيق البيانات (ETL) باستخدام Apache Spark و Airflow."
            ]
        }
    ],
    "education": [
        {
            "university": "جامعة الملك فهد للبترول والمعادن",
            "degree": "بكالوريوس",
            "field": "هندسة البرمجيات والذكاء الاصطناعي",
            "year": "2019"
        }
    ],
    "projects": [
        {
            "name": "منظومة تقييم السير الذاتية بالذكاء الاصطناعي",
            "technologies": ["Python", "FastAPI", "Gemini API", "ChromaDB"],
            "description": "محرك ذكي لتحليل ومطابقة متطلبات الوظائف تلقائياً مع السير الذاتية."
        },
        {
            "name": "محرك استرجاع البيانات الذكي (Enterprise RAG)",
            "technologies": ["LangChain", "OpenAI", "Pinecone", "Streamlit"],
            "description": "منصة بحث دلالي للوثائق القانونية والمؤسسية الضخمة."
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

    if "parsed_at" not in st.session_state:
        st.session_state["parsed_at"] = None

    if "demo_mode" not in st.session_state:
        st.session_state["demo_mode"] = False


def get_user_profile() -> Optional[Dict[str, Any]]:
    """الحصول على بيانات السيرة الذاتية الحالية."""
    return st.session_state.get("user_profile", None)


def set_user_profile(profile_dict: Dict[str, Any], demo_mode: bool = False) -> None:
    """تحديث بيانات السيرة الذاتية وحالة الجلسة."""
    st.session_state["user_profile"] = profile_dict
    st.session_state["parsed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["demo_mode"] = demo_mode


def set_demo_mode() -> None:
    """تفعيل الوضع التجريبي وتعبئة بيانات افتراضية فوراً."""
    set_user_profile(DEMO_PROFILE_DATA, demo_mode=True)


def reset_session() -> None:
    """إعادة ضبط الجلسة ومسح بيانات السيرة الذاتية."""
    st.session_state["user_profile"] = None
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
        st.info("💡 يمكنك العودة للصفحة الرئيسية عبر القائمة الجانبية 👈 أو تفعيل الوضع التجريبي بالزر أدناه:")
        if st.button("🚀 تفعيل الوضع التجريبي فوراً (Demo Mode)", type="primary"):
            set_demo_mode()
            st.rerun()
        st.stop()
    return profile
