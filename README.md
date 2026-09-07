# 🚀 CareerHub AI (Career Copilot)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini%20API-1.5%20Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![CI Status](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20Smoke%20Test-green?style=for-the-badge&logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

**المنصة الذكية المتكاملة لتطوير السير الذاتية، اجتياز أنظمة الـ ATS، مطابقة الوظائف بتقنيات RAG، وتدقيق ملفات LinkedIn.**

[تجربة المنصة](#-التشغيل-السريع-محليا-quickstart) • [المميزات الرئيسية](#-المميزات-الرئيسية-key-features) • [الهيكلية البرمجية](#-هيكلية-المشروع-project-architecture) • [النشر السحابي](#-النشر-على-streamlit-cloud)

</div>

---

## 🌟 نظرة عامة (Overview)

**CareerHub AI** (المعروف بـ **Career Copilot**) هو مساعد ذكي متكامل مصمم للباحثين عن عمل والمهنيين والجامعات. يعتمد التطبيق على أحدث نماذج الذكاء الاصطناعي من **Google Gemini** لاستخراج وتحليل بيانات السير الذاتية (PDF) بهيكلية JSON صافية فائقة الدقة، مع تقديم أدوات متخصصة لتقييم الـ ATS، مطابقة التوصيف الوظيفي، وتطوير الحساب المهني على LinkedIn.

---

## ✨ المميزات الرئيسية (Key Features)

| الميزة | الوصف | الحالة |
|---|---|---|
| 📄 **استخراج الـ CV الذكي** | قراءة وتحليل ملفات الـ PDF واستخراج مصفوفة بيانات مهيكلة عبر Gemini Flash | ✅ مكتمل (ST-01) |
| 🛡️ **إدارة الجلسات الآمنة** | منع أخطاء `KeyError` عند التنقل المباشر عبر `state_manager` المركزي | ✅ مكتمل (ST-02) |
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
│   ├── state_manager.py              # إدارة Session State المركزية ومنع أخطاء الجلسة
│   └── cv_parser.py                  # محرك استخراج البيانات عبر Gemini API
├── .gitignore                         # حماية المفاتيح والمجلدات المؤقتة
├── requirements.txt                  # الاعتماديات المعتمدة والمثبتة
├── README.md                         # التوثيق الشامل
└── app.py                            # الصفحة الرئيسية وواجهة المستخدم
```

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
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
ثم أضف مفتاح Gemini API الخاص بك في `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "AIzaSy..."
```

### 5. إطلاق التطبيق (Run App)
```bash
streamlit run app.py
```
> 🌐 افتح المتصفح على: `http://localhost:8501`

---

## ☁️ النشر على Streamlit Community Cloud

1. ارفع المشروع إلى حسابك على **GitHub**.
2. انتقل إلى [share.streamlit.io](https://share.streamlit.io) وسجل الدخول بحساب GitHub.
3. اضغط **New app** وحدد:
   - **Repository:** `Bodaxxt/career-copilot`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. في قسم **Advanced settings -> Secrets**، أضف المتغير:
   ```toml
   GEMINI_API_KEY = "مفتاح_جيميني_الخاص_بك"
   ```
5. اضغط **Deploy!** 🚀

---

## 🔄 التكامل المستمر (CI/CD Pipeline)

المشروع مزود بملف سير عمل GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) يقوم تلقائياً بالآتي عند كل تحديث لفرع `main`:
1. فحص جودة وتنسيق الكود عبر `flake8`.
2. تشغيل تطبيق Streamlit في وضع الخلفية (`headless`).
3. تنفيذ **Smoke Test** صحي عبر استدعاء نقطة `http://localhost:8501/_stcore/health` للتأكد من استجابة `200 OK`.

---

## 🤝 المساهمة (Contributing)

نرحب بجميع المساهمات والاقتراحات!
1. قم بعمل **Fork** للمشروع.
2. أنشئ فرعاً لميزتك (`git checkout -b feature/AmazingFeature`).
3. احفظ التغييرات (`git commit -m 'feat: Add some AmazingFeature'`).
4. ارفع الفرع (`git push origin feature/AmazingFeature`).
5. افتح **Pull Request**.

---

<div align="center">
صنع بـ ❤️ لتمكين الكفاءات المهنية وتطوير مسارهم الوظيفي بالذكاء الاصطناعي.
</div>
