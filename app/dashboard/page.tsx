'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobUrl, setJobUrl] = useState('');
  const [userName, setUserName] = useState('Kedir'); // Dynamic user name
  const [credits, setCredits] = useState({ coins: 0, target: 1 });
  const [isUploading, setIsUploading] = useState(false);

  // Today's formatted date (e.g., "Monday, September 28")
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setIsUploading(true);

      // Connect to your Flask API backend (/api/parse)
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
          // Optionally update user name from parsed resume if returned:
          if (data.name) setUserName(data.name.split(' ')[0]);
        }
      } catch (err) {
        console.warn('API call failed, running in local preview mode:', err);
      } finally {
        setFile(selectedFile);
        setIsUploading(false);
      }
    }
  };

  const handleLaunchOptimization = async () => {
    if (!file || !jobUrl) return;

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_url', jobUrl);

    try {
      const response = await fetch(`${API_BASE_URL}/api/optimize`, {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      console.log('Optimization Result:', result);
    } catch (err) {
      console.error('Optimization error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F2942]">
      {/* Navbar Header */}
      <nav className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-100">
        <Link href="/" className="text-xl font-bold tracking-tight flex items-center space-x-1">
          <span>cvforge</span>
          <span className="text-amber-500">.</span>
        </Link>

        {/* User Badges & Avatar */}
        <div className="flex items-center space-x-2">
          {/* Gold Token Counter */}
          <div className="flex items-center space-x-1 bg-[#FFFDF0] px-3 py-1 rounded-full border border-[#FDE68A] text-xs font-semibold text-amber-800">
            <span>{credits.coins}</span>
            <span className="w-4 h-4 rounded-full bg-amber-400 flex items-center justify-center text-[10px] text-white">🪙</span>
          </div>

          {/* Blue Target Counter */}
          <div className="flex items-center space-x-1 bg-[#EEF6FA] px-3 py-1 rounded-full border border-[#D0E4EF] text-xs font-semibold text-[#0F2942]">
            <span>{credits.target}</span>
            <span className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center text-[10px] text-white">🎯</span>
          </div>

          {/* User Profile Avatar Initials */}
          <div className="w-9 h-9 rounded-full bg-[#0F2942] text-white font-bold text-xs flex items-center justify-center">
            {userName ? userName.slice(0, 2).toUpperCase() : 'NM'}
          </div>
        </div>
      </nav>

      <main className="max-w-md mx-auto px-5 pt-6 pb-16">
        {/* Date Display */}
        <p className="text-xs font-medium text-gray-400 mb-1">{currentDate}</p>

        {/* Dynamic Greeting */}
        <h1 className="text-2xl font-serif font-bold text-[#0F2942] mb-6">
          Hello {userName}, ready to apply?
        </h1>

        {/* STATE 1: File NOT Uploaded Yet */}
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
          /* STATE 2: File Uploaded -> Displays Uploaded Card + Job Link + Launch Button (Image 5) */
          <div className="space-y-4 mb-8">
            {/* Base Resume Display Card */}
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
            <div className="grid grid-cols-2 gap-3 pt-1">
              <button className="bg-white border border-gray-200 text-gray-600 rounded-2xl py-3 font-semibold text-xs text-center">
                Trial <span className="text-gray-400 font-normal">(1)</span>
              </button>
              <button
                onClick={handleLaunchOptimization}
                disabled={!jobUrl}
                className={`rounded-2xl py-3 font-semibold text-xs flex items-center justify-center space-x-1 text-white transition ${
                  jobUrl ? 'bg-[#3B7A9E] hover:bg-opacity-90' : 'bg-[#7A9BB0] cursor-not-allowed'
                }`}
              >
                <span>✨</span>
                <span>Launch</span>
              </button>
            </div>
          </div>
        )}

        {/* My Optimized Resumes Section */}
        <div className="bg-white rounded-2xl border border-gray-100 p-8 text-center shadow-sm">
          <h2 className="text-lg font-serif font-bold text-[#0F2942] mb-6 flex items-center justify-center space-x-2">
            <span>✨</span>
            <span>My optimized resumes</span>
          </h2>
          <div className="w-12 h-12 border-2 border-gray-300 rounded-lg mx-auto mb-4 flex items-center justify-center text-gray-400">
            📄
          </div>
          <p className="font-semibold text-gray-700 text-sm mb-1">
            No optimized resumes yet
          </p>
          <p className="text-xs text-gray-500 max-w-xs mx-auto">
            Paste a job offer link above and click "Launch" to create an optimized resume.
          </p>
        </div>
      </main>
    </div>
  );
}
