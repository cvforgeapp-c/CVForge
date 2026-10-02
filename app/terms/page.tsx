import Link from 'next/link';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white text-[#0F2942] py-12 px-6 max-w-3xl mx-auto space-y-6">
      <Link href="/" className="text-xl font-bold tracking-tight">
        <span>cvforge</span><span className="text-amber-500">.</span>
      </Link>
      <h1 className="text-3xl font-serif font-bold">Terms of Service</h1>
      <p className="text-xs text-gray-500">Last updated: October 2026</p>

      <section className="space-y-3 text-sm text-gray-700 leading-relaxed">
        <p>Welcome to CVForge. By creating an account or using our resume generation services, you agree to these terms.</p>
        <h2 className="text-base font-bold text-[#0F2942]">1. Service Usage</h2>
        <p>CVForge provides AI-assisted document parsing, tailoring, and PDF compilation. Users retain ownership of all uploaded personal information.</p>
        <h2 className="text-base font-bold text-[#0F2942]">2. Credit Billing & Paddle Gateway</h2>
        <p>Purchases and subscriptions are processed securely via Paddle. Purchased credits remain active on your registered profile.</p>
      </section>
    </div>
  );
}
