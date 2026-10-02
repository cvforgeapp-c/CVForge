'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function BuilderPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobUrl, setJobUrl] = useState('');
  const [tone, setTone] = useState('Professional');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleOptimize = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (!file || !jobUrl) {
      setErrorMsg('Please upload a resume file and provide a job link.');
      return;
    }

    setLoading(true);

    try {
      // 1. Upload & Parse CV File First
      const formData = new FormData();
      formData.append('file', file);

      const parseRes = await fetch(`${API_BASE_URL}/api/parse`, {
        method: 'POST',
        body: formData,
      });

      const parseData = await parseRes.json();
      if (!parseRes.ok) throw new Error(parseData.error || 'Parsing failed.');

      // 2. Trigger AI Optimization
      const token = localStorage.getItem('token');
      const optRes = await fetch(`${API_BASE_URL}/api/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          cv_text: parseData.data.raw_text,
          job_url: jobUrl,
          tone: tone,
        }),
      });

      const optData = await optRes.json();
      if (!optRes.ok) throw new Error(optData.error || 'Optimization failed.');

      setResult(optData);
    } catch (err: any) {
      setErrorMsg(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F2942] py-10 px-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex justify-between items-center border-b pb-4">
          <Link href="/dashboard" className="text-xl font-bold tracking-tight">
            <span>cvforge</span><span className="text-amber-500">.</span>
          </Link>
          <Link href="/dashboard" className="text-xs font-semibold hover:underline">
            ← Back to Dashboard
          </Link>
        </div>

        <h1 className="text-2xl font-serif font-bold">Forge Your ATS-Optimized CV</h1>

        {errorMsg && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-xs">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleOptimize} className="bg-white p-6 rounded-2xl border space-y-4 shadow-sm">
          <div>
            <label className="block text-xs font-semibold mb-1">1. Upload Existing CV (PDF/DOCX)</label>
            <input 
              type="file" 
              accept=".pdf,.docx,.txt"
              onChange={handleFileUpload} 
              className="w-full text-xs p-2 border rounded-xl"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold mb-1">2. Target Job Listing URL</label>
            <input 
              type="url" 
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              placeholder="https://linkedin.com/jobs/view/..."
              className="w-full border rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold mb-1">3. Tone Profile</label>
            <select 
              value={tone} 
              onChange={(e) => setTone(e.target.value)}
              className="w-full border rounded-xl p-3 text-sm focus:outline-none"
            >
              <option value="Professional">Professional & Direct</option>
              <option value="Executive">Executive & Leadership</option>
              <option value="Creative">Dynamic & Creative</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#0F2942] text-white py-3.5 rounded-full font-semibold text-sm hover:opacity-90 disabled:opacity-50"
          >
            {loading ? 'AI Engine Processing...' : 'Generate Optimized CV →'}
          </button>
        </form>

        {result && (
          <div className="bg-green-50 border border-green-200 p-6 rounded-2xl space-y-4">
            <h2 className="font-bold text-green-900 text-sm">✅ Optimization Complete!</h2>
            <p className="text-xs text-green-800">Target Role: {result.job_title}</p>
            <a 
              href={`${API_BASE_URL}/api/download/${localStorage.getItem('user')}`}
              target="_blank"
              className="inline-block bg-green-700 text-white px-5 py-2.5 rounded-full text-xs font-semibold hover:bg-green-800"
            >
              Download PDF Resume ↓
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
