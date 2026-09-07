# 🗄️ دليل إعداد قاعدة البيانات وتطبيق الـ Migrations (PostgreSQL + SQLAlchemy 2.0 + Alembic)

هذا الدليل يشرح كيفية إعداد قاعدة بيانات **Career Copilot**، وتطبيق تحديثات الـ Schema عبر **Alembic**، وتعبئة البيانات الأولية (Seed Data)، بالإضافة إلى تفعيل امتداد **pgvector** لدعم نظام الـ RAG والبحث الدلالي (Semantic Search).

---

## 🏗️ نظرة عامة على التصميم المعماري (Normalized Schema)

تم حل جميع مشاكل التصميم السابقة وإلغاء الاعتماد الزائد على `JSON` عبر تطبيع (Normalize) الجداول:

| المكون                           | الجداول                                                                   | الوصف والتحسينات                                                                              |
| -------------------------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **المستخدمون والجامعات**         | `users`, `universities`                                                   | دعم أدوار متعددة (`student`, `admin`, `recruiter`, `university_admin`) وربط الجامعات.         |
| **السيرة الذاتية و RAG**         | `cvs`, `cv_skills`, `cv_chunks`                                           | دعم `pgvector(1536)` في `cv_chunks` للبحث الشعاعي، وفصل مهارات السيرة الذاتية في `cv_skills`. |
| **الوظائف ومتطلباتها**           | `job_descriptions`, `job_requirements`                                    | فصل متطلبات الوظيفة (`job_requirements`) بدلاً من تخزينها كنصوص JSON مدمجة.                   |
| **تقديم الطلبات والمقابلات**     | `submissions`, `interviews`                                               | تتبع دورة التوظيف ومراحل المقابلات والتقييمات.                                                |
| **بنك أسئلة المقابلات**          | `interview_questions`, `interview_responses`                              | بنك أسئلة وتخزين إجابات وتقييم الذكاء الاصطناعي لكل سؤال على حدة.                             |
| **التكامل مع LinkedIn & GitHub** | `linkedin_data`, `linkedin_skills`, `github_data`, `github_contributions` | جداول منفصلة للمهارات والمساهمات بدلاً من تخزين JSON غير قابل للفلترة.                        |
| **قاموس المهارات الموحد**        | `skill_taxonomy`, `skill_aliases`                                         | قاموس مهارات مع مرادفات للبحث الذكي (مثل: `JS` → `JavaScript`).                               |
| **الاشتراكات والمدفوعات**        | `subscriptions`, `payments`                                               | تكامل مع Stripe وإدارة خطط الاستخدام وفواتير الدفع.                                           |
| **التنبيهات والتدقيق**           | `notifications`, `audit_logs`                                             | سجل أمني لجميع الحركات وتنبيهات المستخدمين.                                                   |
| **الشركاء والجامعات**            | `university_invites`, `bulk_match_jobs`                                   | دعوات الجامعات ومطابقة دفعات الخريجين آلياً مع الوظائف.                                       |
| **مصادر التوظيف الخارجية**       | `job_board_sources`                                                       | منصات التوظيف (LinkedIn, Wuzzuf, Indeed).                                                     |

---

## 📋 المتطلبات الأساسية (Prerequisites)

1. **PostgreSQL** (إصدار 15 أو أحدث) مثبت ويعمل.
2. امتداد **pgvector**:
   - للتثبيت عبر Docker:
     ```bash
     docker run -d --name postgres-vector -p 5432:5432 \
       -e POSTGRES_USER=postgres \
       -e POSTGRES_PASSWORD=postgres_password \
       -e POSTGRES_DB=career_copilot \
       pgvector/pgvector:pg16
     ```
   - للتثبيت المباشر على خادم Linux/Ubuntu:
     ```bash
     sudo apt install postgresql-16-pgvector
     ```

---

## ⚙️ التثبيت وإعداد البيئة

1. ادخل إلى مجلد الـ Backend:

   ```bash
   cd apps/api
   ```

2. ثبّت الحزم المطلوبة من `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

3. تأكد من إعداد ملف `.env` أو `.env.development` بمتغير الاتصال الصحيح:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres_password@localhost:5432/career_copilot
   ```

---

## 🚀 تشغيل الـ Migrations باستخدام Alembic

### 1. إنشاء ملف Migration جديد بناءً على النماذج:

```bash
alembic revision --autogenerate -m "Initial schema with pgvector and normalized tables"
```

### 2. تطبيق الـ Migration على قاعدة البيانات:

```bash
alembic upgrade head
```

### 3. التحقق من الإصدار الحالي لقاعدة البيانات:

```bash
alembic current
```

### 4. التراجع عن آخر Migration (Rollback عند الحاجة):

```bash
alembic downgrade -1
```

---

## 🌱 تعبئة البيانات الأولية (Seed Data)

يحتوي المشروع على سكريبت جاهز لتعبئة البيانات الأساسية (جامعات، قاموس مهارات مع مرادفاتها، منصات توظيف، وبنك أسئلة):

```bash
# من داخل مجلد apps/api
python scripts/seed_data.py
```

### البيانات التي يتم إضافتها تلقائياً:

- **3 جامعات رئيسية**: جامعة القاهرة، جامعة عين شمس، الجامعة الأمريكية.
- **قاموس مهارات متكامل**: Python, FastAPI, PostgreSQL, React, Next.js, Docker, TypeScript, Machine Learning مع أسماء مرادفة (`aliases`).
- **مصادر توظيف**: LinkedIn, Wuzzuf, Indeed.
- **بنك أسئلة مقابلات تجريبية**: أسئلة تقنية وسلوكية مع إجابات نموذجية.
- **حساب تجريبي لاختبار النظام**.

---

## 🔍 اختبار توافق pgvector والـ Embeddings

يمكنك التأكد من تفعيل امتداد الـ vector في قاعدة بياناتك عبر تشغيل الاستعلام:

```sql
-- داخل psql
CREATE EXTENSION IF NOT EXISTS vector;
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## 🛠️ حل المشاكل الشائعة (Troubleshooting)

| المشكلة                                           | السبب                                  | الحل                                                                  |
| ------------------------------------------------- | -------------------------------------- | --------------------------------------------------------------------- |
| `type "vector" does not exist`                    | امتداد pgvector غير مثبت في PostgreSQL | استخدم صورة `pgvector/pgvector` في Docker أو ثبّت الامتداد في الخادم. |
| `ModuleNotFoundError: No module named 'psycopg2'` | غياب مكتبة الربط المتزامن              | تأكد من تثبيت `psycopg2-binary>=2.9.10`.                              |
| `Target database is not up to date`               | يوجد Migration لم يُطبّق بعد           | نفّذ أمر `alembic upgrade head`.                                      |
