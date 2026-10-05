import { NextResponse } from 'next/server'

export async function POST(req: Request) {
  try {
    const { jobUrl, baseCvText, user } = await req.json()

    // Place your AI prompt engineering logic here (e.g., OpenAI / Gemini API call)
    // The prompt extracts job requirements from `jobUrl` and tailors `baseCvText` into an ATS format.

    // Simulated dynamic response tailored to the job posting
    const dynamicAiResult = {
      jobTitle: "Digital Marketing Specialist",
      company: "The Home Depot",
      source: "LinkedIn",
      atsScoreBefore: 48,
      atsScoreAfter: 88,
      matchingBefore: 42,
      matchingAfter: 85,
      optimizedResume: {
        fullName: user?.fullName || "KEDIR ABDELA",
        titleWithExp: "Digital Marketing Specialist (5 yrs exp)",
        contactLine: `${user?.phone || '0908706534'} | ${user?.email || 'nmtullah86@gmail.com'} | ${user?.location || 'Los Angeles'} | linkedin.com/in/kedirmohammed`,
        summary: `Results-driven Digital Marketing Specialist with 5+ years of experience designing data-driven campaigns for e-commerce and retail leaders matching requirements for ${jobUrl.includes('linkedin') ? 'LinkedIn job posting' : 'the target role'}. Proven track record in SEO, paid advertising, and high-converting funnel strategy with measurable impact on audience engagement.`,
        skills: [
          { category: "Digital Marketing", list: "SEO, Social Media Marketing, Paid Advertising, Email Marketing, Campaign Analysis, CRO" },
          { category: "Tools & Analytics", list: "Google Analytics (Certified), Google Ads Search, HubSpot, Performance Dashboards, Meta Ads Manager" }
        ],
        experience: [
          {
            role: "Digital Marketing Specialist",
            company: "BrightWave Media",
            period: "2022 - Present",
            description: "Led end-to-end digital marketing campaigns across major platforms, driving measurable growth in traffic (+45%) and brand visibility aligned with target e-commerce KPIs."
          },
          {
            role: "Marketing Coordinator",
            company: "NovaTech Solutions",
            period: "2019 - 2022",
            description: "Supported social media operations and boosted engagement by 30% through optimized content scheduling and target audience segmentation."
          }
        ],
        educationAndCerts: [
          "Bachelor of Business Administration | New York University",
          "Google Analytics Certification (2023)",
          "Google Ads Search Certification (2023)",
          "HubSpot Content Marketing Certification (2022)"
        ]
      }
    }

    return NextResponse.json({ success: true, data: dynamicAiResult })
  } catch (error) {
    return NextResponse.json({ success: false, error: 'Failed to optimize resume' }, { status: 500 })
  }
}
