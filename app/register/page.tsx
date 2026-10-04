'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function Register() {
  const router = useRouter()

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    acceptTerms: false
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleOAuthDemo = (providerName: string) => {
    if (!formData.acceptTerms) {
      setError('Please accept the Terms of Service and Privacy Policy to continue.')
      return
    }
    setError('')
    setSuccess(`Signing in with ${providerName}... Redirecting to dashboard.`)
    setTimeout(() => {
      router.push('/dashboard')
    }, 1000)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!formData.acceptTerms) {
      setError('Please accept the Terms of Service and Privacy Policy.')
      return
    }

    setLoading(true)

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const data = await res.json().catch(() => ({}))

      if (!res.ok) {
        throw new Error(data.error || 'Failed to create account.')
      }

      setSuccess('Account created successfully! Redirecting...')
      setTimeout(() => {
        router.push('/dashboard')
      }, 1000)
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-white text-[#143a52] px-5 py-6 max-w-md mx-auto flex flex-col justify-between">
      <div>
        {/* Top Controls */}
        <div className="flex items-center justify-between mb-8">
          <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 text-xl font-bold">
            &larr;
          </Link>

          <Link href="/" className="flex items-center gap-2">
            <div className="bg-[#134e6f] p-1.5 rounded-lg text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <span className="font-serif font-bold text-2xl text-[#0d2838]">
              cvforge<span className="text-amber-500">.</span>
            </span>
          </Link>

          <span className="text-lg" aria-label="UK Flag">🇬🇧</span>
        </div>

        <h1 className="font-serif font-extrabold text-3xl text-[#0d2838] mb-2">
          Welcome.
        </h1>
        <p className="text-gray-500 text-xs sm:text-sm mb-6 leading-normal">
          One account = your resumes saved, your credits kept, zero loss.
        </p>

        {/* Dynamic Alerts */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 mb-4 font-medium">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 text-xs rounded-xl p-3 mb-4 font-medium">
            {success}
          </div>
        )}

        {/* Terms Box */}
        <div className="bg-[#fffdf0] border border-amber-200 rounded-xl p-3.5 mb-6 flex items-start gap-3">
          <input
            type="checkbox"
            id="acceptTerms"
            name="acceptTerms"
            checked={formData.acceptTerms}
            onChange={handleChange}
            className="mt-1 rounded border-gray-300 text-[#134e6f] focus:ring-0 cursor-pointer"
          />
          <label htmlFor="acceptTerms" className="text-xs text-amber-900 font-medium leading-relaxed cursor-pointer">
            <span className="font-bold flex items-center gap-1 text-amber-950 mb-0.5">
              🛡️ Required to sign up
            </span>
            I accept the <a href="#" className="underline font-semibold">Terms of Service</a> and the <a href="#" className="underline font-semibold">Privacy Policy</a>.
          </label>
        </div>

        {/* OAuth Buttons (Demo Mode) */}
        <div className="space-y-3 mb-6">
          <button
            type="button"
            onClick={() => handleOAuthDemo('Google')}
            className="w-full border border-gray-300 rounded-full py-2.5 px-4 flex items-center justify-center gap-3 font-medium text-xs text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
            </svg>
            <span>Continue with Google</span>
          </button>

          <button
            type="button"
            onClick={() => handleOAuthDemo('Apple')}
            className="w-full bg-black text-white rounded-full py-2.5 px-4 flex items-center justify-center gap-3 font-medium text-xs hover:bg-gray-900 transition-colors"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.32c.62-.75 1.04-1.8 0.92-2.85-.9.04-2 0.6-2.65 1.35-.58.67-1.09 1.75-.95 2.78 1.01.08 2.05-.53 2.68-1.28z" />
            </svg>
            <span>Continue with Apple</span>
          </button>
        </div>

        {/* Divider */}
        <div className="relative flex py-2 items-center mb-6">
          <div className="flex-grow border-t border-gray-200"></div>
          <span className="flex-shrink mx-4 text-[10px] font-bold text-gray-400 tracking-wider uppercase">
            OR WITH YOUR EMAIL
          </span>
          <div className="flex-grow border-t border-gray-200"></div>
        </div>

        {/* Email Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">First name</label>
              <input
                type="text"
                name="firstName"
                required
                placeholder="First name"
                value={formData.firstName}
                onChange={handleChange}
                className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-xs focus:ring-1 focus:ring-[#134e6f] focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Last name</label>
              <input
                type="text"
                name="lastName"
                required
                placeholder="Last name"
                value={formData.lastName}
                onChange={handleChange}
                className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-xs focus:ring-1 focus:ring-[#134e6f] focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Email address</label>
            <input
              type="email"
              name="email"
              required
              placeholder="you@email.com"
              value={formData.email}
              onChange={handleChange}
              className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-xs focus:ring-1 focus:ring-[#134e6f] focus:outline-none"
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
              minLength={8}
              placeholder="At least 8 characters"
              value={formData.password}
              onChange={handleChange}
              className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-xs focus:ring-1 focus:ring-[#134e6f] focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#134e6f] text-white font-medium text-sm py-3 rounded-full hover:bg-[#0f3d57] transition-colors mt-2 disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>
      </div>
    </main>
  )
}
