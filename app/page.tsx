// app/page.tsx - Landing Page (Reference Image 1)
"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, ShieldCheck, Menu, Globe } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#F7FAFC] text-[#0F2A4A] font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 max-w-6xl mx-auto border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#0F2A4A] rounded-md flex items-center justify-center text-white font-bold text-lg">
            ≡
          </div>
          <span className="text-xl font-bold tracking-tight text-[#0F2A4A]">
            cvforge<span className="text-amber-500">.</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <button className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900">
            <span className="text-base">🇬🇧</span>
          </button>
          <Link
            href="/dashboard"
            className="px-4 py-2 text-sm font-semibold border border-gray-200 rounded-full hover:bg-gray-50 transition"
          >
            Try it
          </Link>
          <button className="p-1 text-gray-700 md:hidden">
            <Menu className="w-6 h-6" />
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-2xl mx-auto px-6 pt-12 pb-16 text-center">
        <h1 className="text-3xl sm:text-4xl font-serif font-extrabold tracking-tight text-[#0F2A4A] leading-tight mb-4">
          Your resume, <br />
          optimized for the job <br />
          you want.
        </h1>

        <p className="text-gray-600 text-sm sm:text-base max-w-lg mx-auto mb-8">
          We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.
        </p>

        {/* Statistic Box */}
        <div className="bg-[#EDF5F9] border border-sky-100 rounded-2xl p-6 mb-8 text-center">
          <span className="text-[11px] font-bold tracking-widest text-sky-800 uppercase block mb-2">
            JOBSTER STUDY · 2025
          </span>
          <h2 className="text-2xl sm:text-3xl font-serif font-bold text-[#0F2A4A] mb-3 leading-snug">
            75% of resumes are rejected before a human ever reads them.
          </h2>
          <p className="text-xs sm:text-sm text-gray-600">
            Yours will be optimized for the job you're targeting.
          </p>
        </div>

        {/* CTA Button & Badge */}
        <div className="relative inline-block mb-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-[#17537A] hover:bg-[#113F5E] text-white font-semibold rounded-full shadow-md transition text-base"
          >
            Try it for free <ArrowRight className="w-4 h-4" />
          </Link>

          {/* GDPR Stamp Badge */}
          <div className="absolute -top-3 -right-6 w-12 h-12 bg-black text-white rounded-full p-1 text-[8px] flex items-center justify-center text-center font-bold border-2 border-white shadow-lg">
            GDPR COMPLIANCE
          </div>
        </div>

        <p className="text-xs text-gray-400 font-medium">
          1 free credit · No credit card required
        </p>
      </main>
    </div>
  );
}
