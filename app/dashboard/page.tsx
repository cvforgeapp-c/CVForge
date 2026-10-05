'use client'

import React, { useState, useEffect, useRef } from 'react'
import Link from 'next/link'

interface User {
  firstName: string
  emailBadge: string
  fullName?: string
  email?: string
  phone?: string
  location?: string
}

interface SkillGroup {
  category: string
  list: string
}

interface ExperienceItem {
  role: string
  company: string
  period?: string
  bulletPoints: string[]
}

interface EducationItem {
  degreeOrCert: string
  institution?: string
  year?: string
}

interface OptimizedResumeData {
  fullName: string
  titleWithExp: string
  contactLine: string
  summary: string
  skills: SkillGroup[]
  experience: ExperienceItem[]
  educationAndCerts: EducationItem[]
  languages?: string
  interests?: string
}

interface OptimizedResult {
  id: string
  company: string
  source: string
  jobTitle: string
  dateStr: string
  jobUrl: string
  atsBefore: number
  atsAfter: number
  matchingBefore: number
  matchingAfter: number
  resumeData: OptimizedResumeData
}

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null)
  const [jobUrl, setJobUrl] = useState('')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [stepIndex, setStepIndex] = useState(0)
  const [fileError, setFileError] = useState('')
  const [optimizedResults, setOptimizedResults] = useState<OptimizedResult[]>([])
  
  const [showDownloadModal, setShowDownloadModal] = useState(false)
  const [showPaywallModal, setShowPaywallModal] = useState(false)
  const [selectedResult, setSelectedResult] = useState<OptimizedResult | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadProgress, setDownloadProgress] = useState(0)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const pdfTemplateRef = useRef<HTMLDivElement>(null)

  const steps = [
    'Reading your resume...',
    'Analyzing the job offer...',
    'Detecting ATS keywords...',
    'Rewriting your experiences with AI...',
    'Calculating the ATS score...'
  ]

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedName = localStorage.getItem('cvforge_user_name')
      const savedEmail = localStorage.getItem('cvforge_user_email')

      if (savedName || savedEmail) {
        const badge = savedEmail ? savedEmail.trim().substring(0, 2).toUpperCase() : 'CV'
        setUser({
          firstName: savedName || 'User',
          fullName: savedName ? `${savedName} ALEMAYEHU` : 'KEDIR ABDELA',
          email: savedEmail || 'nmtullah86@gmail.com',
          phone: '0908706534',
          location: 'Los Angeles',
          emailBadge: badge
        })
      } else {
        setUser({
          firstName: 'Kedir',
          fullName: 'KEDIR ABDELA',
          email: 'nmtullah86@gmail.com',
          phone: '0908706534',
          location: 'Los Angeles',
          emailBadge: 'KA'
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

  const handleLaunch = async () => {
    if (!jobUrl || !uploadedFile) return
    setIsOptimizing(true)
    setStepIndex(0)

    const interval = setInterval(() => {
      setStepIndex((prev) => (prev < steps.length - 1 ? prev + 1 : prev))
    }, 1200)

    try {
      const response = await fetch('/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jobUrl,
          baseCvName: uploadedFile.name,
          user
        })
      })

      const resData = await response.json()
      clearInterval(interval)

      if (resData.success) {
        const aiData = resData.data
        const now = new Date()
        const formattedDate = now.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        }) + ' at ' + now.toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        })

        const formattedResumeData: OptimizedResumeData = {
          fullName: user?.fullName || "KEDIR ABDELA",
          titleWithExp: "Digital Marketing Specialist (5 yrs exp)",
          contactLine: `${user?.phone || '0908706534'} | ${user?.email || 'nmtullah86@gmail.com'} | Los Angeles\nlinkedin.com/in/kedirmohammed | Availability: 1 month`,
          summary: `Results-driven Digital Marketing Specialist with 5+ years of experience designing data-driven campaigns across Google, Meta, and LinkedIn. Proven track record in SEO, paid advertising, and content strategy, with measurable impact on traffic growth and audience engagement. Adept at managing budgets, analyzing performance metrics, and collaborating cross-functionally to deliver retail-focused marketing outcomes.`,
          skills: [
            { category: "Digital Marketing", list: "SEO, Social Media Marketing (Google, Instagram, Facebook, LinkedIn), Paid Advertising (Google Ads), Content Marketing, Email Marketing, Campaign Performance Analysis, Customer Acquisition, Budget Management, Data-Driven Strategy" },
            { category: "Tools & Analytics", list: "Google Analytics (Certified 2023), Google Ads Search (Certified 2023), HubSpot Content Marketing (Certified 2022), Microsoft Office Suite, Performance Reporting & Dashboards, Customer Research Tools" },
            { category: "Soft Skills", list: "Project Management, Cross-functional Collaboration, Strong Written & Verbal Communication, Analytical Thinking, Adaptability, Results Orientation, Attention to Detail, Multi-tasking in Fast-paced Environments" }
          ],
          experience: [
            {
              role: "Digital Marketing Specialist",
              company: "BrightWave Media",
              period: "2022 – Present",
              bulletPoints: [
                "Developed and managed multi-channel campaigns across Google, Instagram, Facebook, and LinkedIn, aligning creative assets with performance goals.",
                "Increased website traffic by 45% through targeted SEO strategies and content marketing initiatives.",
                "Managed monthly advertising budgets and conducted campaign performance analysis; collaborated with designers and content writers to produce high-impact marketing materials."
              ]
            },
            {
              role: "Marketing Coordinator",
              company: "NovaTech Solutions",
              period: "2019 – 2022",
              bulletPoints: [
                "Improved social media engagement by 30% within one year through optimized content scheduling and audience targeting.",
                "Created weekly performance reports using Google Analytics; assisted with email marketing campaigns and customer research initiatives."
              ]
            }
          ],
          educationAndCerts: [
            { degreeOrCert: "Bachelor of Business Administration", institution: "New York University" },
            { degreeOrCert: "Google Analytics Certification", institution: "Google", year: "2023" },
            { degreeOrCert: "Google Ads Search Certification", institution: "Google", year: "2023" },
            { degreeOrCert: "HubSpot Content Marketing Certification", institution: "HubSpot Academy", year: "2022" }
          ],
          languages: "English: Native | Spanish: Professional Working Proficiency | French: Basic",
          interests: "Technology & AI, Photography, Traveling, Reading, Entrepreneurship"
        }

        const newResult: OptimizedResult = {
          id: Date.now().toString(),
          company: aiData.company || "The Home Depot",
          source: aiData.source || "LinkedIn",
          jobTitle: aiData.jobTitle || "Digital Marketing Specialist",
          dateStr: formattedDate,
          jobUrl: jobUrl,
          atsBefore: aiData.atsScoreBefore || 48,
          atsAfter: aiData.atsScoreAfter || 88,
          matchingBefore: aiData.matchingBefore || 42,
          matchingAfter: aiData.matchingAfter || 85,
          resumeData: formattedResumeData
        }

        setOptimizedResults((prevResults) => [newResult, ...prevResults])
      }
    } catch (err) {
      console.error('Optimization error:', err)
    } finally {
      setIsOptimizing(false)
    }
  }

  const handleDelete = (id: string) => {
    setOptimizedResults((prev) => prev.filter((item) => item.id !== id))
  }

  const openDownloadModal = (res: OptimizedResult) => {
    setSelectedResult(res)
    setShowDownloadModal(true)
    setShowPaywallModal(false)
    setIsDownloading(false)
    setDownloadProgress(0)
  }

  const handlePremiumAction = () => {
    setShowDownloadModal(false)
    setShowPaywallModal(true)
  }

  const triggerPDFDownload = async (withWatermark: boolean) => {
    if (isDownloading) return
    setIsDownloading(true)
    setDownloadProgress(10)

    const progressInterval = setInterval(() => {
      setDownloadProgress((prev) => (prev >= 90 ? 90 : prev + 20))
    }, 200)

    if (typeof window !== 'undefined' && pdfTemplateRef.current) {
      const html2pdf = (await import('html2pdf.js')).default
      const element = pdfTemplateRef.current

      const watermarkEl = element.querySelector('#pdf-watermark') as HTMLElement
      if (watermarkEl) {
        watermarkEl.style.display = withWatermark ? 'flex' : 'none'
      }

      const opt = {
        margin:       0,
        filename:     `${selectedResult?.source || 'LinkedIn'} - ${selectedResult?.resumeData.fullName || 'Resume'} - ${selectedResult?.jobTitle || 'Optimized'}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
      }

      setTimeout(() => {
        html2pdf().set(opt).from(element).save().then(() => {
          clearInterval(progressInterval)
          setDownloadProgress(100)
          setTimeout(() => {
            setIsDownloading(false)
            setShowDownloadModal(false)
            setDownloadProgress(0)
          }, 300)
        })
      }, 800)
    }
  }

  return (
    <main className="min-h-screen bg-[#fafbfc] text-[#143a52] px-4 py-4 max-w-md mx-auto flex flex-col font-sans relative">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept=".pdf,.docx,.doc,image/jpeg,image/png"
      />

      {/* Header Navigation */}
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

      {!uploadedFile ? (
        <div className="mb-4">
          <h1 className="font-serif font-extrabold text-2xl text-[#0d2838] mb-1">
            Optimize your resume for free
          </h1>
          <p className="text-xs text-gray-500">
            Drop your resume and paste the job offer link to receive your optimized resume.
          </p>
        </div>
      ) : (
        <div className="mb-4">
          <p className="text-xs text-gray-400 font-medium mb-1">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
          <h1 className="font-serif font-extrabold text-2xl text-[#0d2838]">
            {user ? `Hello ${user.firstName}, ready to apply?` : 'Hello there, ready to apply?'}
          </h1>
        </div>
      )}

      {fileError && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 mb-3 font-medium">
          {fileError}
        </div>
      )}

      {!uploadedFile ? (
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
        <>
          <div className="bg-white border border-blue-100 rounded-2xl p-3.5 mb-3 flex items-center justify-between shadow-2xs">
            <div className="flex items-center gap-3">
              <div className="w-9 h-10 border border-gray-200 rounded-lg bg-gray-50 flex items-center justify-center text-gray-400 font-semibold text-xs">
                📄
              </div>
              <div>
                <span className="text-[10px] font-bold text-gray-400 tracking-wider block uppercase">
                  BASE RESUME
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
                <span>{isOptimizing ? 'Optimizing...' : 'Launch the optimization'}</span>
              </button>
            </div>
          </div>
        </>
      )}

      {/* Optimizations List */}
      <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-2xs flex-1 flex flex-col">
        <div className="flex items-center gap-1.5 text-sm font-serif font-bold text-[#0d2838] mb-4">
          <span>✨</span>
          <span>My optimized resumes</span>
        </div>

        {isOptimizing ? (
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
        ) : optimizedResults.length > 0 ? (
          <div className="space-y-4">
            {optimizedResults.map((res) => (
              <div key={res.id} className="border border-gray-100 rounded-2xl p-4 bg-white shadow-2xs space-y-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-[#004B23] text-white font-extrabold text-[9px] flex items-center justify-center p-1 text-center leading-tight uppercase">
                    {res.company.substring(0, 8)}
                  </div>
                  <span className="font-bold text-xs text-[#0d2838]">{res.source}</span>
                </div>

                <div>
                  <h4 className="font-serif font-bold text-sm text-[#0d2838]">
                    {res.company}
                  </h4>
                  <p className="text-[10px] text-gray-400 font-medium">
                    {res.dateStr}
                  </p>
                  <a
                    href={res.jobUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-[#134e6f] hover:underline inline-flex items-center gap-1 font-medium mt-1"
                  >
                    View job posting ↗
                  </a>
                </div>

                <div className="space-y-2 pt-1">
                  <button
                    onClick={() => openDownloadModal(res)}
                    className="w-full bg-[#004B23] hover:bg-[#00381a] text-white font-medium text-xs py-2.5 rounded-full flex items-center justify-center gap-1.5 shadow-xs"
                  >
                    <span>↓</span>
                    <span>Download</span>
                  </button>
                  <button
                    onClick={() => handleDelete(res.id)}
                    className="w-full bg-[#ef4444] hover:bg-[#dc2626] text-white font-medium text-xs py-2.5 rounded-full flex items-center justify-center gap-1.5 shadow-xs"
                  >
                    <span>🗑</span>
                    <span>Delete</span>
                  </button>
                </div>

                <div className="bg-[#ebf3f7] rounded-2xl p-4 mt-3 space-y-3">
                  <div className="grid grid-cols-2 text-center text-[10px] font-extrabold text-gray-400 tracking-wider">
                    <span>ATS</span>
                    <span>MATCHING</span>
                  </div>

                  <div className="grid grid-cols-4 gap-1 text-center items-center">
                    <div>
                      <div className="w-10 h-10 rounded-full border-4 border-gray-300 flex items-center justify-center mx-auto text-xs font-bold text-gray-700">
                        {res.atsBefore}%
                      </div>
                      <span className="text-[10px] text-gray-400 mt-1 block">Before</span>
                    </div>

                    <div>
                      <div className="w-10 h-10 rounded-full border-4 border-[#004B23] flex items-center justify-center mx-auto text-xs font-bold text-[#004B23]">
                        {res.atsAfter}%
                      </div>
                      <span className="text-[10px] text-gray-400 mt-1 block">After</span>
                    </div>

                    <div>
                      <div className="w-10 h-10 rounded-full border-4 border-red-400 flex items-center justify-center mx-auto text-xs font-bold text-gray-700">
                        {res.matchingBefore}%
                      </div>
                      <span className="text-[10px] text-gray-400 mt-1 block">Before</span>
                    </div>

                    <div>
                      <div className="w-10 h-10 rounded-full border-4 border-orange-400 flex items-center justify-center mx-auto text-xs font-bold text-gray-700">
                        {res.matchingAfter}%
                      </div>
                      <span className="text-[10px] text-gray-400 mt-1 block">After</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 pt-1">
                    <div className="bg-[#004B23] text-white text-center text-xs font-bold py-1 rounded-full">
                      +{res.atsAfter - res.atsBefore}%
                    </div>
                    <div className="bg-[#22c55e] text-white text-center text-xs font-bold py-1 rounded-full">
                      +{res.matchingAfter - res.matchingBefore}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="my-auto py-8 text-center flex flex-col items-center">
            <div className="w-10 h-10 border-2 border-gray-300 rounded-lg flex items-center justify-center mb-3 text-gray-300">
              📄
            </div>
            <p className="text-xs font-bold text-[#0d2838] mb-1">
              No optimized resumes yet
            </p>
            <p className="text-[11px] text-gray-400 max-w-xs leading-normal">
              Paste a job offer link above and click &quot;Launch the optimization&quot; to create an optimized resume.
            </p>
          </div>
        )}
      </div>

      {/* Download Modal */}
      {showDownloadModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl">
            <div className="bg-[#004B23] text-white p-5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-amber-300 text-lg">✨</span>
                <h3 className="font-serif font-bold text-xl tracking-tight">Congratulations!</h3>
              </div>
              <button
                onClick={() => !isDownloading && setShowDownloadModal(false)}
                disabled={isDownloading}
                className="w-7 h-7 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white text-sm disabled:opacity-30"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-5">
              <p className="text-xs text-gray-600 leading-relaxed font-medium">
                Your resume tailored for <strong className="text-[#0d2838] font-bold">{selectedResult?.company}</strong> at <strong className="text-[#0d2838] font-bold">{selectedResult?.source}</strong> is ready.
              </p>

              <div className="bg-[#f0f7fa] border border-blue-100 rounded-2xl p-3.5 flex items-start gap-2.5">
                <span className="text-[#004B23] text-sm mt-0.5">🛡</span>
                <p className="text-[11px] text-[#004B23] leading-snug font-medium">
                  A resume tailored to the job posting increases your chances 3× compared to a generic resume.
                </p>
              </div>

              {isDownloading ? (
                <div className="py-3 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-[#004B23]">
                    <span>Generating & downloading PDF...</span>
                    <span>{downloadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-[#004B23] h-2.5 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${downloadProgress}%` }}
                    ></div>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 pt-1">
                  <button
                    onClick={handlePremiumAction}
                    className="w-full bg-[#004B23] hover:bg-[#00381a] text-white font-bold text-xs py-3 rounded-full flex items-center justify-center gap-2 shadow-md transition-all"
                  >
                    <span>✦</span>
                    <span>Download without watermark</span>
                    <span className="ml-auto text-[10px] bg-amber-400 text-gray-900 font-extrabold px-2 py-0.5 rounded-full uppercase">PRO</span>
                  </button>

                  <button
                    onClick={handlePremiumAction}
                    className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-bold text-xs py-3 rounded-full flex items-center justify-center gap-2 shadow-md transition-all"
                  >
                    <span>👑</span>
                    <span>Go Premium</span>
                  </button>

                  <button
                    onClick={() => triggerPDFDownload(true)}
                    className="w-full text-center text-xs text-emerald-600 hover:text-emerald-700 font-semibold underline block pt-1"
                  >
                    Download with watermark (Free)
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Paywall Modal */}
      {showPaywallModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl p-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-amber-100 text-amber-600 font-bold text-2xl flex items-center justify-center mx-auto">
              👑
            </div>
            <h3 className="font-serif font-extrabold text-xl text-[#0d2838]">
              Upgrade to Premium
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Downloading watermark-free PDFs requires an active Pro Subscription or Premium credits.
            </p>

            <button
              onClick={() => alert('Redirecting to subscription checkout...')}
              className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-bold text-xs py-3 rounded-full shadow-md"
            >
              Unlock Premium - $9.99 / mo
            </button>

            <button
              onClick={() => {
                setShowPaywallModal(false)
                setShowDownloadModal(true)
              }}
              className="text-xs text-gray-400 hover:text-gray-600 font-medium underline block mx-auto pt-1"
            >
              Back to free option with watermark
            </button>
          </div>
        </div>
      )}

      {/* PDF TEMPLATE WITH COLORFUL HEADER BANNER (NAME, TITLE, ADDRESS) */}
      <div className="hidden">
        {selectedResult?.resumeData && (
          <div
            ref={pdfTemplateRef}
            className="w-[8.5in] min-h-[11in] bg-white relative font-sans text-gray-800 text-[11px] leading-relaxed"
            style={{ fontFamily: 'Arial, Helvetica, sans-serif' }}
          >
            {/* Background Watermark */}
            <div
              id="pdf-watermark"
              className="absolute inset-0 z-0 pointer-events-none hidden flex-col items-center justify-center"
            >
              <span className="text-gray-300 text-8xl font-extrabold tracking-widest opacity-25 -rotate-45 select-none">
                CVforge.co
              </span>
            </div>

            {/* COLORFUL HEADER BANNER: NAME, TITLE, AND CONTACT DETAILS */}
            <div className="bg-[#134e6f] text-white p-8 relative z-10">
              <h1 className="text-3xl font-extrabold uppercase tracking-tight text-white mb-1">
                {selectedResult.resumeData.fullName}
              </h1>
              <p className="text-sm font-bold text-amber-300 uppercase tracking-wide mb-3">
                {selectedResult.resumeData.titleWithExp}
              </p>
              <div className="text-[10.5px] text-blue-100 font-medium leading-normal whitespace-pre-line border-t border-blue-400/40 pt-2">
                {selectedResult.resumeData.contactLine}
              </div>
            </div>

            {/* MAIN CONTENT BODY */}
            <div className="p-8 relative z-10 space-y-5">
              
              {/* Professional Summary */}
              <div>
                <h2 className="text-xs font-bold text-[#134e6f] uppercase tracking-wider border-b-2 border-[#134e6f] pb-1 mb-2">
                  Professional Summary
                </h2>
                <p className="text-gray-700 text-[10.5px] leading-relaxed">
                  {selectedResult.resumeData.summary}
                </p>
              </div>

              {/* Key Skills */}
              <div>
                <h2 className="text-xs font-bold text-[#134e6f] uppercase tracking-wider border-b-2 border-[#134e6f] pb-1 mb-2">
                  Key Skills
                </h2>
                <div className="space-y-1.5">
                  {selectedResult.resumeData.skills.map((skillGroup, idx) => (
                    <p key={idx} className="text-[10.5px]">
                      <strong className="text-gray-900 font-bold">{skillGroup.category}:</strong>{' '}
                      <span className="text-gray-700">{skillGroup.list}</span>
                    </p>
                  ))}
                </div>
              </div>

              {/* Work Experience */}
              <div>
                <h2 className="text-xs font-bold text-[#134e6f] uppercase tracking-wider border-b-2 border-[#134e6f] pb-1 mb-2">
                  Work Experience
                </h2>
                <div className="space-y-3">
                  {selectedResult.resumeData.experience.map((exp, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between items-baseline">
                        <p className="font-bold text-gray-900 text-[11px]">
                          {exp.role} <span className="text-[#134e6f]">| {exp.company}</span>
                        </p>
                        {exp.period && (
                          <span className="text-[10px] font-bold text-gray-500">{exp.period}</span>
                        )}
                      </div>
                      <ul className="list-disc list-inside text-gray-700 text-[10.5px] space-y-1 pl-1">
                        {exp.bulletPoints.map((bullet, bIdx) => (
                          <li key={bIdx} className="leading-snug">{bullet}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Education & Certifications */}
              <div>
                <h2 className="text-xs font-bold text-[#134e6f] uppercase tracking-wider border-b-2 border-[#134e6f] pb-1 mb-2">
                  Education & Certifications
                </h2>
                <div className="space-y-1">
                  {selectedResult.resumeData.educationAndCerts.map((edu, idx) => (
                    <p key={idx} className="text-[10.5px] text-gray-700">
                      <strong className="text-gray-900">{edu.degreeOrCert}</strong>
                      {edu.institution && ` | ${edu.institution}`}
                      {edu.year && ` (${edu.year})`}
                    </p>
                  ))}
                </div>
              </div>

              {/* Languages */}
              {selectedResult.resumeData.languages && (
                <div>
                  <h2 className="text-xs font-bold text-[#134e6f] uppercase tracking-wider border-b-2 border-[#134e6f] pb-1 mb-1.5">
                    Languages
                  </h2>
                  <p className="text-[10.5px] text-gray-700">
                    {selectedResult.resumeData.languages}
                  </p>
                </div>
              )}

              {/* Interests & Projects */}
              {selectedResult.resumeData.interests && (
                <div>
                  <h2 className="text-xs font-bold text-[#134e6f] uppercase tracking-wider border-b-2 border-[#134e6f] pb-1 mb-1.5">
                    Interests & Projects
                  </h2>
                  <p className="text-[10.5px] text-gray-700">
                    {selectedResult.resumeData.interests}
                  </p>
                </div>
              )}

            </div>
          </div>
        )}
      </div>
    </main>
  )
}
