'use client';

import { useState } from 'react';
import Link from 'next/link';

interface OptimizedResume {
  id: string;
  companyName: string;
  source: string;
  date: string;
  jobPostingUrl: string;
  pdfUrl?: string;
}

export default function DashboardPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobUrl, setJobUrl] = useState('');
  const [userName, setUserName] = useState('Kedir');
  const [credits, setCredits] = useState({ coins: 0, target: 1 });
  const [isUploading, setIsUploading] = useState(false);

  // Optimization steps & results state
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [optimizedResumes, setOptimizedResumes] = useState<OptimizedResume[]>([]);

  // Modal download state
  const [selectedResumeForDownload, setSelectedResumeForDownload] = useState<OptimizedResume | null>(null);

  const steps = [
    'Reading your resume...',
    'Analyzing the job offer...',
    'Detecting ATS keywords...',
    'Rewriting your experiences...',
    'Calculating the score...',
  ];

  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setIsUploading(true);

      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
        const response = await fetch(`${API_BASE_URL}/api/parse`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          if (data.name) setUserName(data.name.split(' ')[0]);
        }
      } catch (err) {
        console.warn('API call failed, running in local mode:', err);
      } finally {
        setFile(selectedFile);
        setIsUploading(false);
      }
    }
  };

  const handleLaunchOptimization = async () => {
    if (!file || !jobUrl) return;

    setIsOptimizing(true);
    setCurrentStep(0);

    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        } else {
          clearInterval(stepInterval);
          return prev;
        }
      });
    }, 1200);

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_url', jobUrl);

    try {
      const response = await fetch(`${API_BASE_URL}/api/optimize`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setOptimizedResumes((prev) => [
          {
            id: Date.now().toString(),
            companyName: data.company_name || 'The Home Depot',
            source: 'LinkedIn',
            date: new Date().toLocaleString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
              hour: 'numeric',
              minute: '2-digit',
              hour12: true,
            }),
            jobPostingUrl: jobUrl,
            pdfUrl: data.pdf_url,
          },
          ...prev,
        ]);
      } else {
        throw new Error('Optimization failed');
      }
    } catch (err) {
      console.warn('Backend API offline, serving local completion mock:', err);
      setTimeout(() => {
        setOptimizedResumes((prev) => [
          {
            id: Date.now().toString(),
            companyName: 'The Home Depot',
            source: 'LinkedIn',
            date: new Date().toLocaleString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
              hour: 'numeric',
              minute: '2-digit',
              hour12: true,
            }),
            jobPostingUrl: jobUrl,
          },
          ...prev,
        ]);
      }, 6500);
    } finally {
      setTimeout(() => {
        setIsOptimizing(false);
      }, 6500);
    }
  };

  const handleDeleteResume = (id: string) => {
    setOptimizedResumes((prev) => prev.filter((item) => item.id !== id));
  };

  const triggerDownload = (watermarked: boolean) => {
    if (!selectedResumeForDownload) return;
    // Download logic here
    console.log(`Downloading ${selectedResumeForDownload.companyName} resume. Watermark: ${watermarked}`);
    setSelectedResumeForDownload(null);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F2942]">
      {/* Top Bar */}
      <nav className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-100">
        <Link href="/" className="text-xl font-bold tracking-tight flex items-center space-x-1">
          <span>cvforge</span>
          <span className="text-amber-500">.</span>
        </Link>

        {/* User Badges & Avatar */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 bg-[#FFFDF0] px-3 py-1 rounded-full border border-[#FDE68A] text-xs font-semibold text-amber-800">
            <span>{credits.coins}</span>
            <span className="w-4 h-4 rounded-full bg-amber-400 flex items-center justify-center text-[10px] text-white">🪙</span>
          </div>

          <div className="flex items-center space-x-1 bg-[#EEF6FA] px-3 py-1 rounded-full border border-[#D0E4EF] text-xs font-semibold text-[#0F2942]">
            <span>{credits.target}</span>
            <span className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center text-[10px] text-white">🎯</span>
          </div>

          <div className="w-9 h-9 rounded-full bg-[#0F2942] text-white font-bold text-xs flex items-center justify-center">
            {userName ? userName.slice(0, 2).toUpperCase() : 'NM'}
          </div>
        </div>
      </nav>

      <main className="max-w-md mx-auto px-5 pt-6 pb-16">
        <p className="text-xs font-medium text-gray-400 mb-1">{currentDate}</p>

        <h1 className="text-2xl font-serif font-bold text-[#0F2942] mb-6">
          Hello {userName}, ready to apply?
        </h1>

        {/* File Upload / Control Panel */}
        {!file ? (
          <div className="border-2 border-dashed border-[#C0D8E6] rounded-2xl bg-[#F3F8FB] p-8 text-center mb-8">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm border border-gray-100">
              <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            </div>
            <p className="font-serif font-bold text-[#0F2942] mb-4 text-lg">
              Drag and drop your resume here
            </p>
            <p className="text-xs text-gray-400 mb-4">or</p>

            <label className="cursor-pointer bg-white border border-gray-300 px-6 py-2 rounded-full text-sm font-semibold hover:bg-gray-50 transition inline-block">
              {isUploading ? 'Uploading...' : 'Browse'}
              <input type="file" accept=".pdf,.docx,.jpg,.png" className="hidden" onChange={handleFileUpload} />
            </label>
            <p className="text-[11px] text-gray-400 mt-6">
              PDF, DOCX or image (JPG/PNG), max 10 MB
            </p>
          </div>
        ) : (
          <div className="space-y-4 mb-8">
            {/* Base Resume Card */}
            <div className="bg-[#F3F8FB] border border-[#D0E4EF] rounded-2xl p-4 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-12 bg-white rounded border border-gray-200 flex items-center justify-center text-xs text-gray-400 font-mono shadow-sm">
                  📄
                </div>
                <div>
                  <span className="text-[10px] font-bold tracking-wider text-[#3B7A9E] uppercase block">
                    YOUR BASE RESUME
                  </span>
                  <p className="font-semibold text-sm text-[#0F2942]">{userName}</p>
                  <p className="text-xs text-gray-400 truncate max-w-[180px]">{file.name}</p>
                </div>
              </div>
              <label className="cursor-pointer p-2 hover:bg-white rounded-full transition text-gray-500">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                <input type="file" accept=".pdf,.docx" className="hidden" onChange={handleFileUpload} />
              </label>
            </div>

            {/* Job Offer Input Link */}
            <div className="flex space-x-2">
              <input
                type="url"
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                placeholder="https://www.linkedin.com/jobs/view/xx>"
                className="flex-1 bg-white border border-gray-200 rounded-2xl px-4 py-3 text-xs text-gray-700 focus:outline-none focus:border-[#0F2942]"
              />
              <button className="bg-white border border-gray-200 rounded-2xl px-3 py-3 text-gray-500 hover:bg-gray-50">
                🌐
              </button>
            </div>

            {/* Action Buttons Row */}
            <button
              onClick={handleLaunchOptimization}
              disabled={!jobUrl || isOptimizing}
              className={`w-full rounded-2xl py-3.5 font-semibold text-xs flex items-center justify-center space-x-1.5 text-white transition shadow-sm ${
                jobUrl && !isOptimizing ? 'bg-[#7093A8] hover:bg-opacity-90' : 'bg-[#9BB4C4] cursor-not-allowed'
              }`}
            >
              <span>✨</span>
              <span>{isOptimizing ? 'Optimizing...' : 'Launch the optimization'}</span>
            </button>
          </div>
        )}

        {/* My Optimized Resumes Container */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h2 className="text-lg font-serif font-bold text-[#0F2942] mb-6 flex items-center justify-center space-x-2">
            <span>✨</span>
            <span>My optimized resumes</span>
          </h2>

          {/* STATE A: Processing Active Optimization */}
          {isOptimizing ? (
            <div className="bg-[#F8FAFC] rounded-2xl p-6 text-left border border-gray-100">
              <h3 className="text-xl font-serif font-bold text-[#0F2942] text-center mb-6">
                We're working on it.
              </h3>
              <div className="space-y-4 max-w-xs mx-auto">
                {steps.map((stepText, index) => {
                  const isCompleted = index < currentStep;
                  const isCurrent = index === currentStep;

                  return (
                    <div key={index} className="flex items-center space-x-3 text-xs">
                      {isCompleted ? (
                        <div className="w-5 h-5 rounded-full bg-emerald-600 flex items-center justify-center text-white shrink-0">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      ) : isCurrent ? (
                        <div className="w-5 h-5 rounded-full border-2 border-[#0F2942] flex items-center justify-center shrink-0">
                          <div className="w-2 h-2 rounded-full bg-[#0F2942] animate-ping" />
                        </div>
                      ) : (
                        <div className="w-5 h-5 rounded-full bg-gray-100 shrink-0" />
                      )}

                      <span
                        className={`font-medium ${
                          isCompleted
                            ? 'text-gray-700'
                            : isCurrent
                            ? 'text-[#0F2942] font-semibold'
                            : 'text-gray-300'
                        }`}
                      >
                        {stepText}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : optimizedResumes.length > 0 ? (
            /* STATE B: Display Completed Optimized Resume Card */
            <div className="space-y-4">
              {optimizedResumes.map((resume) => (
                <div key={resume.id} className="bg-[#F8FAFC] border border-gray-100 rounded-2xl p-5 text-left">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-10 h-10 rounded-xl bg-orange-500 flex items-center justify-center text-white font-bold text-xs shadow-sm">
                      THD
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-[#0F2942]">{resume.source}</h3>
                    </div>
                  </div>

                  <h4 className="text-lg font-serif font-bold text-[#0F2942]">{resume.companyName}</h4>
                  <p className="text-xs text-gray-400 mb-2">{resume.date}</p>

                  <a
                    href={resume.jobPostingUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center space-x-1 text-xs text-[#3B7A9E] font-medium underline mb-6"
                  >
                    <span>View job posting</span>
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>

                  {/* Action Buttons */}
                  <div className="space-y-2.5">
                    <button
                      onClick={() => setSelectedResumeForDownload(resume)}
                      className="w-full bg-[#0F2942] text-white py-3 rounded-xl font-semibold text-xs flex items-center justify-center space-x-2 hover:bg-opacity-95 transition shadow-sm"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      <span>Download</span>
                    </button>

                    <button className="w-full bg-white border border-gray-200 text-[#0F2942] py-2.5 rounded-xl font-semibold text-xs flex items-center justify-center space-x-1.5 hover:bg-gray-50 transition">
                      <span>✏️️</span>
                      <span>Edit</span>
                    </button>

                    <button className="w-full bg-white border border-gray-200 text-[#0F2942] py-2.5 rounded-xl font-semibold text-xs flex items-center justify-center space-x-1.5 hover:bg-gray-50 transition">
                      <span>☆</span>
                      <span>Rate</span>
                    </button>

                    <button
                      onClick={() => handleDeleteResume(resume.id)}
                      className="w-full bg-[#FF4D4D] text-white py-3 rounded-xl font-semibold text-xs flex items-center justify-center space-x-1.5 hover:bg-opacity-90 transition shadow-sm"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      <span>Delete</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            /* STATE C: Empty State */
            <div className="py-6 text-center">
              <div className="w-12 h-12 border-2 border-gray-300 rounded-lg mx-auto mb-4 flex items-center justify-center text-gray-400">
                📄
              </div>
              <p className="font-semibold text-gray-700 text-sm mb-1">
                No optimized resumes yet
              </p>
              <p className="text-xs text-gray-500 max-w-xs mx-auto">
                Paste a job offer link above and click "Launch the optimization" to create an optimized resume.
              </p>
            </div>
          )}
        </div>
      </main>

      {/* CONGRATULATIONS / DOWNLOAD MODAL (Image 9) */}
      {selectedResumeForDownload && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl w-full max-w-sm overflow-hidden shadow-2xl transition-all">
            {/* Modal Header */}
            <div className="bg-[#0F2942] text-white px-6 py-5 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-amber-400 text-lg">✨</span>
                <h3 className="text-2xl font-serif font-bold tracking-tight">Congratulations!</h3>
              </div>
              <button
                onClick={() => setSelectedResumeForDownload(null)}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-gray-300 transition"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 text-left space-y-6">
              <p className="text-sm text-gray-600 leading-relaxed">
                Your resume tailored for{' '}
                <strong className="text-[#0F2942] font-bold">
                  {selectedResumeForDownload.companyName}
                </strong>{' '}
                at <strong className="text-[#0F2942] font-bold">{selectedResumeForDownload.source}</strong> is ready.
              </p>

              {/* Info Box */}
              <div className="bg-[#F0F7FB] border border-[#D0E4EF] rounded-2xl p-4 flex items-start space-x-3">
                <div className="p-1 text-[#0F2942] shrink-0">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <p className="text-xs text-[#0F2942] leading-normal">
                  A resume tailored to the job posting increases your chances <strong>3×</strong> compared to a generic resume. Every application deserves a custom-made resume.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3 pt-2 text-center">
                <button
                  onClick={() => triggerDownload(false)}
                  className="w-full bg-[#0F2942] text-white py-3.5 rounded-2xl font-semibold text-xs flex items-center justify-center space-x-2 hover:bg-opacity-95 transition shadow-sm"
                >
                  <span className="text-amber-400">✦</span>
                  <span>Download without watermark</span>
                </button>

                <button
                  onClick={() => triggerDownload(false)}
                  className="w-full bg-[#D97706] hover:bg-[#B45309] text-white py-3.5 rounded-2xl font-semibold text-xs flex items-center justify-center space-x-2 transition shadow-sm"
                >
                  <span>👑</span>
                  <span>Go Premium</span>
                </button>

                <button
                  onClick={() => triggerDownload(true)}
                  className="text-xs text-gray-500 hover:text-gray-800 underline transition inline-block pt-1"
                >
                  Download with watermark
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
