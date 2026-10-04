import React from 'react'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="h-screen max-h-screen flex flex-col justify-between overflow-hidden bg-white text-[#143a52]">
      {/* Top Navbar */}
      <header className="bg-[#134e6f] text-white px-4 py-2.5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="bg-white/10 p-1.5 rounded-lg text-white border border-white/20 flex items-center justify-center">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-serif font-bold text-xl tracking-tight text-white">
            cvforge<span className="text-amber-400">.</span>
          </span>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="text-base" aria-label="US Flag">🇺🇸</span>
          <Link 
            href="/dashboard"
            className="bg-white text-[#134e6f] hover:bg-gray-100 font-semibold text-xs px-3.5 py-1 rounded-full transition-colors"
          >
            Try it
          </Link>
          <button className="text-white p-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </header>

      {/* Hero Body - Compact fitting for mobile viewports */}
      <section className="px-5 py-2 flex-1 flex flex-col justify-center items-center text-center max-w-xl mx-auto">
        <h1 className="font-serif font-black text-2xl sm:text-4xl text-[#0d2838] leading-tight mb-2 tracking-tight">
          Your resume, optimized for the job you want.
        </h1>
        <p className="text-gray-600 text-xs sm:text-sm max-w-md mx-auto mb-4 leading-normal">
          We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.
        </p>

        {/* Compact Jobster Box */}
        <div className="bg-[#f0f7fc] border border-[#d2e5f4] rounded-xl p-3.5 mb-4 text-center w-full">
          <p className="text-[10px] font-bold tracking-widest text-[#5d7c93] uppercase mb-1">
            JOBSTER STUDY · 2025
          </p>
          <h2 className="font-serif font-bold text-base sm:text-xl text-[#0d2838] leading-snug mb-1">
            75% of resumes are rejected before a human ever reads them.
          </h2>
          <p className="text-gray-600 text-xs">
            Yours will be optimized for the job you're targeting.
          </p>
        </div>

        {/* Interactive Link to Dashboard with Non-overlapping GDPR Badge */}
        <div className="relative inline-block mb-1">
          <Link
            href="/dashboard"
            className="bg-[#134e6f] hover:bg-[#0f3d57] text-white font-medium text-sm px-6 py-2.5 rounded-full flex items-center gap-2 shadow-sm transition-all"
          >
            <span>Try it for free</span>
            <span className="text-base">&rarr;</span>
          </Link>

          <div className="absolute -top-2 -right-4 w-9 h-9 bg-black text-white rounded-full flex flex-col items-center justify-center border-2 border-white shadow text-[6px] font-bold tracking-tighter uppercase leading-tight text-center">
            <span>GDPR</span>
            <span className="text-[5px] text-gray-300">COMPLIANCE</span>
          </div>
        </div>

        <p className="text-[10px] text-gray-400 mt-1">
          1 free credit · No credit card required
        </p>
      </section>
    </main>
  )
}
