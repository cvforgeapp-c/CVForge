'use client';

import React from 'react';

export function LandingView({ onGetStarted }: { onGetStarted: () => void }) {
  return (
    <section className="relative overflow-hidden py-24 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold mb-8">
        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        Over 75% of CVs are rejected by ATS filters before a human sees them
      </div>

      <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white max-w-4xl leading-tight">
        Bypass ATS Filters with <span className="text-indigo-400">Tailored CVs</span> Generated in Seconds
      </h1>

      <p className="mt-6 text-lg text-slate-400 max-w-2xl leading-relaxed">
        Upload your current resume, paste the target job description, and watch our AI optimize your profile for maximum recruiter callbacks.
      </p>

      <div className="mt-10 flex flex-col sm:flex-row gap-4 items-center">
        <button
          onClick={onGetStarted}
          className="px-8 py-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-lg shadow-lg shadow-indigo-600/30 transition-all hover:scale-105 active:scale-95 cursor-pointer"
        >
          Try It for Free
        </button>
        <span className="text-xs text-slate-500">No credit card or sign-up required</span>
      </div>
    </section>
  );
}
