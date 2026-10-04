'use client'

import React, { useState, useEffect, useRef } from 'react'
import Link from 'next/link'

interface User {
  firstName: string
  emailBadge: string
}

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null)
  const [jobUrl, setJobUrl] = useState('')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [stepIndex, setStepIndex] = useState(0)
  const [fileError, setFileError] = useState('')

  const fileInputRef = useRef<HTMLInputElement>(null)

  const steps = [
    'Reading your resume...',
    'Analyzing the job offer...',
    'Detecting ATS keywords...',
    'Rewriting your experiences...',
    'Calculating the score...'
  ]

  useEffect(() => {
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFileError('')
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.size > 10 * 1024 * 1024) {
        setFileError('File size exceeds 10MB limit.')
        return
      }
      setUploadedFile(file)
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  const handleLaunch = () => {
    if (!jobUrl || !uploadedFile) return
    setIsOptimizing(true)
    setStepIndex(0)

    const interval = setInterval(() => {
      setStepIndex((prev) => {
        if (prev >= steps.length - 1) {
          clearInterval(interval)
          return prev
        }
        return prev + 1
      })
    }, 1200)
  }

  return (
    <main className="min-h-screen bg-[#fafbfc] text-[#143a52] px-4 py-4 max-w-md mx-auto flex flex-col font-sans">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.docx,.doc,image/jpeg,image/png"
      />

      {/* Top Header */}
      <header className="flex items-center justify-between py-2 mb-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-[#134e6f] p-1.5 rounded-xl text-white">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-serif font-bold text-xl text-[#0d2838]">
            cvforge<span className="text-amber-500">.</span>
          </span>
        </Link>

        <div className="flex items-center gap-2">
          {/* Credit Indicators */}
          {user && (
            <div className="bg-amber-50 text-amber-700 font-bold text-xs px-2.5 py-1 rounded-full flex items-center gap-1 border border-amber-200">
              <span>0</span>
              <span className="text-amber-500">🪙</span>
            </div>
          )}
          <div className="bg-blue-50 text-[#134e6f] font-bold text-xs px-2.5 py-1 rounded-full flex items-center gap-1 border border-blue-100">
            <span>1</span>
            <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
          </div>

          {/* User Email Badge / Account Button */}
          {user ? (
            <div className="w-8 h-8 rounded-full bg-[#134e6f] text-white font-extrabold text-xs flex items-center justify-center shadow-sm">
              {user.emailBadge}
            </div>
          ) : (
            <Link
              href="/register"
              className="bg-[#134e6f] text-white text-xs font-semibold px-3 py-1.5 rounded-full flex items-center gap-1 shadow-sm"
            >
              <span>+</span>
              <span>Create an account</span>
            </Link>
          )}
        </div>
      </header>

      {/* Dynamic Titles Depending on Upload State */}
      {!uploadedFile ? (
        /* STAGE 1: BEFORE UPLOAD */
        <div className="mb-4">
          <h1 className="font-serif font-extrabold text-2xl text-[#0d2838] mb-1">
            Optimize your resume for free
          </h1>
          <p className="text-xs text-gray-500">
            Drop your resume and paste the job offer link to receive your optimized resume.
          </p>
        </div>
      ) : (
        /* STAGE 2 & 3: AFTER UPLOAD */
        <div className="mb-4">
          <p className="text-xs text-gray-400 font-medium mb-1">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
          <h1 className="font-serif font-extrabold text-2xl text-[#0d2838]">
            {user ? `Hello ${user.firstName}, ready to apply?` : 'Hello there, ready to apply?'}
          </h1>
        </div>
      )}

      {/* Guest Warning Banner (Visible if not logged in) */}
      {!user && (
        <div className="bg-[#fff9db] border border-amber-200 rounded-2xl p-4 mb-4 flex items-center justify-between shadow-xs">
          <div className="flex items-start gap-2 max-w-[200px]">
            <span className="text-amber-600 text-sm mt-0.5">⚠</span>
            <div className="text-xs text-amber-900 leading-snug">
              <span className="font-bold block">Guest account -</span>
              Create an account to save your resumes and job offers permanently.
            </div>
          </div>
          <Link
            href="/register"
            className="bg-white border border-gray-200 text-[#0d2838] font-semibold text-xs px-3 py-2 rounded-full shadow-2xs hover:bg-gray-50"
          >
            Create an account
          </Link>
        </div>
      )}

      {/* Error Alert */}
      {fileError && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 mb-3 font-medium">
          {fileError}
        </div>
      )}

      {/* MAIN UPLOAD SECTION */}
      {!uploadedFile ? (
        /* Large Dropzone Box (Stage 1) */
        <div
          onClick={triggerFileInput}
          className="border-2 border-dashed border-blue-200 bg-white rounded-2xl p-8 mb-6 text-center flex flex-col items-center justify-center cursor-pointer hover:border-blue-400 transition-colors shadow-2xs"
        >
          <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </div>
          <p className="font-serif font-bold text-base text-[#0d2838] mb-1">
            Drag and drop your resume here
          </p>
          <span className="text-gray-400 text-xs mb-3">or</span>
          <button
            type="button"
            className="bg-white border border-gray-200 text-gray-700 text-xs font-medium px-5 py-2 rounded-full shadow-2xs hover:bg-gray-50 transition-colors mb-4"
          >
            Browse
          </button>
          <p className="text-[11px] text-gray-400">
            PDF, DOCX or image (JPG/PNG), max 10 MB
          </p>
        </div>
      ) : (
        /* Compact Base CV Card + Link Input + Launch Button (Stage 2 & 3) */
        <>
          <div className="bg-white border border-blue-100 rounded-2xl p-3.5 mb-3 flex items-center justify-between shadow-2xs">
            <div className="flex items-center gap-3">
              <div className="w-9 h-10 border border-gray-200 rounded-lg bg-gray-50 flex items-center justify-center text-gray-400 font-semibold text-xs">
                📄
              </div>
              <div>
                <span className="text-[10px] font-bold text-gray-400 tracking-wider block uppercase">
                  YOUR BASE CV
                </span>
                <p className="text-xs font-bold text-[#0d2838] truncate max-w-[180px]">
                  {user ? user.firstName : 'Base Resume'}
                </p>
                <p className="text-[11px] text-gray-400 truncate max-w-[180px]">
                  {uploadedFile.name}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={triggerFileInput}
              className="p-2 text-gray-400 hover:text-[#134e6f] transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </button>
          </div>

          <div className="space-y-3 mb-6">
            <div className="flex items-center border border-gray-200 rounded-2xl bg-white px-3.5 py-2.5 shadow-2xs focus-within:border-blue-400">
              <input
                type="url"
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                placeholder="https://www.linkedin.com/jobs/view/xx"
                className="w-full text-xs text-gray-700 focus:outline-none bg-transparent"
              />
              <div className="text-gray-400 pl-2 border-l border-gray-200 flex items-center gap-1 text-xs">
                🌐 <span className="text-[10px]">▼</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="bg-white border border-gray-200 rounded-full px-4 py-2.5 text-xs text-gray-600 font-medium">
                Trial <span className="text-gray-400">(1)</span>
              </div>
              <button
                onClick={handleLaunch}
                disabled={!jobUrl || isOptimizing}
                className="flex-1 bg-[#134e6f] hover:bg-[#0f3d57] disabled:opacity-50 text-white font-medium text-xs py-2.5 rounded-full transition-colors flex items-center justify-center gap-1.5 shadow-xs"
              >
                <span>✨</span>
                <span>{isOptimizing ? 'Optimizing...' : 'Launch'}</span>
              </button>
            </div>
          </div>
        </>
      )}

      {/* MY OPTIMIZED RESUMES SECTION */}
      <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-2xs flex-1 flex flex-col">
        <div className="flex items-center gap-1.5 text-xs font-bold text-[#0d2838] mb-4">
          <span>✨</span>
          <span>My optimized resumes</span>
        </div>

        {isOptimizing ? (
          /* Live Progress Box (Stage 3) */
          <div className="bg-[#fafbfc] border border-gray-100 rounded-2xl p-5 my-auto text-left space-y-3">
            <h3 className="font-serif font-bold text-base text-[#0d2838] mb-4">
              We&apos;re working on it.
            </h3>
            {steps.map((step, idx) => {
              const isDone = idx < stepIndex
              const isCurrent = idx === stepIndex
              return (
                <div key={idx} className="flex items-center gap-3 text-xs">
                  {isDone ? (
                    <div className="w-5 h-5 rounded-full bg-emerald-500 text-white flex items-center justify-center text-[10px] font-bold">
                      ✓
                    </div>
                  ) : isCurrent ? (
                    <div className="w-5 h-5 rounded-full border-2 border-[#134e6f] border-t-transparent animate-spin"></div>
                  ) : (
                    <div className="w-5 h-5 rounded-full bg-gray-100"></div>
                  )}
                  <span className={`font-medium ${isDone ? 'text-gray-800' : isCurrent ? 'text-[#134e6f] font-semibold' : 'text-gray-300'}`}>
                    {step}
                  </span>
                </div>
              )
            })}
          </div>
        ) : (
          /* Default Empty List Box */
          <div className="my-auto py-8 text-center flex flex-col items-center">
            <div className="w-10 h-10 border-2 border-gray-300 rounded-lg flex items-center justify-center mb-3 text-gray-300">
              📄
            </div>
            <p className="text-xs font-bold text-[#0d2838] mb-1">
              No optimized resumes yet
            </p>
            <p className="text-[11px] text-gray-400 max-w-xs leading-normal">
              Paste a job offer link above and click &quot;Launch&quot; to create an optimized resume.
            </p>
          </div>
        )}
      </div>
    </main>
  )
}
