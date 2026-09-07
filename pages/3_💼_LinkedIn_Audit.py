import streamlit as st
from utils.state_manager import init_session_state, require_cv_profile, render_auth_sidebar

# 1. تهيئة حالة الجلسة
init_session_state()

# 2. إعداد الصفحة
st.set_page_config(
    page_title="تدقيق LinkedIn | CareerHub AI",
    page_icon="💼",
    layout="wide"
)

# 3. عرض مصادقة الشريط الجانبي والتحقق الإلزامي من وجود السيرة الذاتية
render_auth_sidebar()
profile = require_cv_profile()

st.title("💼 مدقق ومطور الملف الشخصي على LinkedIn")
st.markdown("تحسين العنوان، الملخص المهني، والكلمات المفتاحية لجذب مسؤولي التوظيف على LinkedIn.")

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 العنوان والملخص المقترح (Headline & About)")
    st.text_input("العنوان الحالي في السيرة الذاتية:", value=profile.get("headline") or "")
    st.text_area("الملخص المهني الحالي:", value=profile.get("summary") or "", height=120)
    
    if st.button("✨ توليد مقترحات تحسين مدعومة بالذكاء الاصطناعي", type="primary"):
        st.info("💡 سيتم ربط ميزة إعادة الصياغة الاحترافية (Prompt Enhancement) في Sprint 2.")

with col2:
    st.subheader("🌟 أفضل الممارسات لملفك على LinkedIn")
    st.markdown("""
    - **Headline قوي:** اذكر مسمى وظيفي واضح + أدوات تخصصية + القيمة المضافة.
    - **قسم About جذاب:** ابدأ بهوك سريع، ركز على الإنجازات بالأرقام.
    - **قسم Featured:** أضف روابط مشاريعك وشهاداتك المعتمدة.
    """)

with st.expander("🚀 المشاريع المتاحة لإبرازها في LinkedIn"):
    projects = profile.projects if hasattr(profile, "projects") else profile.get("projects", [])
    if projects:
        for proj in projects:
            n = proj.name if hasattr(proj, "name") else proj.get("name")
            t = proj.technologies if hasattr(proj, "technologies") else proj.get("technologies", [])
            d = proj.description if hasattr(proj, "description") else proj.get("description")
            st.markdown(f"**{n}**")
            st.write(f"- التقنيات: {', '.join(t)}")
            st.write(f"- الوصف: {d}")
    else:
        st.write("لا توجد مشاريع مسجلة.")
