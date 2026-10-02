import Link from 'next/link';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white text-[#0F2942] py-12 px-6 max-w-3xl mx-auto space-y-6">
      <Link href="/" className="text-xl font-bold tracking-tight">
        <span>cvforge</span><span className="text-amber-500">.</span>
      </Link>
      <h1 className="text-3xl font-serif font-bold">Privacy Policy</h1>
      <p className="text-xs text-gray-500">Last updated: October 2026</p>

      <section className="space-y-3 text-sm text-gray-700 leading-relaxed">
        <p>Your privacy is important to us. CVForge processes uploaded resume documents solely for content tailoring and document formatting.</p>
        <h2 className="text-base font-bold text-[#0F2942]">Data Protection</h2>
        <p>We do not sell, share, or monetize candidate data or uploaded resumes. Extracted text is stored in secure encrypted database environments.</p>
      </section>
    </div>
  );
}
