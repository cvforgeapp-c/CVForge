// app/dashboard/page.tsx - Optimized Dashboard View
"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Upload, FileText, Sparkles, Link as LinkIcon, Loader2 } from "lucide-react";

export default function DashboardPage() {
  const [jobLink, setJobLink] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [optimizedData, setOptimizedData] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setErrorMsg("");
    }
  };

  const handleLaunch = async () => {
    if (!file || !jobLink) return;
    setLoading(true);
    setErrorMsg("");

    try {
      // Step 1: Upload PDF and job URL to parse text
      const formData = new FormData();
      formData.append("file", file);
      formData.append("job_url", jobLink);

      const parseRes = await fetch("/api/parse", {
        method: "POST",
        body: formData,
      });

      const parseData = await parseRes.json();
      if (!parseRes.ok || parseData.error) {
        throw new Error(parseData.error || "Failed to process files");
      }

      // Step 2: Trigger AI optimization
      const optimizeRes = await fetch("/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cv_text: parseData.cv_text,
          job_text: parseData.job_text,
        }),
      });

      const result = await optimizeRes.json();
      if (!optimizeRes.ok || result.status === "error") {
        throw new Error(result.message || "Optimization failed");
      }

      setOptimizedData(result.data);
    } catch (err: any) {
      setErrorMsg(err.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F2A4A] font-sans">
      {/* Top Navbar */}
      <header className="flex items-center justify-between px-6 py-4 max-w-4xl mx-auto border-b border-gray-100">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#0F2A4A] rounded-md flex items-center justify-center text-white font-bold text-lg">
            ≡
          </div>
          <span className="text-xl font-bold tracking-tight text-[#0F2A4A]">
            cvforge<span className="text-amber-500">.</span>
          </span>
        </Link>

        <div className="flex items-center gap-3">
          {/* Credit Badge */}
          <div className="flex items-center gap-1.5 bg-sky-100/70 border border-sky-200 px-3 py-1 rounded-full text-xs font-bold text-sky-900">
            <span>1</span>
            <span className="w-3.5 h-3.5 bg-sky-500 rounded-full inline-block"></span>
          </div>

          <button className="px-4 py-2 bg-[#17537A] hover:bg-[#113F5E] text-white text-xs font-semibold rounded-full shadow-sm transition">
            Create an account
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-md mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-serif font-extrabold text-[#0F2A4A] mb-2">
            Optimize your resume for free
          </h1>
          <p className="text-xs sm:text-sm text-gray-500 leading-relaxed">
            Drop your resume and paste the job offer link to receive your optimized resume.
          </p>
        </div>

        {/* Error Message Alert */}
        {errorMsg && (
          <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
            {errorMsg}
          </div>
        )}

        {/* 1. Upload Box */}
        <div className="bg-sky-50/40 border-2 border-dashed border-sky-200 rounded-2xl p-6 text-center mb-4 transition hover:border-sky-300">
          <label className="cursor-pointer flex flex-col items-center">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-xs mb-3 text-sky-700">
              <Upload className="w-5 h-5" />
            </div>
            
            <span className="text-base font-serif font-bold text-[#0F2A4A] mb-2">
              Drag and drop your resume here
            </span>
            <span className="text-xs text-gray-400 mb-3">or</span>

            <span className="px-5 py-1.5 bg-white border border-gray-200 rounded-full text-xs font-semibold text-gray-700 shadow-2xs hover:bg-gray-50">
              {file ? file.name : "Browse"}
            </span>

            <input
              type="file"
              className="hidden"
              onChange={handleFileChange}
              accept=".pdf,.docx,.jpg,.png"
            />
          </label>
          <p className="text-[10px] text-gray-400 mt-4">
            PDF, DOCX or image (JPG/PNG), max 10 MB
          </p>
        </div>

        {/* Job Offer Link Input Box */}
        <div className="mb-4">
          <div className="relative flex items-center">
            <LinkIcon className="absolute left-3.5 w-4 h-4 text-gray-400" />
            <input
              type="url"
              placeholder="Paste job offer link here..."
              value={jobLink}
              onChange={(e) => setJobLink(e.target.value)}
              className="w-full pl-10 pr-24 py-2.5 bg-white border border-gray-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition shadow-2xs"
            />
            <button
              onClick={handleLaunch}
              disabled={!jobLink || !file || loading}
              className="absolute right-1.5 px-3 py-1.5 bg-[#17537A] hover:bg-[#113F5E] disabled:bg-gray-300 text-white text-xs font-semibold rounded-lg transition flex items-center gap-1"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : "Launch"}
            </button>
          </div>
        </div>

        {/* 2. My Optimized Resumes Box */}
        <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-2xs text-center">
          <div className="flex items-center gap-1.5 font-serif font-bold text-sm text-[#0F2A4A] mb-6">
            <Sparkles className="w-4 h-4 text-sky-600" />
            <span>My optimized resumes</span>
          </div>

          {optimizedData ? (
            <div className="text-left bg-sky-50/50 p-4 rounded-xl border border-sky-100">
              <h3 className="font-bold text-xs text-[#0F2A4A] mb-2">
                {file?.name.replace(".pdf", "")} (Optimized)
              </h3>
              <pre className="text-[11px] text-gray-600 whitespace-pre-wrap font-sans max-h-60 overflow-y-auto">
                {typeof optimizedData === "string" ? optimizedData : JSON.stringify(optimizedData, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="py-6 flex flex-col items-center justify-center">
              <div className="w-12 h-14 border-2 border-gray-300 rounded-lg flex items-center justify-center mb-3">
                <FileText className="w-6 h-6 text-gray-300" />
              </div>
              
              <p className="text-xs font-semibold text-gray-700 mb-1">
                No optimized resumes yet
              </p>
              <p className="text-[11px] text-gray-400 max-w-xs leading-relaxed">
                Paste a job offer link above and click "Launch" to create an optimized resume.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
