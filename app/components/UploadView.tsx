'use client';

import React, { useState } from 'react';

export function InteractiveUploadView({ 
  onSessionCreated, 
  onExportRequested 
}: { 
  onSessionCreated: (id: string) => void;
  onExportRequested: () => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [jobUrl, setJobUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [streamProgress, setStreamProgress] = useState<{ step: string; percent: number }>({
    step: 'Idle',
    percent: 0,
  });

  const handleStartAnalysis = async () => {
    if (!file || !jobUrl) return;
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('resume', file);
      formData.append('job_url', jobUrl);

      const res = await fetch('/api/v1/analyze', { method: 'POST', body: formData });
      const data = await res.json();
      
      onSessionCreated(data.sessionId);

      const eventSource = new EventSource(`/api/v1/stream-analysis?sessionId=${data.sessionId}`);

      eventSource.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        setStreamProgress({ step: payload.message, percent: payload.progress });

        if (payload.status === 'COMPLETE') {
          eventSource.close();
          setIsProcessing(false);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsProcessing(false);
      };
    } catch (err) {
      setIsProcessing(false);
      alert('Error initiating optimization session');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* Input Side Panel */}
      <div className="lg:col-span-5 space-y-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <h2 className="text-xl font-bold text-white mb-4">1. Document & Job Source</h2>
          
          <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 transition-colors p-6 rounded-xl text-center bg-slate-950/50 cursor-pointer">
            <input 
              type="file" 
              accept=".pdf,.docx" 
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden" 
              id="cv-upload" 
            />
            <label htmlFor="cv-upload" className="cursor-pointer space-y-2 block">
              <span className="text-slate-300 font-medium block">
                {file ? file.name : "Drag & drop CV or click to browse"}
              </span>
              <span className="text-xs text-slate-500 block">PDF or DOCX (Max 10MB)</span>
            </label>
          </div>

          <div className="mt-4">
            <label className="text-xs font-semibold text-slate-400 mb-1 block">Target Job URL</label>
            <input
              type="url"
              placeholder="https://company.com/careers/job-id"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 text-sm"
            />
          </div>

          <button
            onClick={handleStartAnalysis}
            disabled={!file || !jobUrl || isProcessing}
            className="w-full mt-6 py-3 rounded-lg bg-indigo-600 disabled:bg-slate-800 hover:bg-indigo-500 text-white font-semibold transition-all cursor-pointer disabled:cursor-not-allowed"
          >
            {isProcessing ? "Processing..." : "Generate Optimized CV"}
          </button>
        </div>

        {isProcessing && (
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-3">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-indigo-400">{streamProgress.step}</span>
              <span className="text-slate-400">{streamProgress.percent}%</span>
            </div>
            <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
              <div 
                className="bg-indigo-500 h-full transition-all duration-300"
                style={{ width: `${streamProgress.percent}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Live Preview Panel */}
      <div className="lg:col-span-7 bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between min-h-[600px]">
        <div>
          <div className="flex justify-between items-center pb-4 border-b border-slate-800">
            <h3 className="text-lg font-bold text-white">Live Tailored Preview</h3>
            <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              Interactive Preview Mode
            </span>
          </div>

          <div className="mt-6 space-y-4 text-slate-300 text-sm">
            <p className="text-slate-500 italic">
              {isProcessing ? "Analyzing posting keywords and tailoring achievements..." : "Complete inputs and launch optimization to view ATS recommendations."}
            </p>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-800 flex justify-end">
          <button
            onClick={onExportRequested}
            className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold shadow-md transition-all cursor-pointer"
          >
            Export Optimized PDF
          </button>
        </div>
      </div>
    </div>
  );
}
