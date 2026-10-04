import React from 'react'
import Image from 'next/image'

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-[#0e2a47]">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-100 max-w-7xl mx-auto">
        {/* Left: Logo with dark blue document icon */}
        <div className="flex items-center gap-2.5">
          <div className="bg-[#1b4d72] p-2 rounded-xl text-white flex items-center justify-center">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-serif font-bold text-2xl tracking-tight text-[#0e2a47]">
            cvforge<span className="text-amber-500">.</span>
          </span>
        </div>

        {/* Right Controls: Flag + Try it Button + Menu */}
        <div className="flex items-center gap-4">
          <span className="text-xl" aria-label="US Flag">🇺🇸</span>
          <button className="bg-[#1b4d72] text-white px-5 py-2 rounded-full font-medium text-sm hover:bg-[#153e5c] transition-colors">
            Try it
          </button>
          <button className="text-gray-700 p-1">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-6 pt-12 pb-16 max-w-4xl mx-auto text-center">
        <h1 className="font-serif font-bold text-4xl sm:text-5xl md:text-6xl text-[#0e2a47] leading-tight mb-6">
          Your resume,<br />optimized for the job<br />you want.
        </h1>
        <p className="text-gray-600 text-lg max-w-xl mx-auto mb-10 leading-relaxed">
          We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.
        </p>

        {/* Jobster Stat Card */}
        <div className="bg-[#f0f7fc] border border-blue-100 rounded-3xl p-8 mb-12 max-w-2xl mx-auto text-center">
          <p className="text-xs font-semibold tracking-wider text-gray-500 uppercase mb-4">
            JOBSTER STUDY · 2025
          </p>
          <h2 className="font-serif font-bold text-2xl sm:text-3xl text-[#0e2a47] leading-snug mb-4">
            75% of resumes are rejected before a human ever reads them.
          </h2>
          <p className="text-gray-600 text-sm">
            Yours will be optimized for the job you're targeting.
          </p>
        </div>

        {/* CTA Button with Cleanly Positioned GDPR Badge */}
        <div className="relative inline-block mb-3">
          <button className="bg-[#1b4d72] hover:bg-[#153e5c] text-white text-lg font-medium px-8 py-4 rounded-full flex items-center gap-3 transition-colors shadow-md">
            <span>Try it for free</span>
            <span>&rarr;</span>
          </button>

          {/* GDPR Badge positioned to bottom-right without overlapping button text */}
          <div className="absolute -bottom-2 -right-6 translate-x-1/4 translate-y-1/4 w-12 h-12 bg-black text-white rounded-full flex items-center justify-center p-1 shadow-lg text-[9px] font-bold text-center leading-tight border-2 border-white">
            GDPR<br />COMPLIANCE
          </div>
        </div>

        <p className="text-xs text-gray-400 mt-4">
          1 free credit · No credit card required
        </p>
      </section>
    </main>
  )
}
