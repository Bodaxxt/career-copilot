import json
import streamlit as st
from utils.state_manager import (
    init_session_state,
    get_user_profile,
    set_user_profile,
    set_demo_mode,
    reset_session,
)
from utils.cv_parser import parse_cv

# 1. تهيئة حالة الجلسة عند بداية التشغيل
init_session_state()

# 2. إعداد الصفحة
st.set_page_config(
    page_title="CareerHub AI | منصة التوجيه والتوظيف الذكية",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. الشريط الجانبي (Sidebar) ومؤشر الحالة
with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/briefcase.svg", width=48)
    st.title("CareerHub AI")
    st.caption("الجيل القادم من منصات التوظيف والتوجيه المهني الذكية.")
    
    st.divider()
    
    # مؤشر حالة السيرة الذاتية
    current_profile = get_user_profile()
    if current_profile:
        st.success("🟢 السيرة الذاتية محملة")
        if st.session_state.get("demo_mode"):
            st.info("ℹ️ أنت في الوضع التجريبي (Demo Mode)")
        if st.session_state.get("parsed_at"):
            st.caption(f"🕒 وقت التحليل: {st.session_state['parsed_at']}")
        
        if st.button("🔄 إعادة ضبط الجلسة", use_container_width=True):
            reset_session()
            st.rerun()
    else:
        st.error("🔴 بانتظار رفع الـ CV")
        st.caption("ارفع ملف PDF أو فعّل الوضع التجريبي للبدء.")

    st.divider()
    st.markdown("### 📌 الصفحات المتاحة:")
    st.markdown("- 📊 **تقييم ATS**")
    st.markdown("- 🎯 **مطابقة الوظائف**")
    st.markdown("- 💼 **تدقيق LinkedIn**")
    st.markdown("- 🏛️ **لوحة الجامعات**")

# 4. واجهة الصفحة الرئيسية (Hero Section)
st.title("🚀 مرحباً بك في CareerHub AI")
st.subheader("منصتك المتكاملة لتطوير السيرة الذاتية، ومطابقة الفرص الوظيفية بالذكاء الاصطناعي")
st.markdown("""
ارفع سيرتك الذاتية بصيغة **PDF** لاستخراج كافة البيانات بدقة، ثم انتقل إلى الصفحات المتخصصة لفحص توافق **ATS**، مطابقة الوظائف بنظام **RAG**، وتحسين ملف **LinkedIn**.
""")

st.divider()

# 5. منطقة رفع السيرة الذاتية وأزرار التفاعل السريع
col_upload, col_demo = st.columns([2, 1])

with col_upload:
    st.markdown("### 📄 رفع السيرة الذاتية (PDF)")
    uploaded_file = st.file_uploader(
        "اختر ملف السيرة الذاتية (الحد الأقصى 10MB)",
        type=["pdf"],
        help="يتم تحليل الملف محلياً باستخدام Gemini API بنظام استخراج JSON الصافي"
    )

    if uploaded_file is not None:
        if st.button("⚡ استخراج وتحليل السيرة الذاتية", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري قراءة وتحليل السيرة الذاتية عبر الذكاء الاصطناعي..."):
                parsed_data = parse_cv(uploaded_file)
                if parsed_data:
                    set_user_profile(parsed_data, demo_mode=False)
                    st.success("✅ تم استخراج بيانات السيرة الذاتية بنجاح وحفظها في الجلسة!")
                    st.rerun()

with col_demo:
    st.markdown("### 🧪 تجربة سريعة")
    st.info("ليس لديك ملف جاهز الآن؟ يمكنك تفعيل **الوضع التجريبي** فوراً لتجربة كامل مميزات التطبيق ببيانات واقعية.")
    if st.button("🚀 تحميل ملف تجريبي (Demo Mode)", use_container_width=True):
        set_demo_mode()
        st.success("✅ تم تفعيل الوضع التجريبي بنجاح!")
        st.rerun()

st.divider()

# 6. بطاقة المعاينة الحية (Live Preview Card)
active_profile = get_user_profile()

if active_profile:
    st.subheader("✨ بطاقة المعاينة الحية للملف المهني (Live Profile Card)")
    
    col_card1, col_card2, col_card3 = st.columns([1.5, 2, 1.5])
    
    with col_card1:
        st.markdown(f"### 👤 {active_profile.get('full_name') or 'الاسم غير محدد'}")
        st.markdown(f"**💼 المسمى:** {active_profile.get('headline') or 'غير محدد'}")
        if active_profile.get('summary'):
            st.caption(f"📝 {active_profile.get('summary')}")
            
    with col_card2:
        st.markdown("#### 🛠️ المهارات التقنية المستخرجة:")
        skills = active_profile.get("skills", [])
        if skills:
            st.write(", ".join([f"`{s}`" for s in skills]))
        else:
            st.write("لا توجد مهارات مسجلة.")
            
    with col_card3:
        st.markdown("#### 📊 الإحصائيات:")
        st.metric("الخبرات المهنية", len(active_profile.get("experiences", [])))
        st.metric("المشاريع المنجزة", len(active_profile.get("projects", [])))
        st.metric("المؤهلات التعليمية", len(active_profile.get("education", [])))

    st.markdown("---")
    with st.expander("🔍 استعراض كائن الـ JSON المستخرج بالكامل", expanded=False):
        st.json(active_profile)
        st.download_button(
            label="💾 تحميل البيانات بتنسيق JSON",
            data=json.dumps(active_profile, ensure_ascii=False, indent=2),
            file_name="careerhub_profile.json",
            mime="application/json"
        )
else:
    st.info("💡 بمجرد رفع ملف السيرة الذاتية أو الضغط على **تحميل ملف تجريبي**، ستظهر بطاقة بياناتك هنا وستتمكن من الانتقال للصفحات الأخرى.")
