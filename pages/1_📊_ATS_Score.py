import streamlit as st
from utils.state_manager import init_session_state, require_cv_profile, render_auth_sidebar

# 1. تهيئة حالة الجلسة
init_session_state()

# 2. إعداد الصفحة
st.set_page_config(
    page_title="تقييم ATS | CareerHub AI",
    page_icon="📊",
    layout="wide"
)

# 3. عرض مصادقة الشريط الجانبي والتحقق الإلزامي من وجود السيرة الذاتية
render_auth_sidebar()
profile = require_cv_profile()

st.title("📊 نظام فحص ومطابقة أنظمة تتبع المتقدمين (ATS Evaluation)")
st.markdown("تحليل دقيق لمدى توافق سيرتك الذاتية مع معايير أنظمة التوظيف الآلية (ATS).")

st.divider()

# عرض ملخص الملف الشخصي المحمل
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("👤 المرشح", profile.get("full_name") or "غير محدد")
with col_info2:
    st.metric("💼 المسمى المستهدف", profile.get("headline") or "غير محدد")
with col_info3:
    st.metric("🛠️ عدد المهارات الموحدة", len(profile.skills) if hasattr(profile, "skills") else len(profile.get("skills", [])))

st.divider()

# منطقة التقييم (Sprint 2 Ready)
st.subheader("🎯 بطاقة التقييم التفاعلية (قيد التطوير - Sprint 2)")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.info("💡 **المعايير المعتمدة في التقييم القادم:**\n"
            "- قابلية القراءة الآلية (Machine Readability)\n"
            "- كثافة الكلمات المفتاحية التخصصية\n"
            "- هيكلة الأقسام والتواريخ القياسية\n"
            "- صياغة الإنجازات القابلة للقياس (Action Verbs & Impact)")

with col_right:
    st.success("✅ **بيانات السيرة الذاتية جاهزة للمعالجة الفورية!**\n"
               "سيتم ربط محرك الـ ATS Scoring المتقدم بنموذج Gemini في التحديث القادم.")

with st.expander("🔍 استعراض المهارات المستخرجة للتحليل", expanded=True):
    skills = profile.skills if hasattr(profile, "skills") else profile.get("skills", [])
    if skills:
        st.write(", ".join([f"`{s}`" for s in skills]))
    else:
        st.write("لا توجد مهارات مسجلة.")
