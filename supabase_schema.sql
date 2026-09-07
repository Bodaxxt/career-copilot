-- ==============================================================================
-- CareerHub AI - Supabase Database & Auth Migration Schema
-- جدول حفظ وتخزين بيانات السيرة الذاتية السحابية للمستخدمين المسجلين
-- ==============================================================================

-- 1. إنشاء جدول user_profiles المرتبط بحسابات Supabase Auth
create table if not exists public.user_profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    email text,
    profile_data jsonb not null default '{}'::jsonb,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. تفعيل نظام حماية الصفوف (Row Level Security - RLS)
alter table public.user_profiles enable row level security;

-- 3. سياسات الأمان (Policies): لا يمكن لأي مستخدم القراءة أو التعديل إلا لملفه الشخصي فقط
drop policy if exists "Allow users to read own profile" on public.user_profiles;
create policy "Allow users to read own profile" on public.user_profiles
    for select using (auth.uid() = id);

drop policy if exists "Allow users to upsert own profile" on public.user_profiles;
create policy "Allow users to upsert own profile" on public.user_profiles
    for insert with check (auth.uid() = id);

drop policy if exists "Allow users to update own profile" on public.user_profiles;
create policy "Allow users to update own profile" on public.user_profiles
    for update using (auth.uid() = id);

-- 4. فهرس لتسريع البحث والـ JSON queries
create index if not exists idx_user_profiles_updated_at on public.user_profiles(updated_at desc);
