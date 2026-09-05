import { SignInButton, UserButton, Show } from '@clerk/nextjs';

export function Header() {
  return (
    <header className="flex justify-between items-center py-6 border-b border-white/10">
      <div className="text-2xl font-extrabold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
        Career Copilot ✨
      </div>
      <div>
        <Show when="signed-out">
          <SignInButton mode="modal">
            <button className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-all shadow-md">
              تسجيل الدخول
            </button>
          </SignInButton>
        </Show>
        <Show when="signed-in">
          <div className="flex items-center gap-4">
            <span className="text-slate-400 text-sm">مرحباً بك!</span>
            <UserButton />
          </div>
        </Show>
      </div>
    </header>
  );
}
