'use client';

import React from 'react';

export function AuthRetentionModal({ 
  onClose, 
  onSuccess 
}: { 
  onClose: () => void; 
  onSuccess: () => void; 
}) {
  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full relative shadow-2xl space-y-6">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-500 hover:text-white text-lg"
        >
          ✕
        </button>

        <div className="text-center space-y-2">
          <h3 className="text-2xl font-bold text-white">Save Your Optimized CV</h3>
          <p className="text-sm text-slate-400">
            Create an account to export high-resolution PDFs and store variations for different job applications.
          </p>
        </div>

        <div className="space-y-3">
          <button 
            onClick={onSuccess}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl bg-white text-slate-950 font-semibold hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <span>Continue with Google</span>
          </button>
          
          <button 
            onClick={onSuccess}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold transition-colors cursor-pointer"
          >
            <span>Continue with Apple</span>
          </button>
        </div>

        <div className="relative flex items-center justify-center">
          <div className="border-t border-slate-800 w-full" />
          <span className="bg-slate-900 px-3 text-xs text-slate-500 absolute">OR EMAIL</span>
        </div>

        <form onSubmit={(e) => { e.preventDefault(); onSuccess(); }} className="space-y-4">
          <input
            type="email"
            required
            placeholder="name@example.com"
            className="w-full px-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 text-sm"
          />
          <button
            type="submit"
            className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-all cursor-pointer"
          >
            Save & Export Document
          </button>
        </form>
      </div>
    </div>
  );
}
