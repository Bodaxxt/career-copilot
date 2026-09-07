"""
CareerHub AI - تطبيق التوجيه والتوظيف الذكي
Sprint 1: ST-03 Production CV Parser & Manual Fallback System
"""

import json
import streamlit as st
from utils.state_manager import (
    init_session_state,
    get_user_profile,
    set_user_profile,
    get_temp_draft_profile,
    set_temp_draft_profile,
    get_raw_pdf_text,
    set_raw_pdf_text,
    get_parse_status,
    set_parse_status,
    set_demo_mode,
    reset_session,
)
from utils.cv_parser import parse_cv, extract_raw_text_from_pdf

# 1. تهيئة حالة الجلسة
init_session_state()

# 2. إعداد الصفحة
st.set_page_config(
    page_title="CareerHub AI | منصة التوظيف الذكية",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. الشريط الجانبي (Sidebar) ومؤشرات الحالة
with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/briefcase.svg", width=42)
    st.title("CareerHub AI")
    st.caption("الجيل القادم من منصات التوظيف والتحليل المهني.")
    
    st.divider()
    
    # مؤشر حالة السيرة الذاتية
    status = get_parse_status()
    current_profile = get_user_profile()
    
    if status == "success" and current_profile:
        st.success("🟢 السيرة الذاتية معتمدة")
        if st.session_state.get("demo_mode"):
            st.info("🧪 الوضع التجريبي نشط")
        if st.session_state.get("parsed_at"):
            st.caption(f"🕒 تم الاعتماد: {st.session_state['parsed_at']}")
    elif status == "manual_edit":
        st.warning("🟡 قيد التعديل والمراجعة اليدوية")
    else:
        st.error("🔴 بانتظار رفع السيرة الذاتية")
        st.caption("ارفع ملف PDF أو استخدم الوضع التجريبي للبدء.")

    if current_profile or get_temp_draft_profile():
        if st.button("🔄 إعادة ضبط ومسح البيانات", use_container_width=True):
            reset_session()
            st.rerun()

    st.divider()
    st.markdown("### 📌 الخطوات والصفحات المتاحة:")
    st.markdown("1. 📄 **الرئيسية (رفع وتدقيق الـ CV)** `[أنت هنا]`")
    st.markdown("2. 📊 **تقييم الـ ATS** (`pages/1_📊_ATS_Score.py`)")
    st.markdown("3. 🎯 **مطابقة الوظائف (RAG)** (`pages/2_🎯_Job_Matching.py`)")
    st.markdown("4. 💼 **تدقيق LinkedIn** (`pages/3_💼_LinkedIn_Audit.py`)")
    st.markdown("5. 🏛️ **لوحة الجامعات** (`pages/4_🏛️_University_Dashboard.py`)")

# 4. الترويسة الرئيسية (Hero Section)
st.title("🚀 CareerHub AI - مساعدك المهني الذكي")
st.markdown("""
ارفع سيرتك الذاتية لتحليلها بنموذج **Gemini 1.5 Flash** واستخراج بياناتها بدقة بالغة. 
تتيح لك المنصة مراجعة النصوص المستخرجة محلياً، وتعديل أي حقول يدوياً لضمان دقة 100% قبل الانتقال لتقييم الـ ATS والوظائف.
""")

st.divider()

# 5. منطقة رفع الملف والتجربة السريعة
col_upload, col_demo = st.columns([2, 1])

with col_upload:
    st.markdown("### 📄 خطوة 1: رفع السيرة الذاتية (PDF)")
    uploaded_file = st.file_uploader(
        "اختر ملف السيرة الذاتية (PDF فقط - الحد الأقصى 10MB)",
        type=["pdf"],
        help="سيتم استخراج النص محلياً وإرساله للتحليل الذكي عبر Gemini API."
    )

    if uploaded_file is not None:
        # فحص الحجم المباشر
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 10.0:
            st.error(f"❌ حجم الملف ({file_size_mb:.2f} MB) يتجاوز الحد المسموح به (10 MB).")
        elif uploaded_file.size == 0:
            st.error("❌ الملف المرفوع فارغ (0 بايت).")
        else:
            if st.button("⚡ بدء استخراج وتحليل السيرة الذاتية بالذكاء الاصطناعي", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري تحليل السيرة الذاتية واستخراج المهارات والخبرات بالذكاء الاصطناعي..."):
                    parsed_dict, raw_text, error_msg = parse_cv(uploaded_file)
                    
                    # حفظ النص الخام المستخرج محلياً في كل الأحوال
                    if raw_text:
                        set_raw_pdf_text(raw_text)

                    if parsed_dict:
                        set_temp_draft_profile(parsed_dict)
                        set_user_profile(parsed_dict, demo_mode=False, show_toast=True)
                        st.rerun()
                    else:
                        # في حالة فشل الـ AI ولكن النص الخام متوفر -> فتح محرر التعديل اليدوي مباشرة
                        st.error(f"⚠️ {error_msg}")
                        if raw_text:
                            st.info("💡 تم استخراج النص محلياً بنجاح! تم تفعيل وضع التعديل اليدوي حتى تتمكن من إدخال البيانات مباشرة.")
                            fallback_template = {
                                "full_name": "",
                                "headline": "",
                                "summary": "",
                                "skills": [],
                                "experiences": [],
                                "education": [],
                                "projects": []
                            }
                            set_temp_draft_profile(fallback_template)
                            set_parse_status("manual_edit")
                            st.rerun()

with col_demo:
    st.markdown("### ⚡ تجربة فورية")
    st.info("تريد تجربة المنصة ومميزات الـ ATS والوظائف فوراً دون رفع ملف؟")
    if st.button("⚡ تجربة سريعة بسيرة ذاتية جاهزة (Demo CV)", use_container_width=True):
        set_demo_mode()
        st.rerun()

st.divider()

# 6. مساحة العمل التفاعلية (Tabs: التعديل اليدوي / المعاينة / النصوص والـ JSON)
draft_profile = get_temp_draft_profile() or get_user_profile()

if draft_profile is not None:
    st.markdown("### 🛠️ خطوة 2: مراجعة وتدقيق واعتماد البيانات")
    
    tab_edit, tab_preview, tab_raw = st.tabs([
        "📝 محرر البيانات والتدقيق اليدوي (Manual Editor)",
        "👁️ بطاقة الملف المهني المعتمد (Live Profile Card)",
        "📄 النص المستخرج الخام و JSON (Raw Text & Export)"
    ])

    # ------------------ Tab 1: محرر البيانات ------------------
    with tab_edit:
        st.markdown("#### ✏️ تدقيق البيانات المستخرجة:")
        st.caption("يمكنك تعديل أي معلومة أخطأ الذكاء الاصطناعي في تفسيرها ثم الضغط على **اعتماد السيرة الذاتية**.")
        
        with st.form(key="manual_cv_editor_form"):
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                edit_name = st.text_input("👤 الاسم الكامل (Full Name):", value=draft_profile.get("full_name") or "")
            with col_b2:
                edit_headline = st.text_input("💼 المسمى المهني (Headline):", value=draft_profile.get("headline") or "")
            
            edit_summary = st.text_area("📝 نبذة وملخص مهني (Summary):", value=draft_profile.get("summary") or "", height=100)

            # المهارات
            current_skills_str = ", ".join(draft_profile.get("skills", []))
            edit_skills_input = st.text_area(
                "🛠️ المهارات التقنية (مفصولة بفواصل ','):",
                value=current_skills_str,
                help="أدخل المهارات مفصولة بفواصل مثل: Python, FastAPI, Docker, SQL",
                height=80
            )

            st.markdown("---")
            st.markdown("##### 💼 الخبرات المهنية (Experiences)")
            experiences_list = draft_profile.get("experiences", [])
            
            # محرر مبسط ومرن للخبرات
            exp_text_blocks = []
            for i, exp in enumerate(experiences_list):
                with st.expander(f"📌 خبرة {i+1}: {exp.get('title') or 'مسمى'} في {exp.get('company') or 'شركة'}", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        c_title = st.text_input(f"المسمى الوظيفي #{i+1}:", value=exp.get("title") or "", key=f"exp_title_{i}")
                        c_comp = st.text_input(f"اسم الشركة #{i+1}:", value=exp.get("company") or "", key=f"exp_comp_{i}")
                    with c2:
                        c_period = st.text_input(f"الفترة الزمنية #{i+1}:", value=exp.get("period") or "", key=f"exp_period_{i}")
                    
                    ach_str = "\n".join(exp.get("achievements", []))
                    c_ach = st.text_area(f"الإنجازات والمهام #{i+1} (سطر لكل إنجاز):", value=ach_str, key=f"exp_ach_{i}", height=90)
                    
                    ach_list = [a.strip() for a in c_ach.split("\n") if a.strip()]
                    exp_text_blocks.append({
                        "title": c_title or None,
                        "company": c_comp or None,
                        "period": c_period or None,
                        "achievements": ach_list
                    })

            st.markdown("---")
            st.markdown("##### 🎓 المؤهلات التعليمية (Education)")
            edu_list = draft_profile.get("education", [])
            edu_text_blocks = []
            for j, edu in enumerate(edu_list):
                with st.expander(f"🎓 مؤهل {j+1}: {edu.get('degree') or ''} - {edu.get('university') or ''}", expanded=False):
                    e1, e2 = st.columns(2)
                    with e1:
                        e_uni = st.text_input(f"الجامعة / المؤسسة #{j+1}:", value=edu.get("university") or "", key=f"edu_uni_{j}")
                        e_deg = st.text_input(f"الدرجة العلمية #{j+1}:", value=edu.get("degree") or "", key=f"edu_deg_{j}")
                    with e2:
                        e_field = st.text_input(f"التخصص #{j+1}:", value=edu.get("field") or "", key=f"edu_field_{j}")
                        e_year = st.text_input(f"سنة التخرج #{j+1}:", value=edu.get("year") or "", key=f"edu_year_{j}")
                    
                    edu_text_blocks.append({
                        "university": e_uni or None,
                        "degree": e_deg or None,
                        "field": e_field or None,
                        "year": e_year or None
                    })

            st.markdown("---")
            st.markdown("##### 🚀 المشاريع (Projects)")
            proj_list = draft_profile.get("projects", [])
            proj_text_blocks = []
            for k, proj in enumerate(proj_list):
                with st.expander(f"🚀 مشروع {k+1}: {proj.get('name') or 'مشروع'}", expanded=False):
                    p_name = st.text_input(f"اسم المشروع #{k+1}:", value=proj.get("name") or "", key=f"proj_name_{k}")
                    p_tech_str = ", ".join(proj.get("technologies", []))
                    p_tech = st.text_input(f"التقنيات المستخدمة #{k+1}:", value=p_tech_str, key=f"proj_tech_{k}")
                    p_desc = st.text_area(f"وصف المشروع #{k+1}:", value=proj.get("description") or "", key=f"proj_desc_{k}")
                    
                    tech_list = [t.strip() for t in p_tech.split(",") if t.strip()]
                    proj_text_blocks.append({
                        "name": p_name or None,
                        "technologies": tech_list,
                        "description": p_desc or None
                    })

            submitted = st.form_submit_button("💾 حفظ التعديلات واعتماد السيرة الذاتية", type="primary", use_container_width=True)
            if submitted:
                # معالجة المهارات (تجريد وتنسيق بدون تكرار)
                formatted_skills = []
                for s in edit_skills_input.split(","):
                    clean_s = s.strip()
                    if clean_s and clean_s not in formatted_skills:
                        formatted_skills.append(clean_s.capitalize() if clean_s.isascii() else clean_s)

                updated_profile = {
                    "full_name": edit_name.strip() or None,
                    "headline": edit_headline.strip() or None,
                    "summary": edit_summary.strip() or None,
                    "skills": formatted_skills,
                    "experiences": exp_text_blocks if exp_text_blocks else experiences_list,
                    "education": edu_text_blocks if edu_text_blocks else edu_list,
                    "projects": proj_text_blocks if proj_text_blocks else proj_list
                }

                set_user_profile(updated_profile, demo_mode=False, show_toast=True)
                st.rerun()

    # ------------------ Tab 2: المعاينة الحية ------------------
    with tab_preview:
        confirmed_profile = get_user_profile() or draft_profile
        st.subheader("✨ بطاقة المعاينة الحية للملف المهني (Live Profile Card)")
        
        c_p1, c_p2, c_p3 = st.columns([1.5, 2, 1.5])
        with c_p1:
            st.markdown(f"### 👤 {confirmed_profile.get('full_name') or 'غير محدد'}")
            st.markdown(f"**💼 المسمى:** `{confirmed_profile.get('headline') or 'غير محدد'}`")
            if confirmed_profile.get('summary'):
                st.info(f"📝 **نبذة:** {confirmed_profile.get('summary')}")
        
        with c_p2:
            st.markdown("#### 🛠️ المهارات المستخرجة:")
            skills = confirmed_profile.get("skills", [])
            if skills:
                st.write(" ".join([f"`{s}`" for s in skills]))
            else:
                st.write("لا توجد مهارات مسجلة.")
        
        with c_p3:
            st.markdown("#### 📊 ملخص الملف:")
            st.metric("عدد الخبرات", len(confirmed_profile.get("experiences", [])))
            st.metric("عدد المشاريع", len(confirmed_profile.get("projects", [])))
            st.metric("المؤهلات التعليمية", len(confirmed_profile.get("education", [])))

        st.divider()
        
        col_exp_view, col_proj_view = st.columns(2)
        with col_exp_view:
            st.markdown("#### 💼 الخبرات المهنية:")
            for exp in confirmed_profile.get("experiences", []):
                st.markdown(f"**{exp.get('title')}** في *{exp.get('company')}* ({exp.get('period')})")
                for ach in exp.get("achievements", []):
                    st.write(f"- {ach}")
        
        with col_proj_view:
            st.markdown("#### 🚀 المشاريع:")
            for proj in confirmed_profile.get("projects", []):
                st.markdown(f"**{proj.get('name')}**")
                if proj.get("technologies"):
                    st.caption(f"التقنيات: {', '.join(proj.get('technologies', []))}")
                if proj.get("description"):
                    st.write(proj.get("description"))

    # ------------------ Tab 3: النص الخام والـ JSON ------------------
    with tab_raw:
        st.subheader("📄 البيانات الخام و التصدير")
        
        raw_text_content = get_raw_pdf_text()
        col_raw1, col_raw2 = st.columns(2)
        
        with col_raw1:
            st.markdown("##### 📝 النص المستخرج محلياً من ملف الـ PDF:")
            if raw_text_content:
                st.text_area("محتوى النص الخام المستخرج:", value=raw_text_content, height=350)
            else:
                st.info("لا يتوفر نص خام مستخرج للملف الحالي.")
        
        with col_raw2:
            st.markdown("##### 📦 كائن الـ JSON المستخرج والمحدث:")
            json_str = json.dumps(draft_profile, ensure_ascii=False, indent=2)
            st.code(json_str, language="json")
            st.download_button(
                label="💾 تحميل البيانات بتنسيق JSON",
                data=json_str,
                file_name="careerhub_profile.json",
                mime="application/json",
                use_container_width=True
            )
else:
    st.info("💡 قم برفع ملف السيرة الذاتية أعلاه أو اضغط على **⚡ تجربة سريعة بسيرة ذاتية جاهزة** لعرض ومراجعة كافة البيانات هنا.")
