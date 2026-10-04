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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

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

      // Save user details for top header badge & dashboard salutation
      if (typeof window !== 'undefined') {
        localStorage.setItem('cvforge_user_name', formData.firstName)
        localStorage.setItem('cvforge_user_email', formData.email)
      }

      router.push('/dashboard')
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

        <h1 className="font-serif font-extrabold text-3xl text-[#0d2838] mb-2">Welcome.</h1>
        <p className="text-gray-500 text-xs sm:text-sm mb-6 leading-normal">
          One account = your resumes saved, your credits kept, zero loss.
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 mb-4 font-medium">
            {error}
          </div>
        )}

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
