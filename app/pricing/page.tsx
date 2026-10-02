'use client';

import { useState } from 'react';

export default function PricingPage() {
  const [billingType, setBillingType] = useState<'subscriptions' | 'packs'>('subscriptions');

  const plans = [
    {
      name: 'Starter',
      price: '$4.99',
      originalPrice: null,
      discountBadge: null,
      credits: '15 credits/month',
      unitCost: '$0.33 / credit',
      isPopular: false,
      buttonColor: 'bg-[#0F2942] hover:bg-opacity-95 text-white',
      cardStyle: 'bg-white border-gray-100',
      features: [
        { text: 'ATS Optimization', included: true },
        { text: 'Resume Tailoring to Job Posting', included: true },
        { text: 'Edit Optimized Resume', included: true },
        { text: 'Cover Letter Generation', included: true },
        { text: 'Interview Pitch & Preparation Advice', included: true },
        { text: 'Detailed Match Scores', included: true },
        { text: 'Priority Support', included: false },
        { text: 'MCP Access for Automation', included: false },
      ],
    },
    {
      name: 'Pro',
      price: '$12.99',
      originalPrice: '$16.63',
      discountBadge: 'SAVE 22%',
      credits: '50 credits/month',
      unitCost: '$0.26 / credit',
      isPopular: true,
      buttonColor: 'bg-[#C28E2B] hover:bg-opacity-90 text-white',
      cardStyle: 'bg-[#FFFDF7] border-[#E8C574] ring-1 ring-[#E8C574]',
      features: [
        { text: 'ATS Optimization', included: true },
        { text: 'Resume Tailoring to Job Posting', included: true },
        { text: 'Edit Optimized Resume', included: true },
        { text: 'Cover Letter Generation', included: true },
        { text: 'Interview Pitch & Preparation Advice', included: true },
        { text: 'Detailed Match Scores', included: true },
        { text: 'Priority Support', included: false },
        { text: 'MCP Access for Automation', included: false },
      ],
    },
    {
      name: 'Expert',
      price: '$29.99',
      originalPrice: '$49.90',
      discountBadge: 'SAVE 40%',
      credits: '150 credits/month',
      unitCost: '$0.20 / credit',
      isPopular: false,
      buttonColor: 'bg-[#0F2942] hover:bg-opacity-95 text-white',
      cardStyle: 'bg-white border-gray-100',
      features: [
        { text: 'ATS Optimization', included: true },
        { text: 'Resume Tailoring to Job Posting', included: true },
        { text: 'Edit Optimized Resume', included: true },
        { text: 'Cover Letter Generation', included: true },
        { text: 'Interview Pitch & Preparation Advice', included: true },
        { text: 'Detailed Match Scores', included: true },
        { text: 'Priority Support', included: true },
        { text: 'MCP Access for Automation', included: true },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F2942] py-12 px-4">
      <div className="max-w-md mx-auto text-center">
        <h1 className="text-3xl font-serif font-bold mb-6">Choose your plan</h1>

        {/* Toggle */}
        <div className="bg-[#EBF2F7] p-1 rounded-full inline-flex mb-2">
          <button
            onClick={() => setBillingType('subscriptions')}
            className={`px-6 py-2 rounded-full text-xs font-semibold transition ${
              billingType === 'subscriptions' ? 'bg-[#0F2942] text-white' : 'text-gray-600'
            }`}
          >
            Subscriptions
          </button>
          <button
            onClick={() => setBillingType('packs')}
            className={`px-6 py-2 rounded-full text-xs font-semibold transition ${
              billingType === 'packs' ? 'bg-[#0F2942] text-white' : 'text-gray-600'
            }`}
          >
            Packs
          </button>
        </div>
        <p className="text-xs text-gray-400 italic mb-8">Monthly payment, cancel anytime.</p>

        {/* Pricing Cards */}
        <div className="space-y-6">
          {plans.map((plan, idx) => (
            <div key={idx} className="relative">
              {plan.isPopular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-[#C28E2B] text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider z-10 shadow-sm">
                  ★ Popular
                </div>
              )}

              <div className={`rounded-3xl border p-6 shadow-sm relative ${plan.cardStyle}`}>
                {/* Discount Badge Header */}
                {plan.discountBadge && (
                  <span className="absolute top-4 right-4 bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2.5 py-0.5 rounded-full">
                    {plan.discountBadge}
                  </span>
                )}

                <h2 className="text-lg font-bold text-[#0F2942]">{plan.name}</h2>
                
                <div className="my-3 flex items-baseline justify-center space-x-2">
                  {plan.originalPrice && (
                    <span className="text-sm text-gray-400 line-through font-serif">
                      {plan.originalPrice}
                    </span>
                  )}
                  <span className="text-3xl font-bold font-serif">{plan.price}</span>
                  <span className="text-xs text-gray-500"> /month</span>
                </div>

                <p className="text-xs font-semibold text-[#3B7A9E]">{plan.credits}</p>
                <p className="text-[10px] text-gray-400 mb-6">{plan.unitCost}</p>

                {/* Features */}
                <ul className="text-left space-y-3 text-xs mb-8">
                  {plan.features.map((feat, fIdx) => (
                    <li
                      key={fIdx}
                      className={`flex items-start space-x-2.5 ${
                        feat.included ? 'text-gray-700' : 'text-gray-300 line-through'
                      }`}
                    >
                      <span className="shrink-0">{feat.included ? '✓' : '✕'}</span>
                      <span>{feat.text}</span>
                    </li>
                  ))}
                </ul>

                <button
                  className={`w-full py-3.5 rounded-full font-semibold text-xs transition shadow-sm ${plan.buttonColor}`}
                >
                  Subscribe
                </button>
              </div>
            </div>
          ))}
        </div>

        <p className="text-[10px] text-gray-400 mt-6">
          By clicking Subscribe, I accept the{' '}
          <a href="/terms" className="underline">
            Terms of Sale
          </a>{' '}
          and the immediate performance of the service.
        </p>
      </div>
    </div>
  );
}
