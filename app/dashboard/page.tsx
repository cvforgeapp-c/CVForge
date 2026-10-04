import React from 'react'
import Link from 'next/link'

export default function Dashboard() {
  return (
    <main className="min-h-screen bg-[#fcfdfe] text-[#143a52]">
      {/* Header Navigation */}
      <header className="bg-white border-b border-gray-100 px-4 py-3 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-[#134e6f] p-1.5 rounded-lg text-white">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-serif font-bold text-xl text-[#0d2838]">
            cvforge<span className="text-amber-500">.</span>
          </span>
        </Link>

        <div className="flex items-center gap-2.5">
          {/* Credit Counter */}
          <div className="bg-blue-50 text-[#134e6f] px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1 border border-blue-100">
            <span>1</span>
            <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
          </div>

          {/* Create Account Link -> Registration Page */}
          <Link
            href="/auth/register"
            className="bg-[#134e6f] text-white hover:bg-[#0f3d57] text-xs font-medium px-3.5 py-1.5 rounded-full transition-colors"
          >
            Create an account
          </Link>
        </div>
      </header>

      {/* Main Section */}
      <section className="px-5 py-8 max-w-xl mx-auto">
        <h1 className="font-serif font-bold text-2xl sm:text-3xl text-[#0d2838] mb-2">
          Optimize your resume for free
        </h1>
        <p className="text-gray-600 text-xs sm:text-sm mb-6">
          Drop your resume and paste the job offer link to receive your optimized resume.
        </p>

        {/* Upload Zone */}
        <div className="border-2 border-dashed border-blue-200 bg-blue-50/20 rounded-2xl p-8 text-center mb-8">
          <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-3 shadow-sm border border-gray-100 text-gray-600">
            &uarr;
          </div>
          <p className="font-serif font-bold text-base sm:text-lg text-[#0d2838] mb-2">
            Drag and drop your resume here
          </p>
          <p className="text-xs text-gray-400 mb-4">or</p>
          <button className="bg-white border border-gray-300 text-gray-700 font-medium text-xs px-5 py-2 rounded-full shadow-sm hover:bg-gray-50">
            Browse
          </button>
          <p className="text-[10px] text-gray-400 mt-4">
            PDF, DOCX or image (JPG/PNG), max 10 MB
          </p>
        </div>

        {/* Optimized Resumes Container */}
        <div className="bg-white border border-gray-100 rounded-2xl p-6 text-center shadow-sm">
          <h2 className="font-serif font-bold text-sm sm:text-base text-[#0d2838] mb-4 flex items-center justify-center gap-2">
            <span>&#10024;</span> My optimized resumes
          </h2>
          <div className="w-10 h-10 text-gray-300 mx-auto mb-2 flex items-center justify-center border border-gray-200 rounded-lg">
            📄
          </div>
          <p className="text-xs font-semibold text-gray-600 mb-1">No optimized resumes yet</p>
          <p className="text-[11px] text-gray-400">
            Paste a job offer link above and click "Launch" to create an optimized resume.
          </p>
        </div>
      </section>
    </main>
  )
}
