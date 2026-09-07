import streamlit as st
from utils.state_manager import init_session_state, require_cv_profile

# 1. تهيئة حالة الجلسة
init_session_state()

# 2. إعداد الصفحة
st.set_page_config(
    page_title="لوحة تحكم الجامعات | CareerHub AI",
    page_icon="🏛️",
    layout="wide"
)

# 3. التحقق الإلزامي من وجود السيرة الذاتية
profile = require_cv_profile()

st.title("🏛️ لوحة تحكم الخريجين والجامعات (B2B University Dashboard)")
st.markdown("منظومة تحليلات مخصصة للجامعات ومراكز التطوير المهني لمتابعة جاهزية الطلاب لسوق العمل.")

st.divider()

# ملخص بيانات التعليم للخريج الحالي
st.subheader("🎓 بيانات التعليم الأكاديمي للمرشح")
education_list = profile.get("education", [])
if education_list:
    for edu in education_list:
        st.info(f"🏛️ **الجامعة:** {edu.get('university') or 'غير محدد'} | **الدرجة:** {edu.get('degree') or 'غير محدد'} | **التخصص:** {edu.get('field') or 'غير محدد'} | **سنة التخرج:** {edu.get('year') or 'غير محدد'}")
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
