"""
CareerHub AI - تطبيق التوجيه والتوظيف الذكي
Sprint 1: ST-04 Profile Object & Comprehensive Skill Normalizer
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
from utils.cv_parser import parse_cv
from utils.skill_normalizer import normalize_skills
from utils.models import UserProfile

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
        norm_count = st.session_state.get("normalized_skills_count", len(current_profile.skills))
        st.metric("🛠️ المهارات الموحدة", f"{norm_count} مهارة")
        
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
ارفع سيرتك الذاتية لاستخراجها بنموذج **Gemini 1.5 Flash** وهيكلتها بنماذج **Pydantic v2** الصارمة. 
يقوم النظام تلقائياً بتنقية وتوحيد أكثر من **150+ مهارة تقنية (Skill Normalization)** لضمان أعلى توافق مع أنظمة الـ ATS والبحث الدلالي.
""")

st.divider()

# 5. منطقة رفع الملف والتجربة السريعة
col_upload, col_demo = st.columns([2, 1])

with col_upload:
    st.markdown("### 📄 خطوة 1: رفع السيرة الذاتية (PDF)")
    uploaded_file = st.file_uploader(
        "اختر ملف السيرة الذاتية (PDF فقط - الحد الأقصى 10MB)",
        type=["pdf"],
        help="سيتم استخراج النص محلياً وإرساله للتحليل الذكي عبر Gemini API وتوحيد المهارات."
    )

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 10.0:
            st.error(f"❌ حجم الملف ({file_size_mb:.2f} MB) يتجاوز الحد المسموح به (10 MB).")
        elif uploaded_file.size == 0:
            st.error("❌ الملف المرفوع فارغ (0 بايت).")
        else:
            if st.button("⚡ بدء استخراج وتحليل وتوحيد السيرة الذاتية", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري تحليل السيرة الذاتية واستخراج وتوحيد المهارات بالذكاء الاصطناعي..."):
                    parsed_dict, raw_text, error_msg = parse_cv(uploaded_file)
                    
                    if raw_text:
                        set_raw_pdf_text(raw_text)

                    if parsed_dict:
                        # توحيد واعتماد السيرة الذاتية مباشرة
                        set_user_profile(parsed_dict, demo_mode=False, show_toast=True)
                        st.rerun()
                    else:
                        st.error(f"⚠️ {error_msg}")
                        if raw_text:
                            st.info("💡 تم استخراج النص محلياً بنجاح! تم تفعيل وضع التعديل اليدوي.")
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
    st.info("تريد تجربة المنصة ومحرك توحيد المهارات ومميزات الـ ATS والوظائف فوراً؟")
    if st.button("⚡ تجربة سريعة بسيرة ذاتية جاهزة (Demo CV)", use_container_width=True):
        set_demo_mode()
        st.rerun()

st.divider()

# 6. مساحة العمل التفاعلية (Tabs: التعديل اليدوي / المعاينة / النصوص والـ JSON)
raw_draft = get_temp_draft_profile() or (get_user_profile().to_dict() if get_user_profile() else None)

if raw_draft is not None:
    st.markdown("### 🛠️ خطوة 2: مراجعة وتدقيق وتوحيد البيانات")
    
    tab_edit, tab_preview, tab_raw = st.tabs([
        "📝 محرر البيانات وتوحيد المهارات (Manual Editor & Normalizer)",
        "👁️ بطاقة الملف المهني المعتمد (Live Profile Card)",
        "📄 النص المستخرج الخام و JSON (Raw Text & Export)"
    ])

    # ------------------ Tab 1: محرر البيانات وتوحيد المهارات ------------------
    with tab_edit:
        st.markdown("#### ✏️ تدقيق البيانات المستخرجة:")
        st.caption("أي مهارة تدخلها مثل `reactjs` أو `k8s` أو `python3` سيتم تحويلها وتوحيدها آلياً إلى الصيغة القياسية المعيارية.")
        
        with st.form(key="manual_cv_editor_form"):
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                edit_name = st.text_input("👤 الاسم الكامل (Full Name):", value=raw_draft.get("full_name") or "")
            with col_b2:
                edit_headline = st.text_input("💼 المسمى المهني (Headline):", value=raw_draft.get("headline") or "")
            
            edit_summary = st.text_area("📝 نبذة وملخص مهني (Summary):", value=raw_draft.get("summary") or "", height=100)

            # المهارات
            current_skills = raw_draft.get("skills", [])
            current_skills_str = ", ".join(current_skills) if isinstance(current_skills, list) else str(current_skills)
            
            edit_skills_input = st.text_area(
                "🛠️ المهارات التقنية (أدخلها مفصولة بفواصل ',' - سيتم توحيدها وتنسيقها آلياً):",
                value=current_skills_str,
                help="مثال: python3, k8s, docker, reactjs, postgres, fast api, custom_skill",
                height=80
            )

            st.markdown("---")
            st.markdown("##### 💼 الخبرات المهنية (Experiences)")
            experiences_list = raw_draft.get("experiences", [])
            exp_text_blocks = []
            for i, exp in enumerate(experiences_list):
                if isinstance(exp, dict):
                    e_title = exp.get("title") or ""
                    e_comp = exp.get("company") or ""
                    e_period = exp.get("period") or ""
                    e_ach = exp.get("achievements") or []
                else:
                    e_title = getattr(exp, "title", "") or ""
                    e_comp = getattr(exp, "company", "") or ""
                    e_period = getattr(exp, "period", "") or ""
                    e_ach = getattr(exp, "achievements", []) or []

                with st.expander(f"📌 خبرة {i+1}: {e_title or 'مسمى'} في {e_comp or 'شركة'}", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        c_title = st.text_input(f"المسمى الوظيفي #{i+1}:", value=e_title, key=f"exp_title_{i}")
                        c_comp = st.text_input(f"اسم الشركة #{i+1}:", value=e_comp, key=f"exp_comp_{i}")
                    with c2:
                        c_period = st.text_input(f"الفترة الزمنية #{i+1}:", value=e_period, key=f"exp_period_{i}")
                    
                    ach_str = "\n".join(e_ach) if isinstance(e_ach, list) else str(e_ach)
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
            edu_list = raw_draft.get("education", [])
            edu_text_blocks = []
            for j, edu in enumerate(edu_list):
                if isinstance(edu, dict):
                    edu_u = edu.get("university") or ""
                    edu_d = edu.get("degree") or ""
                    edu_f = edu.get("field") or ""
                    edu_y = edu.get("year") or ""
                else:
                    edu_u = getattr(edu, "university", "") or ""
                    edu_d = getattr(edu, "degree", "") or ""
                    edu_f = getattr(edu, "field", "") or ""
                    edu_y = getattr(edu, "year", "") or ""

                with st.expander(f"🎓 مؤهل {j+1}: {edu_d} - {edu_u}", expanded=False):
                    e1, e2 = st.columns(2)
                    with e1:
                        e_uni = st.text_input(f"الجامعة / المؤسسة #{j+1}:", value=edu_u, key=f"edu_uni_{j}")
                        e_deg = st.text_input(f"الدرجة العلمية #{j+1}:", value=edu_d, key=f"edu_deg_{j}")
                    with e2:
                        e_field = st.text_input(f"التخصص #{j+1}:", value=edu_f, key=f"edu_field_{j}")
                        e_year = st.text_input(f"سنة التخرج #{j+1}:", value=edu_y, key=f"edu_year_{j}")
                    
                    edu_text_blocks.append({
                        "university": e_uni or None,
                        "degree": e_deg or None,
                        "field": e_field or None,
                        "year": e_year or None
                    })

            st.markdown("---")
            st.markdown("##### 🚀 المشاريع (Projects)")
            proj_list = raw_draft.get("projects", [])
            proj_text_blocks = []
            for k, proj in enumerate(proj_list):
                if isinstance(proj, dict):
                    p_n = proj.get("name") or ""
                    p_t = proj.get("technologies") or []
                    p_d = proj.get("description") or ""
                else:
                    p_n = getattr(proj, "name", "") or ""
                    p_t = getattr(proj, "technologies", []) or []
                    p_d = getattr(proj, "description", "") or ""

                with st.expander(f"🚀 مشروع {k+1}: {p_n or 'مشروع'}", expanded=False):
                    p_name = st.text_input(f"اسم المشروع #{k+1}:", value=p_n, key=f"proj_name_{k}")
                    p_tech_str = ", ".join(p_t) if isinstance(p_t, list) else str(p_t)
                    p_tech = st.text_input(f"التقنيات المستخدمة #{k+1}:", value=p_tech_str, key=f"proj_tech_{k}")
                    p_desc = st.text_area(f"وصف المشروع #{k+1}:", value=p_d, key=f"proj_desc_{k}")
                    
                    tech_raw = [t.strip() for t in p_tech.split(",") if t.strip()]
                    proj_text_blocks.append({
                        "name": p_name or None,
                        "technologies": normalize_skills(tech_raw),
                        "description": p_desc or None
                    })

            submitted = st.form_submit_button("💾 حفظ التعديلات واعتماد السيرة الذاتية وتوحيد المهارات", type="primary", use_container_width=True)
            if submitted:
                # استخراج وتوحيد المهارات
                raw_input_skills = [s.strip() for s in edit_skills_input.split(",") if s.strip()]
                normalized_skills_result = normalize_skills(raw_input_skills)

                updated_dict = {
                    "full_name": edit_name.strip() or None,
                    "headline": edit_headline.strip() or None,
                    "summary": edit_summary.strip() or None,
                    "skills": normalized_skills_result,
                    "experiences": exp_text_blocks if exp_text_blocks else experiences_list,
                    "education": edu_text_blocks if edu_text_blocks else edu_list,
                    "projects": proj_text_blocks if proj_text_blocks else proj_list
                }

                set_user_profile(updated_dict, demo_mode=False, show_toast=True)
                st.rerun()

    # ------------------ Tab 2: المعاينة الحية ------------------
    with tab_preview:
        active_user_profile = get_user_profile()
        if active_user_profile:
            st.subheader("✨ بطاقة المعاينة الحية للملف المهني (Live Profile Card)")
            
            c_p1, c_p2, c_p3 = st.columns([1.5, 2, 1.5])
            with c_p1:
                st.markdown(f"### 👤 {active_user_profile.full_name or 'غير محدد'}")
                st.markdown(f"**💼 المسمى:** `{active_user_profile.headline or 'غير محدد'}`")
                if active_user_profile.summary:
                    st.info(f"📝 **نبذة:** {active_user_profile.summary}")
            
            with c_p2:
                st.markdown("#### 🛠️ المهارات التقنية الموحدة (Normalized Skills):")
                skills_list = active_user_profile.skills
                if skills_list:
                    st.write(" ".join([f"`{s}`" for s in skills_list]))
                    st.caption(f"✨ تم توحيد وتنقية إجمالي **{len(skills_list)}** مهارة بنجاح.")
                else:
                    st.write("لا توجد مهارات مسجلة.")
            
            with c_p3:
                st.markdown("#### 📊 إحصائيات الملف:")
                st.metric("عدد المهارات الموحدة", len(active_user_profile.skills))
                st.metric("عدد الخبرات", len(active_user_profile.experiences))
                st.metric("عدد المشاريع", len(active_user_profile.projects))

            st.divider()
            
            col_exp_view, col_proj_view = st.columns(2)
            with col_exp_view:
                st.markdown("#### 💼 الخبرات المهنية:")
                for exp in active_user_profile.experiences:
                    st.markdown(f"**{exp.title or 'مسمى'}** في *{exp.company or 'شركة'}* ({exp.period or 'فترة'})")
                    for ach in exp.achievements:
                        st.write(f"- {ach}")
            
            with col_proj_view:
                st.markdown("#### 🚀 المشاريع التقنية:")
                for proj in active_user_profile.projects:
                    st.markdown(f"**{proj.name or 'مشروع'}**")
                    if proj.technologies:
                        st.caption(f"التقنيات الموحدة: {', '.join(proj.technologies)}")
                    if proj.description:
                        st.write(proj.description)

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
            st.markdown("##### 📦 كائن الـ JSON المهيكل (Pydantic Schema):")
            active_profile_obj = get_user_profile()
            json_str = active_profile_obj.to_json(indent=2) if active_profile_obj else json.dumps(raw_draft, ensure_ascii=False, indent=2)
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
