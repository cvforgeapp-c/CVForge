import React from 'react'

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-[#143a52]">
      {/* Navbar matching reference banner color */}
      <header className="bg-[#134e6f] text-white px-5 py-3.5 flex items-center justify-between">
        {/* Left: Logo with white document icon box */}
        <div className="flex items-center gap-2.5">
          <div className="bg-white/10 p-2 rounded-xl text-white border border-white/20 flex items-center justify-center">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-serif font-bold text-2xl tracking-tight text-white">
            cvforge<span className="text-amber-400">.</span>
          </span>
        </div>

        {/* Right Controls: Flag + White Pill Button + Menu */}
        <div className="flex items-center gap-3">
          <span className="text-lg" aria-label="US Flag">🇺🇸</span>
          <button className="bg-white text-[#134e6f] hover:bg-gray-100 font-semibold text-sm px-4 py-1.5 rounded-full transition-colors">
            Try it
          </button>
          <button className="text-white p-1 ml-1">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </header>

      {/* Hero Content */}
      <section className="px-6 pt-12 pb-16 max-w-2xl mx-auto text-center">
        <h1 className="font-serif font-black text-4xl sm:text-5xl text-[#0d2838] leading-[1.15] mb-6 tracking-tight">
          Your resume,<br />optimized for the job<br />you want.
        </h1>
        <p className="text-gray-600 text-base sm:text-lg max-w-lg mx-auto mb-10 leading-relaxed font-normal">
          We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.
        </p>

        {/* Jobster Stat Box */}
        <div className="bg-[#f0f7fc] border border-[#d2e5f4] rounded-2xl p-6 sm:p-8 mb-10 text-center">
          <p className="text-[11px] font-bold tracking-widest text-[#5d7c93] uppercase mb-3">
            JOBSTER STUDY · 2025
          </p>
          <h2 className="font-serif font-bold text-2xl sm:text-3xl text-[#0d2838] leading-snug mb-4">
            75% of resumes are rejected before a human ever reads them.
          </h2>
          <p className="text-gray-600 text-sm">
            Yours will be optimized for the job you're targeting.
          </p>
        </div>

        {/* CTA Container with GDPR Badge Positioned Cleanly Outside Top-Right */}
        <div className="relative inline-block mb-3">
          <button className="bg-[#134e6f] hover:bg-[#0f3d57] text-white font-medium text-lg px-8 py-3.5 rounded-full flex items-center gap-2.5 shadow-md transition-all">
            <span>Try it for free</span>
            <span className="text-xl">&rarr;</span>
          </button>

          {/* GDPR Compliance Seal */}
          <div className="absolute -top-3 -right-5 w-11 h-11 bg-black text-white rounded-full flex flex-col items-center justify-center border-2 border-white shadow-lg text-[7px] font-bold tracking-tighter uppercase leading-tight text-center">
            <span>GDPR</span>
            <span className="text-[6px] text-gray-300">COMPLIANCE</span>
          </div>
        </div>

        <p className="text-xs text-gray-400 mt-2 font-normal">
          1 free credit · No credit card required
        </p>
      </section>
    </main>
  )
}
