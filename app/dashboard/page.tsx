'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'

export default function Dashboard() {
  const [user, setUser] = useState<{ firstName: string; emailBadge: string } | null>(null)

  useEffect(() => {
    // Read user credentials saved during registration
    if (typeof window !== 'undefined') {
      const savedName = localStorage.getItem('cvforge_user_name')
      const savedEmail = localStorage.getItem('cvforge_user_email')

      if (savedName || savedEmail) {
        const badge = savedEmail ? savedEmail.trim().substring(0, 2).toUpperCase() : 'CV'
        setUser({
          firstName: savedName || 'User',
          emailBadge: badge
        })
      }
    }
  }, [])

  return (
    <main className="min-h-screen bg-[#fafbfc] text-[#143a52] px-4 py-4 max-w-lg mx-auto flex flex-col font-sans">
      {/* Header Bar */}
      <header className="flex items-center justify-between py-3 mb-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-[#134e6f] p-2 rounded-xl text-white shadow-sm">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-serif font-bold text-2xl text-[#0d2838]">
            cvforge<span className="text-amber-500">.</span>
          </span>
        </Link>

        {/* Top Right Controls */}
        <div className="flex items-center gap-2">
          <div className="bg-blue-50 text-[#134e6f] font-bold text-xs px-2.5 py-1.5 rounded-full flex items-center gap-1 border border-blue-100">
            <span>1</span>
            <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
          </div>

          {/* Dynamic Header Action: Email Badge Avatar OR Create an account button */}
          {user ? (
            <div className="w-9 h-9 rounded-full bg-[#134e6f] text-amber-300 font-extrabold text-xs flex items-center justify-center border-2 border-white shadow-sm tracking-wider">
              {user.emailBadge}
            </div>
          ) : (
            <Link
              href="/register"
              className="bg-[#134e6f] hover:bg-[#0f3d57] text-white text-xs font-semibold px-4 py-2 rounded-full transition-colors shadow-sm"
            >
              Create an account
            </Link>
          )}
        </div>
      </header>

      {/* Dynamic Salutation & Subtitle */}
      <section className="mb-6">
        <h1 className="font-serif font-extrabold text-2xl sm:text-3xl text-[#0d2838] mb-2 leading-tight">
          {user ? `Welcome back, ${user.firstName}!` : 'Optimize your resume for free'}
        </h1>
        <p className="text-gray-500 text-xs sm:text-sm leading-relaxed">
          Drop your resume and paste the job offer link to receive your optimized resume.
        </p>
      </section>

      {/* Upload Box */}
      <section className="border-2 border-dashed border-blue-200 bg-white rounded-2xl p-8 mb-6 text-center flex flex-col items-center justify-center transition-all hover:border-blue-300">
        <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        </div>
        <p className="font-serif font-bold text-base text-[#0d2838] mb-2">
          Drag and drop your resume here
        </p>
        <span className="text-gray-400 text-xs mb-3">or</span>
        <button className="bg-white border border-gray-200 text-gray-700 text-xs font-medium px-6 py-2 rounded-full shadow-xs hover:bg-gray-50 transition-colors mb-4">
          Browse
        </button>
        <p className="text-[11px] text-gray-400">
          PDF, DOCX or image (JPG/PNG), max 10 MB
        </p>
      </section>

      {/* Resumes Section */}
      <section className="bg-white border border-gray-100 rounded-2xl p-6 shadow-xs text-center">
        <div className="flex items-center justify-center gap-1 text-xs font-bold text-[#0d2838] mb-4">
          <span>✨</span>
          <span>My optimized resumes</span>
        </div>
        <div className="flex flex-col items-center justify-center py-4">
          <div className="w-10 h-10 bg-gray-50 border border-gray-100 rounded-lg flex items-center justify-center mb-2 text-gray-300">
            📄
          </div>
          <p className="text-xs font-semibold text-gray-700 mb-1">
            No optimized resumes yet
          </p>
          <p className="text-[11px] text-gray-400 max-w-xs leading-normal">
            Paste a job offer link above and click &quot;Launch&quot; to create an optimized resume.
          </p>
        </div>
      </section>
    </main>
  )
}
