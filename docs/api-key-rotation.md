# 🔑 خطة تدوير مفاتيح API (API Key Rotation Strategy)

## متى تُدوِّر المفاتيح؟

| الحدث                | الإجراء                     |
| -------------------- | --------------------------- |
| كل **3 أشهر** دورياً | تدوير روتيني لجميع المفاتيح |
| اختراق أمني محتمل    | تدوير فوري لجميع المفاتيح   |
| مغادرة عضو من الفريق | تدوير فوري لجميع المفاتيح   |
| اكتشاف مفتاح في Git  | تدوير فوري + مراجعة السجلات |

---

## 📋 خطوات التدوير الدورية (كل 3 شهور)

### 1. Google Gemini API Key

**من أين تحصل على مفتاح جديد؟**

- ادخل على: [Google AI Studio](https://aistudio.google.com/app/apikey)
- اضغط **Create API Key**
- اختر مشروعك من Google Cloud

**خطوات التحديث:**

```bash
# 1. احصل على المفتاح الجديد من AI Studio
# 2. حدّث البيئة المحلية
echo "GEMINI_API_KEY=YOUR_NEW_KEY" >> apps/api/.env.development

# 3. حدّث Vercel (الإنتاج)
vercel env rm GEMINI_API_KEY production
vercel env add GEMINI_API_KEY production
# أدخل المفتاح الجديد عند الطلب

# 4. احذف المفتاح القديم من AI Studio فوراً
```

---

### 2. Clerk Keys (Publishable + Secret)

**من أين تحصل على مفاتيح جديدة؟**

- ادخل على: [Clerk Dashboard](https://dashboard.clerk.com)
- اختر مشروعك → **API Keys**
- اضغط **Roll API Keys** أو أنشئ مشروعاً جديداً للبيئة الجديدة

**خطوات التحديث:**

```bash
# 1. احصل على المفاتيح الجديدة من Clerk Dashboard

# 2. حدّث البيئة المحلية
# apps/web/.env.development
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_NEW_KEY
CLERK_SECRET_KEY=sk_test_NEW_KEY

# apps/api/.env.development
CLERK_SECRET_KEY=sk_test_NEW_KEY

# 3. حدّث Vercel
vercel env rm CLERK_SECRET_KEY production
vercel env add CLERK_SECRET_KEY production
vercel env rm NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY production
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY production

# 4. أعد Deployment
vercel --prod
```

---

### 3. SECRET_KEY (JWT Signing Key)

```bash
# توليد مفتاح عشوائي آمن
python -c "import secrets; print(secrets.token_urlsafe(64))"

# أو باستخدام OpenSSL
openssl rand -base64 64
```

---

## 🔧 تحديث المفاتيح في بيئات مختلفة

### البيئة المحلية (Development)

```bash
# عدّل الملفات مباشرة
apps/api/.env.development
apps/web/.env.development
```

### Vercel (Staging / Production)

```bash
# عرض المتغيرات الحالية
vercel env ls

# حذف متغير
vercel env rm VARIABLE_NAME [environment]

# إضافة متغير جديد
vercel env add VARIABLE_NAME [environment]

# أو عبر واجهة Vercel:
# Project → Settings → Environment Variables
```

### Docker / Server

```bash
# حدّث ملف .env على السيرفر
ssh user@server
nano /path/to/project/.env.production

# أعد تشغيل الحاويات
docker-compose down && docker-compose up -d
```

---

## ✅ Checklist تدوير المفاتيح

```
[ ] توليد مفاتيح جديدة من كل مزود
[ ] تحديث .env.development محلياً
[ ] تحديث متغيرات Vercel (Production)
[ ] تحديث متغيرات بيئة Staging (إن وجدت)
[ ] إعادة Deploy على Vercel
[ ] اختبار أن كل شيء يعمل بعد التغيير
[ ] حذف/إلغاء المفاتيح القديمة من لوحات التحكم
[ ] توثيق تاريخ التدوير في ملف CHANGELOG
```

---

> [!CAUTION]
> **لا تضع أي مفتاح حقيقي داخل الكود مباشرة أو في ملفات .env.example**
> استخدم دائماً placeholder مثل `sk_test_...` في ملفات المثال.

> [!WARNING]  
> إذا وجدت مفتاحاً حقيقياً قد رُفع على GitHub عن طريق الخطأ:
>
> 1. **غيّر المفتاح فوراً** من لوحة تحكم المزود
> 2. نظّف تاريخ Git باستخدام `git filter-branch` أو `BFG Repo Cleaner`
> 3. أخبر فريقك بالحادثة
