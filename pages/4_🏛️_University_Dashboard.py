import streamlit as st
from utils.state_manager import init_session_state, require_cv_profile, render_auth_sidebar

# 1. تهيئة حالة الجلسة
init_session_state()

# 2. إعداد الصفحة
st.set_page_config(
    page_title="لوحة تحكم الجامعات | CareerHub AI",
    page_icon="🏛️",
    layout="wide"
)

# 3. عرض مصادقة الشريط الجانبي والتحقق الإلزامي من وجود السيرة الذاتية
render_auth_sidebar()
profile = require_cv_profile()

st.title("🏛️ لوحة تحكم الخريجين والجامعات (B2B University Dashboard)")
st.markdown("منظومة تحليلات مخصصة للجامعات ومراكز التطوير المهني لمتابعة جاهزية الطلاب لسوق العمل.")

st.divider()

# ملخص بيانات التعليم للخريج الحالي
st.subheader("🎓 بيانات التعليم الأكاديمي للمرشح")
education_list = profile.education if hasattr(profile, "education") else profile.get("education", [])
if education_list:
    for edu in education_list:
        u = edu.university if hasattr(edu, "university") else edu.get("university")
        d = edu.degree if hasattr(edu, "degree") else edu.get("degree")
        f = edu.field if hasattr(edu, "field") else edu.get("field")
        y = edu.year if hasattr(edu, "year") else edu.get("year")
        st.info(f"🏛️ **الجامعة:** {u or 'غير محدد'} | **الدرجة:** {d or 'غير محدد'} | **التخصص:** {f or 'غير محدد'} | **سنة التخرج:** {y or 'غير محدد'}")
else:
    st.write("لا توجد بيانات تعليم مسجلة.")

st.divider()

st.subheader("📈 مؤشرات قياس أداء الدفعة (Cohort Readiness Metrics - قيد التطوير)")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.metric("معدل جاهزية الطلاب", "84%", "+5%")
with col_stat2:
    st.metric("أكثر مهارة مطلوبة", "Python / AI", "High Demand")
with col_stat3:
    st.metric("نسبة اجتياز الـ ATS", "78%", "+12%")
with col_stat4:
    st.metric("الشركات المستهدفة", "45 شركة", "Active")

st.caption("🚀 سيتم دعم رفع دفعات جماعية من السير الذاتية (Batch Processing) في الإصدار القادم.")
