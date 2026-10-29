import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'
import ShareModal from '../../components/ShareModal'
import ApplyTrackerModal from '../../components/ApplyTrackerModal'
import SchemeReviewsSection from '../../components/SchemeReviewsSection'
import { exportSchemePdf } from '../../utils/pdfExport'

export default function SchemeDetail() {
  const { id } = useParams()
  const { t } = useTranslation()
  const [scheme, setScheme] = useState(null)
  const [loading, setLoading] = useState(true)
  const [eligibility, setEligibility] = useState(null)
  const [checking, setChecking] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [checkedDocs, setCheckedDocs] = useState({})

  // Modals state
  const [isShareOpen, setIsShareOpen] = useState(false)
  const [isApplyTrackerOpen, setIsApplyTrackerOpen] = useState(false)
  const [familyMembers, setFamilyMembers] = useState([])

  useEffect(() => {
    api.get(`/schemes/${id}`)
      .then(({ data }) => setScheme(data))
      .catch(() => toast.error('Could not load scheme details'))
      .finally(() => setLoading(false))

    // Check if saved
    api.get('/saved')
      .then(({ data }) => {
        setIsSaved(data.some((s) => s.scheme.id === Number(id)))
      })
      .catch(() => {})

    // Load family members for apply tracker modal dropdown
    api.get('/family')
      .then(({ data }) => setFamilyMembers(data))
      .catch(() => {})
  }, [id])

  const checkEligibility = async () => {
    setChecking(true)
    try {
      const { data } = await api.get(`/eligibility/check/${id}`)
      setEligibility(data)
      if (data.is_eligible) {
        toast.success('You are eligible for this scheme!')
      } else {
        toast('Check unmatched criteria below.', { icon: 'ℹ️' })
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not check eligibility')
    } finally {
      setChecking(false)
    }
  }

  const handleToggleSave = async () => {
    try {
      if (isSaved) {
        await api.delete(`/saved/${id}`)
        setIsSaved(false)
        toast.success('Removed from saved bookmarks')
      } else {
        await api.post(`/saved/${id}`)
        setIsSaved(true)
        toast.success('Scheme saved to bookmarks!')
      }
    } catch {
      toast.error('Action failed')
    }
  }

  const toggleDocCheck = (docId) => {
    setCheckedDocs((prev) => ({
      ...prev,
      [docId]: !prev[docId],
    }))
  }

  const handleDownloadPdf = () => {
    if (!scheme) return
    try {
      exportSchemePdf(scheme, eligibility, checkedDocs)
      toast.success('PDF Dossier downloaded!')
    } catch {
      toast.error('Failed to generate PDF')
    }
  }

  if (loading) return <LoadingSpinner text="Loading scheme details..." />
  if (!scheme) {
    return (
      <div className="text-center py-20 animate-fade-in">
        <span className="text-5xl">🔍</span>
        <h2 className="text-xl font-bold text-navy-900 mt-4">Scheme not found</h2>
        <p className="text-slate-500 mt-2">The requested welfare scheme may have been archived or removed.</p>
        <Link to="/schemes" className="btn-primary mt-4 inline-block">Browse All Schemes</Link>
      </div>
    )
  }

  const totalDocs = scheme.documents.length
  const readyDocsCount = scheme.documents.filter((d) => checkedDocs[d.id]).length
  const readinessPercent = totalDocs > 0 ? Math.round((readyDocsCount / totalDocs) * 100) : 0

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 animate-fade-in">
      {/* Modals */}
      <ShareModal
        scheme={scheme}
        isOpen={isShareOpen}
        onClose={() => setIsShareOpen(false)}
      />
      <ApplyTrackerModal
        scheme={scheme}
        isOpen={isApplyTrackerOpen}
        onClose={() => setIsApplyTrackerOpen(false)}
        familyMembers={familyMembers}
      />

      {/* Breadcrumbs and Action Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
        <nav className="text-slate-400">
          <Link to="/schemes" className="hover:text-navy-700 transition-colors">🏛️ Schemes</Link>
          <span className="mx-2">/</span>
          <span className="text-navy-900 font-medium">{scheme.title}</span>
        </nav>
        <div className="flex items-center gap-2">
          {/* Share Button */}
          <button
            onClick={() => setIsShareOpen(true)}
            className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3"
            title="Share via WhatsApp, Telegram, or Link"
          >
            <span>📱</span>
            <span>Share</span>
          </button>

          {/* Download PDF Button */}
          <button
            onClick={handleDownloadPdf}
            className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3 bg-red-50/50 hover:bg-red-50 text-red-700 border-red-200"
            title="Download PDF Dossier"
          >
            <span>📄</span>
            <span>Download PDF</span>
          </button>

          {/* Track Application Button */}
          <button
            onClick={() => setIsApplyTrackerOpen(true)}
            className="btn-secondary text-xs flex items-center gap-1.5 py-1.5 px-3 bg-blue-50/50 hover:bg-blue-50 text-blue-700 border-blue-200"
            title="Track your application progress"
          >
            <span>📋</span>
            <span>Track Application</span>
          </button>

          {/* Bookmark Button */}
          <button
            onClick={handleToggleSave}
            className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
              isSaved
                ? 'bg-clay-50 text-clay-700 border border-clay-200 hover:bg-clay-100'
                : 'bg-moss-50 text-moss-600 border border-moss-200 hover:bg-moss-100'
            }`}
          >
            {isSaved ? '★ Bookmarked' : '☆ Save Scheme'}
          </button>
        </div>
      </div>

      {/* Main Header Card */}
      <div className="card border-t-4 border-t-navy-700">
        <div className="flex flex-wrap items-start justify-between gap-4 mb-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="badge bg-navy-100 text-navy-800 font-semibold">{scheme.category || 'General'}</span>
              <span className="badge bg-slate-100 text-slate-700">📍 {scheme.state || 'All India'}</span>
              {scheme.target_group && (
                <span className="badge bg-clay-50 text-clay-700 ring-1 ring-clay-200">🎯 {scheme.target_group}</span>
              )}
            </div>
            <h1 className="page-title text-2xl md:text-3xl mt-2">{scheme.title}</h1>
            <p className="text-sm text-slate-500 mt-1 font-medium">🏢 {scheme.department}</p>
          </div>
        </div>

        <p className="text-slate-700 leading-relaxed mt-4 text-base">{scheme.description}</p>

        {/* Benefits Box */}
        {scheme.benefits && (
          <div className="mt-5 p-4 bg-gradient-to-br from-moss-50/80 to-emerald-50/50 rounded-xl border border-moss-200/80">
            <h3 className="font-semibold text-moss-700 text-sm mb-1.5 flex items-center gap-1.5">
              <span>💰</span>
              <span>Key Benefits & Entitlements</span>
            </h3>
            <p className="text-sm text-slate-800 leading-relaxed font-medium">{scheme.benefits}</p>
          </div>
        )}

        {/* Action Row */}
        <div className="mt-6 pt-5 border-t border-navy-100 flex flex-wrap items-center justify-between gap-3">
          <button
            onClick={checkEligibility}
            disabled={checking}
            className="btn-primary flex items-center gap-2 text-sm"
          >
            <span>{checking ? '⏳' : '⚡'}</span>
            <span>{checking ? 'Evaluating...' : 'Check My Eligibility'}</span>
          </button>

          {scheme.official_link && (
            <a
              href={scheme.official_link}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-navy-700 hover:text-navy-900 bg-navy-50 hover:bg-navy-100 border border-navy-200 px-3.5 py-2 rounded-lg transition-colors"
            >
              <span>🔒 Official Portal</span>
              <span>↗</span>
            </a>
          )}
        </div>

        {/* Real-Time Rule Evaluator Results Box */}
        {eligibility && (
          <div className="mt-6 animate-slide-up">
            <div
              className={`p-5 rounded-xl border ${
                eligibility.is_eligible
                  ? 'bg-moss-50/90 border-moss-300 ring-2 ring-moss-200'
                  : 'bg-clay-50/90 border-clay-300 ring-2 ring-clay-200'
              }`}
            >
              <div className="flex items-center justify-between gap-4 mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{eligibility.is_eligible ? '🎉' : '⚠️'}</span>
                  <div>
                    <p className="font-bold text-lg text-slate-900">
                      Match Score: {eligibility.match_score}%
                    </p>
                    <p
                      className={`text-sm font-semibold ${
                        eligibility.is_eligible ? 'text-moss-700' : 'text-clay-700'
                      }`}
                    >
                      {eligibility.is_eligible
                        ? '✓ You meet all specified eligibility criteria!'
                        : '✕ Not fully eligible based on your current profile'}
                    </p>
                  </div>
                </div>
                <Link to="/profile" className="btn-secondary text-xs whitespace-nowrap">
                  Edit Profile ✏️
                </Link>
              </div>

              {eligibility.matched_reasons.length > 0 && (
                <div className="mb-3 bg-white/80 rounded-lg p-3 border border-moss-200">
                  <p className="text-xs font-bold text-moss-700 uppercase tracking-wide mb-2">
                    Criteria Met ({eligibility.matched_reasons.length}):
                  </p>
                  <ul className="space-y-1.5">
                    {eligibility.matched_reasons.map((r, i) => (
                      <li key={i} className="text-sm text-slate-800 flex items-start gap-2">
                        <span className="text-moss-600 font-bold">✓</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {eligibility.unmatched_reasons.length > 0 && (
                <div className="bg-white/80 rounded-lg p-3 border border-clay-200">
                  <p className="text-xs font-bold text-clay-700 uppercase tracking-wide mb-2">
                    Criteria Not Met ({eligibility.unmatched_reasons.length}):
                  </p>
                  <ul className="space-y-1.5">
                    {eligibility.unmatched_reasons.map((r, i) => (
                      <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                        <span className="text-clay-600 font-bold">✕</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Interactive Document Readiness Tracker */}
      {scheme.documents && scheme.documents.length > 0 && (
        <div className="card">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <div>
              <h3 className="section-title">📄 Required Documents & Readiness Tracker</h3>
              <p className="text-xs text-slate-500 mt-0.5">Check off documents you have ready before applying</p>
            </div>
            <div className="flex items-center gap-2 bg-navy-50 px-3 py-1.5 rounded-lg border border-navy-100">
              <span className="text-xs font-semibold text-navy-800">
                Readiness: {readyDocsCount}/{totalDocs} ({readinessPercent}%)
              </span>
            </div>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-navy-100 rounded-full h-2 mb-4 overflow-hidden">
            <div
              className={`h-2 transition-all duration-300 ${
                readinessPercent === 100 ? 'bg-moss-500' : 'bg-navy-600'
              }`}
              style={{ width: `${readinessPercent}%` }}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {scheme.documents.map((d) => (
              <label
                key={d.id}
                onClick={() => toggleDocCheck(d.id)}
                className={`flex items-center gap-3 p-3 rounded-lg border text-sm cursor-pointer transition-all ${
                  checkedDocs[d.id]
                    ? 'bg-moss-50/80 border-moss-300 text-slate-900'
                    : 'bg-navy-50/40 border-navy-200/70 hover:bg-navy-50 text-slate-700'
                }`}
              >
                <input
                  type="checkbox"
                  checked={!!checkedDocs[d.id]}
                  onChange={() => {}}
                  className="rounded text-navy-700 focus:ring-navy-500 w-4 h-4"
                />
                <div className="flex-1">
                  <span className={checkedDocs[d.id] ? 'font-medium line-through text-slate-500' : 'font-medium'}>
                    {d.document_name}
                  </span>
                  {!d.is_mandatory && <span className="text-xs text-slate-400 ml-1.5">(Optional)</span>}
                  {d.is_mandatory && <span className="text-xs text-red-500 ml-1.5 font-semibold">*Mandatory</span>}
                </div>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Step-by-Step Application Guide */}
      {scheme.steps && scheme.steps.length > 0 && (
        <div className="card">
          <h3 className="section-title mb-4">📝 Step-by-Step How to Apply</h3>
          <div className="space-y-4">
            {scheme.steps
              .sort((a, b) => a.step_number - b.step_number)
              .map((s) => (
                <div key={s.id} className="flex gap-3.5 items-start">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-navy-800 text-white flex items-center justify-center text-sm font-bold shadow-sm">
                    {s.step_number}
                  </div>
                  <div className="pt-1 text-sm text-slate-800 leading-relaxed font-medium">
                    {s.instruction}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Scheme Reviews & Ratings Section */}
      <SchemeReviewsSection schemeId={scheme.id} />

      {/* Bottom Back Button */}
      <Link
        to="/schemes"
        className="text-sm font-medium text-navy-600 hover:text-navy-900 hover:underline self-start mb-6 inline-flex items-center gap-1.5"
      >
        <span>← Back to Scheme Catalog</span>
      </Link>
    </div>
  )
}
