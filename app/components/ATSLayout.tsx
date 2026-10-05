interface ResumeData {
  name: string;
  title: string;
  contact: { phone: string; email: string; location: string; linkedin: string; availability?: string };
  summary: string;
  skills: { core: string[]; tools: string[]; soft: string[] };
  experience: Array<{ role: string; company: string; period: string; summary_line?: string; bullets: string[] }>;
  education: Array<{ degree: string; institution: string; year: string }>;
  languages: string[];
  interests: string[];
}

export default function ATSLayout({ data }: { data: ResumeData }) {
  return (
    <div className="max-w-[800px] mx-auto p-8 bg-white text-gray-900 font-sans leading-relaxed text-sm">
      {/* Centered Header */}
      <div className="text-center border-b pb-4 mb-6 border-gray-300">
        <h1 className="text-2xl font-bold uppercase tracking-wide text-gray-900">{data.name}</h1>
        <p className="text-md font-semibold text-blue-700 mt-1">{data.title}</p>
        <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-600 mt-2">
          <span>{data.contact.phone}</span> • <span>{data.contact.email}</span> • <span>{data.contact.location}</span>
          {data.contact.linkedin && <> • <span>{data.contact.linkedin}</span></>}
          {data.contact.availability && <> • <span>Availability: {data.contact.availability}</span></>}
        </div>
      </div>

      {/* Professional Summary */}
      <section className="mb-6">
        <h2 className="text-xs font-bold uppercase tracking-wider text-blue-800 border-b pb-1 mb-2">
          Professional Summary
        </h2>
        <p className="text-gray-800 leading-snug text-justify">{data.summary}</p>
      </section>

      {/* Key Skills */}
      <section className="mb-6">
        <h2 className="text-xs font-bold uppercase tracking-wider text-blue-800 border-b pb-1 mb-2">
          Key Skills
        </h2>
        <div className="space-y-1 text-xs">
          <p><strong>Core Competencies:</strong> {data.skills.core.join(", ")}</p>
          <p><strong>Tools & Analytics:</strong> {data.skills.tools.join(", ")}</p>
          <p><strong>Soft Skills:</strong> {data.skills.soft.join(", ")}</p>
        </div>
      </section>

      {/* Work Experience */}
      <section className="mb-6">
        <h2 className="text-xs font-bold uppercase tracking-wider text-blue-800 border-b pb-1 mb-3">
          Work Experience
        </h2>
        {data.experience.map((exp, idx) => (
          <div key={idx} className="mb-4">
            <div className="flex justify-between font-bold text-gray-900">
              <span>{exp.role} | <span className="font-normal italic">{exp.company}</span></span>
              <span>{exp.period}</span>
            </div>
            {exp.summary_line && <p className="text-xs italic text-gray-600 my-1">{exp.summary_line}</p>}
            <ul className="list-disc list-inside text-xs text-gray-800 space-y-1 mt-1">
              {exp.bullets.map((bullet, i) => (
                <li key={i}>{bullet}</li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      {/* Education */}
      <section className="mb-6">
        <h2 className="text-xs font-bold uppercase tracking-wider text-blue-800 border-b pb-1 mb-2">
          Education & Certifications
        </h2>
        <div className="space-y-1 text-xs">
          {data.education.map((edu, idx) => (
            <div key={idx} className="flex justify-between">
              <span><strong>{edu.degree}</strong> | {edu.institution}</span>
              <span>{edu.year}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Languages & Interests */}
      {(data.languages.length > 0 || data.interests.length > 0) && (
        <section className="grid grid-cols-2 gap-4 text-xs">
          {data.languages.length > 0 && (
            <div>
              <h3 className="font-bold uppercase text-blue-800 border-b pb-1 mb-1">Languages</h3>
              <p>{data.languages.join(" • ")}</p>
            </div>
          )}
          {data.interests.length > 0 && (
            <div>
              <h3 className="font-bold uppercase text-blue-800 border-b pb-1 mb-1">Interests</h3>
              <p>{data.interests.join(" • ")}</p>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
