'use client'

import React, { useState } from 'react'
import Link from 'next/link'

export default function Home() {
  const [showCookieBanner, setShowCookieBanner] = useState(true)

  const handleCookieConsent = () => {
    setShowCookieBanner(false)
  }

  return (
    <main className="min-h-screen flex flex-col justify-between bg-white text-[#143a52] relative pb-28">
      {/* Header Banner */}
      <header className="bg-[#134e6f] text-white px-4 py-3.5 flex items-center justify-between shrink-0">
        {/* Left: Logo with document badge */}
        <div className="flex items-center gap-2">
          <div className="bg-[#0e3b54] p-2 rounded-xl text-white border border-white/10 flex items-center justify-center">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-serif font-bold text-2xl tracking-tight text-white">
            cvforge<span className="text-amber-400">.</span>
          </span>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-2.5">
          <span className="text-lg" aria-label="UK Flag">🇬🇧</span>
          <Link
            href="/dashboard"
            className="bg-white text-[#134e6f] hover:bg-gray-100 font-semibold text-xs px-4 py-1.5 rounded-full transition-colors"
          >
            Try it
          </Link>
          <button className="text-white p-1">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </header>

      {/* Main Hero Section */}
      <section className="px-5 pt-10 pb-6 flex-1 flex flex-col justify-center items-center text-center max-w-xl mx-auto">
        <h1 className="font-serif font-extrabold text-3xl sm:text-5xl text-[#0d2838] leading-[1.18] mb-4 tracking-tight">
          Your resume, optimized for the job you want.
        </h1>
        <p className="text-gray-600 text-sm sm:text-base max-w-md mx-auto mb-8 leading-relaxed font-normal">
          We tailor your resume to each job posting so it gets selected. No cheating, and full respect for your data.
        </p>

        {/* Jobster Study Card */}
        <div className="bg-[#f0f7fc] border border-[#d2e5f4] rounded-2xl p-6 mb-8 text-center w-full">
          <p className="text-[10px] font-bold tracking-widest text-[#5d7c93] uppercase mb-2">
            JOBSTER STUDY · 2025
          </p>
          <h2 className="font-serif font-bold text-xl sm:text-2xl text-[#0d2838] leading-snug mb-2">
            75% of resumes are rejected before a human ever reads them.
          </h2>
          <p className="text-gray-600 text-xs sm:text-sm">
            Yours will be optimized for the job you're targeting.
          </p>
        </div>

        {/* CTA Button with Overlapping GDPR Badge */}
        <div className="relative inline-block mb-2">
          <Link
            href="/dashboard"
            className="bg-[#134e6f] hover:bg-[#0f3d57] text-white font-medium text-base px-8 py-3 rounded-full flex items-center gap-2 shadow-sm transition-all"
          >
            <span>Try it for free</span>
            <span className="text-lg">&rarr;</span>
          </Link>

          {/* GDPR Starburst Badge */}
          <div className="absolute -top-3 -right-3 w-10 h-10 bg-black text-white rounded-full flex flex-col items-center justify-center border border-gray-700 shadow-md text-[6px] font-bold tracking-tighter uppercase leading-tight text-center">
            <span>GDPR</span>
            <span className="text-[5px] text-gray-300">COMPLIANCE</span>
          </div>
        </div>

        <p className="text-[11px] text-gray-400 mt-1">
          1 free credit · No credit card required
        </p>
      </section>

      {/* Interactive Cookie Consent Banner matching reference text exactly */}
      {showCookieBanner && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 p-4 shadow-2xl z-50 transition-all duration-300">
          <div className="max-w-md mx-auto flex flex-col gap-3">
            <div className="flex items-start gap-3">
              <span className="text-2xl leading-none">🍪</span>
              <div>
                <p className="font-bold text-sm text-[#0d2838]">We use cookies</p>
                <p className="text-xs text-gray-500 leading-snug mt-0.5">
                  This site uses cookies and a technical identifier from your device to improve your experience and prevent abuse.{' '}
                  <a href="#" className="underline text-gray-700">Learn more</a>
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 pt-1">
              <button
                onClick={handleCookieConsent}
                className="flex-1 py-2.5 border border-gray-300 rounded-full text-xs font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Decline
              </button>
              <button
                onClick={handleCookieConsent}
                className="flex-1 py-2.5 bg-[#134e6f] rounded-full text-xs font-semibold text-white hover:bg-[#0f3d57] transition-colors"
              >
                Accept
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
