import { SignInButton, SignUpButton, UserButton, Show } from '@clerk/nextjs';
import { Header } from '../components/header';
import { Footer } from '../components/footer';
import { CareerCard } from '../components/career-card';
import { APP_NAME } from '@career/shared';

export default function HomePage() {
  return (
    <div className="max-w-6xl mx-auto px-6 min-h-screen flex flex-col justify-between">
      {/* Header Component */}
      <Header />

      {/* Hero Section */}
      <main className="flex flex-col items-center text-center py-20">
        <span className="inline-block bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 px-4 py-1.5 rounded-full text-sm font-semibold mb-6">
          🚀 المنظومة الشاملة لتطوير المسار الوظيفي
        </span>

        <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-6">
          بوابتك الذكية للنمو المهني مع <br />
          <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
            {APP_NAME}
          </span>
        </h1>

        <p className="text-slate-400 text-lg md:text-xl max-w-2xl mb-10 leading-relaxed">
          منصة احترافية تجمع بين Next.js 15 و FastAPI و Celery Background Workers في Monorepo فائق الأداء.
        </p>

        <div>
          <Show when="signed-out">
            <SignUpButton mode="modal">
              <button className="px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:opacity-90 text-white font-bold text-lg transition-all shadow-xl hover:shadow-indigo-500/25">
                ابدأ رحلتك المهنية الآن مجاناً
              </button>
            </SignUpButton>
          </Show>
          <Show when="signed-in">
            <button className="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-lg transition-all shadow-lg">
              الانتقال إلى لوحة التحكم المهنية
            </button>
          </Show>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-16">
          <CareerCard
            icon="⚡"
            title="Turborepo Monorepo"
            description="إدارة مركزية لجميع التطبيقات والحزم المشتركة مع سرعة بناء فائقة بفضل Caching."
          />
          <CareerCard
            icon="🧠"
            title="FastAPI + Celery"
            description="خوادم معالجة غير متزامنة مدعومة بـ Python و Celery لتحليل السير الذاتية ومحاكاة المقابلات."
          />
          <CareerCard
            icon="🗄️"
            title="Postgres & ChromaDB"
            description="تخزين بيانات متقدم يجمع بين العلاقات وقواعد البيانات المتجهة (Vector Store) للبحث الدلالي."
          />
        </div>
      </main>

      {/* Footer Component */}
      <Footer />
    </div>
  );
}
