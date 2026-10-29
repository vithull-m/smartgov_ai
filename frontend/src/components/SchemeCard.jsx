import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

const CATEGORY_COLORS = {
  'Education': 'bg-blue-50 text-blue-700 border-blue-200',
  'Agriculture': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Healthcare': 'bg-rose-50 text-rose-700 border-rose-200',
  'Housing': 'bg-violet-50 text-violet-700 border-violet-200',
  'Women Welfare': 'bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200',
  'Employment & Business': 'bg-amber-50 text-amber-800 border-amber-200',
  'Senior Citizens': 'bg-teal-50 text-teal-700 border-teal-200',
  'Disability Support': 'bg-indigo-50 text-indigo-700 border-indigo-200',
}

export default function SchemeCard({ scheme, matchScore, isEligible, onSave, saved }) {
  const { t } = useTranslation()
  const catStyle = CATEGORY_COLORS[scheme.category] || 'bg-slate-100 text-slate-700 border-slate-200'

  return (
    <div className="card flex flex-col justify-between group hover:border-slate-300 hover:shadow-lg transition-all duration-200">
      <div>
        {/* Top Header Row */}
        <div className="flex items-start justify-between gap-3 mb-2.5">
          <div className="flex items-center gap-1.5 flex-wrap">
            {scheme.category && (
              <span className={`badge border text-[11px] font-semibold ${catStyle}`}>
                {scheme.category}
              </span>
            )}
            <span className="badge bg-slate-50 text-slate-600 border border-slate-200 text-[11px]">
              📍 {scheme.state || 'All India'}
            </span>
          </div>

          {matchScore !== undefined && (
            <span
              className={`badge shrink-0 text-xs font-bold ${
                isEligible
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-amber-50 text-amber-800 border border-amber-200'
              }`}
            >
              {matchScore}% Match
            </span>
          )}
        </div>

        {/* Scheme Title */}
        <h3 className="font-bold text-base text-slate-900 group-hover:text-blue-600 transition-colors leading-snug mb-1">
          {scheme.title}
        </h3>

        {/* Department */}
        {scheme.department && (
          <p className="text-xs text-slate-400 font-medium mb-2.5">
            🏢 {scheme.department}
          </p>
        )}

        {/* Description snippet */}
        <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-3 font-normal">
          {scheme.description}
        </p>

        {/* Target Group badge if available */}
        {scheme.target_group && (
          <div className="mb-3">
            <span className="inline-block text-[11px] font-medium text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
              🎯 Target: {scheme.target_group}
            </span>
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="pt-3 border-t border-slate-100 flex items-center gap-2 mt-auto">
        <Link
          to={`/schemes/${scheme.id}`}
          className="btn-secondary text-xs flex-1 text-center py-2 font-semibold"
        >
          {t('view_details')} →
        </Link>
        {onSave && (
          <button
            onClick={() => onSave(scheme.id)}
            className={`text-xs px-3 py-2 rounded-xl font-medium transition-all border ${
              saved
                ? 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'
                : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
            }`}
            title={saved ? 'Remove bookmark' : 'Save bookmark'}
          >
            {saved ? '★ Saved' : '☆ Save'}
          </button>
        )}
      </div>
    </div>
  )
}
