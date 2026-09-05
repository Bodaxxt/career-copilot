# 🚀 Career Copilot Monorepo

نظام متكامل لإدارة وتطوير المسار المهني بالذكاء الاصطناعي مبني باستخدام **Turborepo**، **Next.js 16 (App Router)**، و **FastAPI (Python)**.

---

## 🏗️ هيكلية المشروع (Architecture)

```text
Career-Copilot/
├── apps/
│   ├── web/                     # Frontend: Next.js 16 + React 19 + Clerk + TypeScript
│   │   ├── app/                 # صفحات App Router والتنسيقات
│   │   ├── __tests__/           # اختبارات الوحدة (Jest & Testing Library)
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── api/                     # Backend: FastAPI + Uvicorn + Pydantic v2
│       ├── main.py              # نقاط الـ API والـ Middleware
│       ├── requirements.txt     # حزم Python
│       ├── tests/               # اختبارات PyTest
│       └── package.json         # للتنسيق مع Turborepo
│
├── packages/
│   └── shared/                  # الحزم المشتركة (Shared Types & Constants)
│       ├── src/index.ts
│       └── package.json
│
├── .github/
│   └── workflows/
│       └── ci.yml               # CI Pipeline (Lint, Typecheck, Jest, PyTest)
│
├── .husky/                      # Git Pre-commit Hooks
├── .lintstagedrc.json           # تنسيق وفحص الأكواد قبل الـ Commit
├── turbo.json                   # إعدادات خطوط مهام Turborepo
├── pnpm-workspace.yaml          # إدارة فضاء العمل لـ pnpm
├── package.json                 # الـ Root Package
├── docker-compose.yml           # قواعد بيانات PostgreSQL و Redis
└── README.md
```

---

## ⚙️ المتطلبات الأساسية (Prerequisites)

- **Node.js**: إصدار `20.0.0` أو أحدث.
- **pnpm**: إصدار `9.x` (`npm install -g pnpm`).
- **Python**: إصدار `3.10` أو `3.11` مع `pip`.
- **Docker & Docker Compose** (اختياري لتشغيل PostgreSQL و Redis).

---

## 🛠️ خطوات التثبيت والتشغيل المحلي (Quick Start)

### 1. تثبيت حزم الـ Frontend والـ Monorepo
في المجلد الرئيسي للمشروع:
```bash
pnpm install
```

### 2. تثبيت بيئة الـ Backend (FastAPI)
```bash
cd apps/api
# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة:
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# تثبيت الحزم
pip install -r requirements.txt

cd ../..
```

### 3. تشغيل الخدمات المساندة (PostgreSQL + Redis)
```bash
docker-compose up -d
```

### 4. تشغيل جميع التطبيقات معاً (Turborepo)
في المجلد الرئيسي:
```bash
pnpm dev
```

- 🌐 **Frontend (Next.js):** [http://localhost:3000](http://localhost:3000)
- 🔌 **Backend (FastAPI Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 الأوامر المتاحة (Turborepo Commands)

| الأمر | الوصف |
|---|---|
| `pnpm dev` | تشغيل الـ Frontend والـ Backend معاً بالتوازي |
| `pnpm build` | بناء جميع التطبيقات والحزم المحتاجة للبناء |
| `pnpm lint` | فحص الأخطاء البرمجية (ESLint للواجهات و Flake8/Black للباك إند) |
| `pnpm lint:fix` | التصليح التلقائي وتنسيق الأكواد |
| `pnpm typecheck` | التحقق من الأنواع (TypeScript Check) في كامل الـ Monorepo |
| `pnpm test` | تشغيل اختبارات Jest للـ Frontend واختبارات PyTest للـ Backend |

---

## 🛡️ خطافات Git وتكامل الجودة (Husky & Lint-Staged)

المشروع مزود بـ **Husky Pre-commit Hooks** تضمن:
1. تطبيق Prettier و ESLint على ملفات TypeScript/JavaScript المعدلة.
2. تطبيق Black و Flake8 على ملفات Python المعدلة.
3. تشغيل فحص الأنواع `turbo run typecheck` قبل السماح بأي Commit.

---

## 🔄 مسار الـ CI/CD (GitHub Actions)

ملف [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) يقوم تلقائياً عند كل `push` أو `pull_request` بتشغيل:
- **Frontend Job:** فحص Prettier و ESLint، وتدقيق TypeScript، وتشغيل اختبارات Jest مع قياس التغطية (Coverage).
- **Backend Job:** فحص التنسيق بـ Black، وتدقيق Flake8، وتشغيل اختبارات PyTest غير المتزامنة.
