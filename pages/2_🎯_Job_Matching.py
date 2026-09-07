import streamlit as st
from utils.state_manager import init_session_state, require_cv_profile, render_auth_sidebar

# 1. تهيئة حالة الجلسة
init_session_state()

# 2. إعداد الصفحة
st.set_page_config(
    page_title="مطابقة الوظائف الذكية | CareerHub AI",
    page_icon="🎯",
    layout="wide"
)

# 3. عرض مصادقة الشريط الجانبي والتحقق الإلزامي من وجود السيرة الذاتية
render_auth_sidebar()
profile = require_cv_profile()

st.title("🎯 محرك مطابقة الوظائف الذكي (RAG Job Matching)")
st.markdown("مطابقة دلالية بين خبراتك والفرص الوظيفية المتاحة باستخدام تقنيات الاسترجاع الذكي (RAG).")

st.divider()

col_header1, col_header2 = st.columns([2, 1])
with col_header1:
    st.subheader(f"مرحباً {profile.get('full_name', 'بك')} 👋")
    st.caption(f"المجال التخصصي: {profile.get('headline', 'غير محدد')}")
with col_header2:
    mode_badge = "🟢 وضع تجريبي (Demo Mode)" if st.session_state.get("demo_mode") else "🔵 سيرة ذاتية مرفوعة"
    st.markdown(f"**الحالة:** `{mode_badge}`")

st.divider()

st.subheader("📋 مقارنة الوصف الوظيفي (Job Description Matching)")
job_description = st.text_area(
    "الصق نص الوصف الوظيفي للمطابقة (Job Description):",
    placeholder="e.g. We are looking for a Senior AI Engineer with strong background in Python, RAG, and FastAPI...",
    height=150
)

if st.button("🔍 تحليل نسبة التطابق والفجوات (Gap Analysis)", type="primary"):
    if not job_description.strip():
        st.warning("يرجى إدخال نص الوصف الوظيفي أولاً.")
    else:
        st.info("⏳ سيتم تفعيل محرك RAG المعتمد على الـ Embeddings في Sprint 2 لمقارنة المتطلبات مباشرة.")

with st.expander("💼 ملخص الخبرات المعتمدة في المطابقة"):
    experiences = profile.experiences if hasattr(profile, "experiences") else profile.get("experiences", [])
    if experiences:
        for exp in experiences:
            t = exp.title if hasattr(exp, "title") else exp.get("title")
            c = exp.company if hasattr(exp, "company") else exp.get("company")
            p = exp.period if hasattr(exp, "period") else exp.get("period")
            ach_list = exp.achievements if hasattr(exp, "achievements") else exp.get("achievements", [])
            st.markdown(f"**{t}** في **{c}** ({p})")
            for ach in ach_list:
                st.write(f"- {ach}")
    else:
        st.write("لا توجد خبرات مسجلة.")
