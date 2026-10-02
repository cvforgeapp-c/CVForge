'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function SignupPage() {
  const router = useRouter();

  // Integrated Form & Submission States
  const [accepted, setAccepted] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    if (!accepted) {
      setErrorMsg('You must accept the terms of service to sign up.');
      return;
    }

    if (!formData.email || !formData.password) {
      setErrorMsg('Please enter a valid email and password.');
      return;
    }

    if (formData.password.length < 8) {
      setErrorMsg('Your password must contain at least 8 characters.');
      return;
    }

    setLoading(true);

    try {
      // 1. Send Signup Request
      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Signup failed. Please try again.');
      }

      // 2. Perform Automatic Login Session Link
      let token = data.token;
      let user = data.user;

      if (!token) {
        // Fallback login request if signup didn't return token directly
        const loginRes = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
          }),
        });

        const loginData = await loginRes.json();
        if (loginRes.ok) {
          token = loginData.token;
          user = loginData.user;
        }
      }

      // 3. Store JWT Session Token & Link Saved Files/State
      if (token) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
      }

      // Redirect to Dashboard with active session
      router.push('/dashboard');
    } catch (err: any) {
      setErrorMsg(err.message || 'Server connection error.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center px-6 py-12 text-[#0F2942]">
      <div className="max-w-md w-full space-y-6">
        
        {/* Header Logo & Notice */}
        <div className="text-center">
          <Link href="/" className="text-2xl font-bold tracking-tight inline-block mb-1">
            <span>cvforge</span>
            <span className="text-amber-500">.</span>
          </Link>
          <p className="text-sm text-gray-600">
            One account = your resumes saved, your credits kept, zero loss.
          </p>
        </div>

        {/* Backend Error Banner */}
        {errorMsg && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-xs font-medium text-center">
            {errorMsg}
          </div>
        )}

        {/* Terms Box */}
        <div className="bg-[#FFFDF0] border border-[#FDE68A] rounded-xl p-4 flex items-start space-x-3">
          <input 
            type="checkbox" 
            checked={accepted} 
            onChange={(e) => setAccepted(e.target.checked)}
            className="mt-1 h-4 w-4 rounded border-gray-300 text-[#0F2942] focus:ring-[#0F2942]"
          />
          <div className="text-xs text-amber-900">
            <span className="font-semibold block mb-0.5">🛡️ Required to sign up</span>
            I accept the <Link href="/terms" className="underline">Terms of Service</Link> and the <Link href="/privacy" className="underline">Privacy Policy</Link>.
          </div>
        </div>

        {/* OAuth Buttons */}
        <div className="space-y-3">
          <button 
            type="button"
            className="w-full bg-white border border-gray-300 rounded-full py-3 px-4 flex items-center justify-center space-x-2 font-medium text-sm hover:bg-gray-50 transition shadow-sm"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Continue with Google</span>
          </button>
          
          <button 
            type="button"
            className="w-full bg-black text-white rounded-full py-3 px-4 flex items-center justify-center space-x-2 font-medium text-sm hover:bg-opacity-90 transition shadow-sm"
          >
            <span className="text-base"></span>
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
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">First name</label>
              <input 
                type="text" 
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="First name" 
                className="w-full border border-gray-300 rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]" 
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Last name</label>
              <input 
                type="text" 
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Last name" 
                className="w-full border border-gray-300 rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]" 
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Email address</label>
            <input 
              type="email" 
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              placeholder="you@email.com" 
              className="w-full border border-gray-300 rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]" 
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              Password <span className="text-red-500">*</span>
            </label>
            <input 
              type="password" 
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              placeholder="At least 8 characters" 
              className="w-full border border-gray-300 rounded-xl p-3 text-sm focus:outline-none focus:border-[#0F2942]" 
            />
            <p className="text-[11px] text-gray-400 mt-1">
              Your password must contain at least 8 characters, one letter and one number.
            </p>
          </div>

          <button
            type="submit"
            disabled={!accepted || loading}
            className={`w-full py-3.5 rounded-full font-semibold text-white transition ${
              accepted && !loading 
                ? 'bg-[#0F2942] hover:bg-opacity-90 cursor-pointer shadow-sm' 
                : 'bg-gray-400 cursor-not-allowed'
            }`}
          >
            {loading ? 'Creating my account...' : 'Create my account →'}
          </button>
        </form>

        <p className="text-center text-xs text-gray-600 pt-2">
          Already have an account?{' '}
          <Link href="/auth/login" className="font-semibold text-[#0F2942] underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
