import { ClerkProvider } from '@clerk/nextjs';
import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Career Copilot | مسار مسيرتك المهنية بالذكاء الاصطناعي',
  description: 'منصة Career Copilot الشاملة لبناء وتطوير السير الذاتية ومحاكاة المقابلات',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="ar" dir="rtl">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
