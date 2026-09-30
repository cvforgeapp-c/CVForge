'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function SignupPage() {
  const [accepted, setAccepted] = useState(false);

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center px-6 py-12 text-[#0F2942]">
      <div className="max-w-md w-full space-y-6">
        <p className="text-center text-sm text-gray-600">
          One account = your resumes saved, your credits kept, zero loss.
        </p>

        {/* Terms Box */}
        <div className="bg-[#FFFDF0] border border-[#FDE68A] rounded-xl p-4 flex items-start space-x-3">
          <input 
            type="checkbox" 
            checked={accepted} 
            onChange={(e) => setAccepted(e.target.checked)}
            className="mt-1 h-4 w-4 rounded border-gray-300 text-[#0F2942]"
          />
          <div className="text-xs text-amber-900">
            <span className="font-semibold block mb-0.5">🛡️ Required to sign up</span>
            I accept the <a href="#" className="underline">Terms of Service</a> and the <a href="#" className="underline">Privacy Policy</a>.
          </div>
        </div>

        {/* OAuth Buttons */}
        <div className="space-y-3">
          <button className="w-full bg-white border border-gray-300 rounded-full py-3 px-4 flex items-center justify-center space-x-2 font-medium text-sm hover:bg-gray-50 transition shadow-sm">
            <span>Google Icon</span>
            <span>Continue with Google</span>
          </button>
          <button className="w-full bg-black text-white rounded-full py-3 px-4 flex items-center justify-center space-x-2 font-medium text-sm hover:bg-opacity-90 transition shadow-sm">
            <span></span>
            <span>Continue with Apple</span>
          </button>
        </div>

        <div className="relative flex items-center justify-center my-4">
          <div className="border-t border-gray-200 w-full"></div>
          <span className="bg-[#F8FAFC] px-3 text-[11px] text-gray-400 font-semibold tracking-wider uppercase absolute">
            OR WITH YOUR EMAIL
          </span>
        </div>

        {/* Registration Form */}
        <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">First name</label>
              <input type="text" placeholder="First name" className="w-full border border-gray-300 rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Last name</label>
              <input type="text" placeholder="Last name" className="w-full border border-gray-300 rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Email address</label>
            <input type="email" placeholder="you@email.com" className="w-full border border-gray-300 rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]" />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Password <span className="text-red-500">*</span></label>
            <input type="password" placeholder="At least 8 characters" className="w-full border border-gray-300 rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]" />
            <p className="text-[11px] text-gray-400 mt-1">Your password must contain at least 8 characters, one letter and one number.</p>
          </div>

          <button
            type="submit"
            disabled={!accepted}
            className={`w-full py-3.5 rounded-full font-semibold text-white transition ${accepted ? 'bg-[#0F2942] hover:bg-opacity-90' : 'bg-gray-400 cursor-not-allowed'}`}
          >
            Create my account &rarr;
          </button>
        </form>

        <p className="text-center text-xs text-gray-600 pt-2">
          Already have an account? <Link href="/auth/signin" className="font-semibold text-[#0F2942] underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
