'use client';

import React, { useState } from 'react';

export function LandingView({ onGetStarted }: { onGetStarted: () => void }) {
  const [showCookies, setShowCookies] = useState(true);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A] font-sans relative flex flex-col justify-between">
      {/* Header Bar */}
      <header className="w-full max-w-5xl mx-auto px-6 py-5 flex items-center justify-between border-b border-slate-200/60">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#0F3A5D] flex items-center justify-center text-white font-bold text-lg shadow-sm">
            📄
          </div>
          <span className="text-2xl font-black tracking-tight text-[#0F3A5D]">cvforge<span className="text-amber-500">.</span></span>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-xl cursor-pointer hover:opacity-80 transition-opacity">🇬🇧</span>
          <button 
            onClick={onGetStarted}
            className="px-5 py-2 rounded-full bg-white border border-slate-300 text-[#0F3A5D] font-semibold hover:bg-slate-50 transition-all cursor-pointer shadow-sm text-sm"
          >
            Try it
          </button>
          <button className="text-[#0F3A5D] p-2 hover:bg-slate-100 rounded-lg transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </header>

      {/* Main Content Hero */}
      <main className="max-w-3xl mx-auto px-6 py-12 flex-1 flex flex-col items-center text-center justify-center">
        <h1 className="text-4xl md:text-5xl font-serif font-black text-[#0F3A5D] leading-tight tracking-tight max-w-2xl">
          Your resume, optimized for the job you want.
        </h1>

        <p className="mt-6 text-base md:text-lg text-slate-600 max-w-xl leading-relaxed">
          We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.
        </p>

        {/* Statistic Callout Card */}
        <div className="mt-10 w-full max-w-xl bg-[#F0F6FA] border border-[#D9E6F0] rounded-2xl p-8 shadow-sm">
          <div className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-3">
            JOBSTER STUDY · 2025
          </div>
          <h2 className="text-2xl md:text-3xl font-serif font-extrabold text-[#0F3A5D] leading-snug">
            75% of resumes are rejected before a human ever reads them.
          </h2>
          <p className="mt-4 text-sm md:text-base text-slate-600 font-medium">
            Yours will be optimized for the job you're targeting.
          </p>
        </div>

        {/* Action Button */}
        <div className="mt-8">
          <button
            onClick={onGetStarted}
            className="px-8 py-3.5 rounded-full bg-[#0F3A5D] hover:bg-[#0A2740] text-white font-bold text-lg shadow-lg transition-all hover:scale-105 active:scale-95 cursor-pointer"
          >
            Get Started Now
          </button>
        </div>
      </main>

      {/* GDPR Cookie Banner */}
      {showCookies && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 w-[92%] max-w-md bg-white border border-slate-200 rounded-3xl p-5 shadow-2xl z-50 animate-in slide-in-from-bottom duration-300">
          <div className="flex items-start gap-3">
            <span className="text-2xl p-1 bg-amber-50 rounded-full">🍪</span>
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-slate-900">We use cookies</h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                This site uses cookies and a technical identifier from your device to improve your experience and prevent abuse.{' '}
                <a href="#" className="underline text-slate-700">Learn more</a>
              </p>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3">
            <button
              onClick={() => setShowCookies(false)}
              className="py-2.5 px-4 rounded-full border border-slate-300 text-slate-700 font-semibold text-xs hover:bg-slate-50 transition-colors"
            >
              Decline
            </button>
            <button
              onClick={() => setShowCookies(false)}
              className="py-2.5 px-4 rounded-full bg-[#0F3A5D] text-white font-semibold text-xs hover:bg-[#0A2740] transition-colors"
            >
              Accept
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
