# 🚀 CareerHub AI (Career Copilot)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.7%2B-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Auth%20%26%20Postgres-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini%20API-1.5%20Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![CI Status](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20Smoke%20Test-green?style=for-the-badge&logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

**المنصة الذكية المتكاملة لتطوير السير الذاتية، اجتياز أنظمة الـ ATS، مطابقة الوظائف بتقنيات RAG، وتدقيق ملفات LinkedIn مع دعم التخزين السحابي الآمن عبر Supabase.**

[تجربة المنصة](#-التشغيل-السريع-محليا-quickstart) • [المميزات الرئيسية](#-المميزات-الرئيسية-key-features) • [الهيكلية البرمجية](#-هيكلية-المشروع-project-architecture) • [إعداد Supabase](#-إعداد-قاعدة-بيانات-supabase) • [النشر السحابي](#-النشر-على-streamlit-cloud)

</div>

---

## 🌟 نظرة عامة (Overview)

**CareerHub AI** (المعروف بـ **Career Copilot**) هو مساعد ذكي متكامل مصمم للباحثين عن عمل والمهنيين والجامعات. يعتمد التطبيق على أحدث نماذج الذكاء الاصطناعي من **Google Gemini** ونماذج **Pydantic v2** الصارمة لاستخراج وتحليل وتوحيد بيانات السير الذاتية (PDF)، مع محرك **Skill Normalizer** يحتوي على أكثر من **150+ مهارة قياسية** معتمدة، وتكامل سحابي كامل مع **Supabase Auth & PostgreSQL** لحفظ واسترجاع السيرة الذاتية عبر الحسابات مع دعم وضع الزائر التلقائي (Resilient Guest Fallback).

---

## ✨ المميزات الرئيسية (Key Features)

| الميزة | الوصف | الحالة |
|---|---|---|
| 📄 **استخراج الـ CV الذكي** | قراءة وتحليل ملفات الـ PDF واستخراج مصفوفة بيانات مهيكلة عبر Gemini Flash و pypdf | ✅ مكتمل (ST-01 / ST-03) |
| 🛡️ **إدارة الجلسات والزائر** | إدارة مركزية للجلسة ومنع أخطاء `KeyError` والعمل السلس بوضع الزائر (Guest Mode) | ✅ مكتمل (ST-02 / ST-05) |
| ☁️ **المصادقة والتخزين السحابي** | تسجيل الدخول والمزامنة السحابية للسيرة الذاتية مع PostgreSQL عبر Supabase Auth | ✅ مكتمل (ST-05) |
| 🛠️ **توحيد المهارات (Skill Normalizer)** | محرك ذكي لتوحيد أكثر من 150+ مهارة برمجية وتنقية المترادفات والصيغ المختلفة | ✅ مكتمل (ST-04) |
| 📐 **نماذج Pydantic v2 الصارمة** | كائنات بيانات منضبطة (`UserProfile`, `Experience`, `Education`, `Project`) | ✅ مكتمل (ST-04) |
| 📝 **محرر التدقيق اليدوي** | إمكانية تعديل وتصحيح الحقول يدوياً مع استخراج النص المحلي عند انقطاع الـ API | ✅ مكتمل (ST-03) |
| 🧪 **الوضع التجريبي (Demo Mode)** | تجربة كامل مميزات التطبيق بنقرة زر دون الحاجة لرفع سيرة ذاتية فوراً | ✅ مكتمل (ST-02) |
| 📊 **تقييم ومطابقة الـ ATS** | فحص قابلية القراءة الآلية، كثافة الكلمات المفتاحية، ومعايير القبول | 🚧 جاهز للربط (Sprint 2) |
| 🎯 **مطابقة الوظائف (RAG Engine)** | مقارنة متطلبات الوصف الوظيفي مع خبرات المرشح واكتشاف الفجوات | 🚧 جاهز للربط (Sprint 2) |
| 💼 **تدقيق وتحسين LinkedIn** | اقتراح عناوين جذابة وملخصات مهنية تزيد من ظهور الملف في البحث | 🚧 جاهز للربط (Sprint 2) |
| 🏛️ **لوحة تحكم الجامعات (B2B)** | تقارير ومؤشرات لقياس جاهزية دفعات الطلاب والخريجين لسوق العمل | 🚧 قيد التطوير |

---

## 🏗️ هيكلية المشروع (Project Architecture)

```text
career-copilot/
├── .github/
│   └── workflows/
│       └── ci.yml                     # فحص الكود التلقائي و Smoke Test عبر GitHub Actions
├── .streamlit/
│   ├── config.toml                   # إعدادات الثيم الداكن والخادم
│   └── secrets.toml.example          # قالب مفاتيح وبيئات التشغيل
├── pages/
│   ├── 1_📊_ATS_Score.py             # صفحة تقييم ومطابقة الـ ATS
│   ├── 2_🎯_Job_Matching.py          # صفحة مطابقة الوظائف (RAG Engine)
│   ├── 3_💼_LinkedIn_Audit.py        # صفحة تدقيق وتطوير ملف LinkedIn
│   └── 4_🏛️_University_Dashboard.py  # لوحة تحكم الجامعات ومتابعة الخريجين
├── utils/
│   ├── __init__.py                   # تصدير الحزم
│   ├── models.py                     # نماذج Pydantic v2 (UserProfile, Experience, etc.)
│   ├── skill_normalizer.py           # محرك توحيد المهارات (150+ مهارة قياسية)
│   ├── supabase_client.py            # وحدة المصادقة والتخزين السحابي (Supabase)
│   ├── state_manager.py              # إدارة Session State ومزامنة الحساب السحابي
│   └── cv_parser.py                  # محرك استخراج البيانات عبر Gemini و pypdf
├── supabase_schema.sql                # سكربت تهيئة جداول وسياسات Supabase RLS
├── .gitignore                         # حماية المفاتيح والمجلدات المؤقتة
├── requirements.txt                  # الاعتماديات المعتمدة والمثبتة
├── README.md                         # التوثيق الشامل
└── app.py                            # الصفحة الرئيسية وواجهة المستخدم
```

---

## ☁️ إعداد قاعدة بيانات Supabase

1. أنشئ مشروعاً جديداً على [Supabase](https://supabase.com).
2. توجه إلى **SQL Editor** ونفّذ الأوامر الموجودة في [`supabase_schema.sql`](supabase_schema.sql):
```sql
create table if not exists public.user_profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    email text,
    profile_data jsonb not null default '{}'::jsonb,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.user_profiles enable row level security;

create policy "Allow users to read own profile" on public.user_profiles
    for select using (auth.uid() = id);

create policy "Allow users to upsert own profile" on public.user_profiles
    for insert with check (auth.uid() = id);

create policy "Allow users to update own profile" on public.user_profiles
    for update using (auth.uid() = id);
```
3. احصل على **Project URL** و **anon public key** من إعدادات المشروع (`Project Settings -> API`).
4. أضفهما في ملف `.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```
*(ملاحظة: إذا لم تضف مفاتيح Supabase، سيعمل التطبيق تلقائياً في وضع الزائر دون أي توقف أو أخطاء).*

---

## ⚡ التشغيل السريع محلياً (Quickstart)

### 1. استنساخ المستودع (Clone Repo)
```bash
git clone https://github.com/Bodaxxt/career-copilot.git
cd career-copilot
```

### 2. إنشاء وتفعيل البيئة الافتراضية
```bash
# إنشاء البيئة
python -m venv .venv

# التفعيل على Windows (PowerShell):
.venv\Scripts\Activate.ps1

# التفعيل على Linux / macOS:
source .venv/bin/activate
```

### 3. تثبيت الاعتماديات (Install Dependencies)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. إعداد مفاتيح التشغيل (API Keys)
قم بنسخ ملف القالب وإنشاء ملف `secrets.toml`:
```bash
# Windows:
copy .streamlit\secrets.toml.example .streamlit\secrets.toml

# Linux / Mac:
cp .streamlit\secrets.toml.example .streamlit\secrets.toml
```
ثم أضف مفاتيحك الخاصة في `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "AIzaSy..."
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

### 5. إطلاق التطبيق (Run App)
```bash
streamlit run app.py
```
> 🌐 افتح المتصفح على: `http://localhost:8501`

---

## 🔄 التكامل المستمر (CI/CD Pipeline)

المشروع مزود بملف سير عمل GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) يقوم تلقائياً بالآتي عند كل تحديث لفرع `main`:
1. فحص جودة وتنسيق الكود عبر `flake8`.
2. تشغيل تطبيق Streamlit في وضع الخلفية (`headless`).
3. تنفيذ **Smoke Test** صحي عبر استدعاء نقطة `http://localhost:8501/_stcore/health` للتأكد من استجابة `200 OK` حتى بدون توفر مفاتيح Supabase الخارجية.

---

<div align="center">
صنع بـ ❤️ لتمكين الكفاءات المهنية وتطوير مسارهم الوظيفي بالذكاء الاصطناعي.
</div>
