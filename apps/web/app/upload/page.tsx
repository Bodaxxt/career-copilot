'use client';

import React, { useState, useRef } from 'react';
import { useUser, SignInButton, SignedIn, SignedOut } from '@clerk/nextjs';
import type { UploadResponse } from '@career/shared';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default function UploadPage() {
  const { user } = useUser();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndSetFile = (file: File) => {
    setErrorMessage(null);
    setUploadResult(null);

    // 1. Validate File Type (PDF Only)
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');

    if (!isPdf) {
      setErrorMessage('عذراً، يُسمح فقط برفع الملفات بصيغة PDF (.pdf).');
      setSelectedFile(null);
      return false;
    }

    // 2. Validate File Size (Max 10MB)
    if (file.size > MAX_FILE_SIZE) {
      const sizeInMB = (file.size / (1024 * 1024)).toFixed(1);
      setErrorMessage(
        `حجم الملف (${sizeInMB} ميجابايت) يتجاوز الحد الأقصى المسموح به (10 ميجابايت).`,
      );
      setSelectedFile(null);
      return false;
    }

    setSelectedFile(file);
    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setErrorMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'حدث خطأ أثناء رفع السيرة الذاتية.');
      }

      setUploadResult(data);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'فشل الرفع، يرجى المحاولة لاحقاً.');
    } finally {
      setIsUploading(false);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadResult(null);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div
      className="min-h-screen bg-[#0b0f19] text-[#f8fafc] flex flex-col font-['Tajawal',sans-serif]"
      dir="rtl"
    >
      {/* Header */}
      <header className="border-b border-white/10 bg-[#161e31]/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-extrabold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Career Copilot
            </span>
            <span className="bg-indigo-500/20 text-indigo-300 text-xs px-2.5 py-1 rounded-full font-medium border border-indigo-500/30">
              رفع السيرة الذاتية
            </span>
          </div>
          <nav className="flex items-center gap-4 text-sm">
            <a href="/" className="text-slate-400 hover:text-white transition-colors">
              الرئيسية
            </a>
            <span className="text-slate-400">
              {user ? `مرحباً، ${user.firstName || user.fullName || 'مستخدم'}` : ''}
            </span>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-6 py-12 flex flex-col items-center">
        {/* Title Section */}
        <div className="text-center mb-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-sm px-4 py-1.5 rounded-full mb-4">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            التحليل الذكي المدعوم بالذكاء الاصطناعي
          </div>
          <h1 className="text-4xl font-black mb-3 leading-tight tracking-tight">
            ارفع سيرتك الذاتية (CV)
          </h1>
          <p className="text-slate-400 text-base leading-relaxed">
            قم برفع سيرتك الذاتية بصيغة PDF لنقوم بتحليلها بدقة، استخراج المهارات، ومطابقتها مع أفضل
            الفرص وسوق العمل.
          </p>
        </div>

        {/* Signed Out State */}
        <SignedOut>
          <div className="w-full bg-[#161e31]/80 border border-white/10 rounded-2xl p-8 text-center backdrop-blur-xl shadow-2xl">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-2xl">
              🔒
            </div>
            <h2 className="text-xl font-bold mb-2">تسجيل الدخول مطلوب</h2>
            <p className="text-slate-400 text-sm mb-6 max-w-md mx-auto">
              يرجى تسجيل الدخول أو إنشاء حساب جديد للتمكن من رفع سيرتك الذاتية والبدء في رحلتك
              المهنية.
            </p>
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:opacity-90 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg hover:shadow-indigo-500/25 cursor-pointer">
                تسجيل الدخول الآن
              </button>
            </SignInButton>
          </div>
        </SignedOut>

        {/* Signed In Upload Zone */}
        <SignedIn>
          <div className="w-full bg-[#161e31]/80 border border-white/10 rounded-3xl p-8 backdrop-blur-xl shadow-2xl">
            {/* Error Alert */}
            {errorMessage && (
              <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-lg">⚠️</span>
                  <span>{errorMessage}</span>
                </div>
                <button
                  onClick={() => setErrorMessage(null)}
                  className="text-rose-400 hover:text-rose-200 text-xs font-semibold"
                >
                  إغلاق
                </button>
              </div>
            )}

            {/* Success State */}
            {uploadResult ? (
              <div className="text-center py-8">
                <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-3xl animate-bounce">
                  ✓
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">تم رفع السيرة الذاتية بنجاح!</h2>
                <p className="text-slate-400 text-sm mb-6">
                  تم حفظ الملف وجاري إعداده للتحليل واستخراج المهارات.
                </p>

                {/* Upload Details Card */}
                <div className="bg-slate-900/60 border border-white/10 rounded-2xl p-6 mb-8 text-right max-w-md mx-auto">
                  <div className="flex justify-between items-center py-2 border-b border-white/5">
                    <span className="text-slate-400 text-sm">اسم الملف:</span>
                    <span className="font-semibold text-sm text-indigo-300">
                      {uploadResult.original_filename || selectedFile?.name}
                    </span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-white/5">
                    <span className="text-slate-400 text-sm">معرف السيرة الذاتية (ID):</span>
                    <span className="font-mono text-xs text-slate-300">{uploadResult.cv_id}</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-slate-400 text-sm">حالة المعالجة:</span>
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
                      {uploadResult.status}
                    </span>
                  </div>
                </div>

                <div className="flex gap-4 justify-center">
                  <button
                    onClick={resetUpload}
                    className="px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold transition-colors cursor-pointer"
                  >
                    رفع سيرة ذاتية أخرى
                  </button>
                  <a
                    href="/"
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:opacity-90 text-white text-sm font-bold transition-all shadow-md cursor-pointer"
                  >
                    الانتقال للوحة التحكم
                  </a>
                </div>
              </div>
            ) : (
              /* Dropzone Form */
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileChange}
                  className="hidden"
                  id="cv-file-input"
                />

                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center ${
                    dragActive
                      ? 'border-indigo-400 bg-indigo-500/10 scale-[1.01]'
                      : selectedFile
                        ? 'border-emerald-500/50 bg-emerald-500/5'
                        : 'border-white/15 hover:border-indigo-500/50 hover:bg-white/[0.02]'
                  }`}
                >
                  <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-3xl mb-4 text-indigo-400">
                    📄
                  </div>

                  {selectedFile ? (
                    <div className="space-y-1">
                      <p className="text-emerald-400 font-bold text-lg">{selectedFile.name}</p>
                      <p className="text-slate-400 text-xs">
                        الحجم: {(selectedFile.size / (1024 * 1024)).toFixed(2)} ميجابايت • اضغط
                        للتغيير
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <p className="text-lg font-bold text-slate-200">
                        اسحب ملف الـ PDF وأفلته هنا، أو{' '}
                        <span className="text-indigo-400 underline underline-offset-4">
                          تصفح جهازك
                        </span>
                      </p>
                      <p className="text-slate-400 text-xs">
                        صيغة PDF فقط • الحد الأقصى للحجم 10 ميجابايت
                      </p>
                    </div>
                  )}
                </div>

                {/* Upload Button */}
                <div className="mt-8 flex justify-end gap-3">
                  {selectedFile && (
                    <button
                      type="button"
                      onClick={resetUpload}
                      disabled={isUploading}
                      className="px-5 py-3 rounded-xl border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 text-sm font-semibold transition-colors disabled:opacity-50"
                    >
                      إلغاء
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={handleUpload}
                    disabled={!selectedFile || isUploading}
                    className="flex items-center justify-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:opacity-90 text-white font-bold text-sm transition-all shadow-lg hover:shadow-indigo-500/25 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer min-w-[160px]"
                  >
                    {isUploading ? (
                      <>
                        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                        <span>جاري الرفع...</span>
                      </>
                    ) : (
                      <span>تأكيد ورفع الـ CV</span>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </SignedIn>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mt-10">
          <div className="p-5 rounded-2xl bg-[#161e31]/40 border border-white/5 text-right">
            <span className="text-xl mb-2 block">🔒</span>
            <h3 className="font-bold text-sm text-slate-200 mb-1">أمان وخصوصية تامة</h3>
            <p className="text-slate-400 text-xs leading-relaxed">
              تشفير متكامل للبيانات وحفظ محمي للسير الذاتية.
            </p>
          </div>
          <div className="p-5 rounded-2xl bg-[#161e31]/40 border border-white/5 text-right">
            <span className="text-xl mb-2 block">⚡</span>
            <h3 className="font-bold text-sm text-slate-200 mb-1">تحليل سريع وفوري</h3>
            <p className="text-slate-400 text-xs leading-relaxed">
              استخراج المهارات والتجارب في ثوانٍ معدودة.
            </p>
          </div>
          <div className="p-5 rounded-2xl bg-[#161e31]/40 border border-white/5 text-right">
            <span className="text-xl mb-2 block">🎯</span>
            <h3 className="font-bold text-sm text-slate-200 mb-1">مطابقة الفرص بدقة</h3>
            <p className="text-slate-400 text-xs leading-relaxed">
              توصيات مخصصة للوظائف والتدريب المناسب لمستواك.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
