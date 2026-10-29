import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import api from '../../api/axios'
import { useAuth } from '../../context/AuthContext'
import LoadingSpinner from '../../components/LoadingSpinner'

export default function Dashboard() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/recommendations')
      .then(({ data }) => setResults(data))
      .catch((err) => setError(err.response?.data?.detail || 'Could not load recommendations.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner text="Computing personalized welfare recommendations..." />

  const eligibleCount = results.filter((r) => r.is_eligible).length
  const notEligibleCount = results.filter((r) => !r.is_eligible).length
  const avgScore = results.length > 0
    ? Math.round(results.reduce((sum, r) => sum + r.match_score, 0) / results.length)
    : 0

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-8 shadow-xl border border-slate-800">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-300 text-xs font-semibold mb-3">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>AI Welfare Match Engine Active</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Welcome back, {user?.full_name ? user.full_name.split(' ')[0] : 'Citizen'}!
            </h1>
            <p className="text-slate-300 text-sm mt-2 leading-relaxed">
              We evaluated your demographic profile against <strong>100+ state and central schemes</strong>. Below are programs where your household qualifies for direct benefits.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/schemes"
              className="inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all shadow-md shadow-blue-500/20"
            >
              Explore 100+ Schemes →
            </Link>
            <Link
              to="/profile"
              className="inline-flex items-center justify-center px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all"
            >
              Edit Profile ✏️
            </Link>
          </div>
        </div>

        {/* Decorative background glow */}
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />
      </div>

      {/* KPI Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card border-l-4 border-l-blue-600 flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Eligible Schemes</span>
            <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-2">{eligibleCount}</p>
          </div>
          <p className="text-xs text-emerald-600 font-semibold mt-3 flex items-center gap-1">
            <span>✓</span> 100% statutory match
          </p>
        </div>

        <div className="card border-l-4 border-l-indigo-600 flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Average Match</span>
            <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-2">{avgScore}%</p>
          </div>
          <p className="text-xs text-slate-500 mt-3 font-medium">
            Based on current profile
          </p>
        </div>

        <div className="card border-l-4 border-l-amber-500 flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Partial Match</span>
            <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-2">{notEligibleCount}</p>
          </div>
          <p className="text-xs text-amber-700 mt-3 font-semibold">
            Missing 1-2 criteria
          </p>
        </div>

        <div className="card border-l-4 border-l-emerald-600 flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Database Size</span>
            <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-2">101</p>
          </div>
          <p className="text-xs text-slate-500 mt-3 font-medium">
            Central & state verified
          </p>
        </div>
      </div>

      {/* Quick Access Feature Tiles */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        <Link
          to="/applications"
          className="card group hover:border-blue-300 hover:shadow-md transition-all p-4 flex items-center gap-3.5"
        >
          <div className="w-11 h-11 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
            📋
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
              Application Tracker
            </h4>
            <p className="text-[11px] text-slate-500 mt-0.5">Track your pipeline</p>
          </div>
        </Link>

        <Link
          to="/family"
          className="card group hover:border-indigo-300 hover:shadow-md transition-all p-4 flex items-center gap-3.5"
        >
          <div className="w-11 h-11 rounded-2xl bg-indigo-50 text-indigo-700 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
            👨‍👩‍👧
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
              Family Profile
            </h4>
            <p className="text-[11px] text-slate-500 mt-0.5">Household schemes</p>
          </div>
        </Link>

        <Link
          to="/compare"
          className="card group hover:border-amber-300 hover:shadow-md transition-all p-4 flex items-center gap-3.5"
        >
          <div className="w-11 h-11 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
            ⚖️
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 group-hover:text-amber-600 transition-colors">
              Compare Schemes
            </h4>
            <p className="text-[11px] text-slate-500 mt-0.5">Side-by-side specs</p>
          </div>
        </Link>

        <Link
          to="/chatbot"
          className="card group hover:border-emerald-300 hover:shadow-md transition-all p-4 flex items-center gap-3.5"
        >
          <div className="w-11 h-11 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
            💬
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 group-hover:text-emerald-600 transition-colors">
              Ask AI Assistant
            </h4>
            <p className="text-[11px] text-slate-500 mt-0.5">Multilingual guide</p>
          </div>
        </Link>
      </div>

      {/* Top Matching Schemes Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
              Recommended Schemes for You
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Ranked by compatibility with your age, income, and category criteria
            </p>
          </div>
          <Link
            to="/schemes"
            className="text-xs font-bold text-blue-600 hover:text-blue-700 hover:underline"
          >
            View All 101 Schemes →
          </Link>
        </div>

        {error && (
          <div className="alert-warning flex items-center justify-between">
            <span>{error}</span>
            <Link to="/profile" className="font-bold underline text-xs">
              Complete Profile
            </Link>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {results.slice(0, 8).map((r) => (
            <div
              key={r.scheme_id}
              className="card flex flex-col justify-between hover:border-slate-300 hover:shadow-md transition-all"
            >
              <div>
                <div className="flex justify-between items-start gap-3 mb-2">
                  <h3 className="font-bold text-base text-slate-900 leading-snug">
                    {r.title}
                  </h3>
                  <span
                    className={`badge shrink-0 ${
                      r.is_eligible
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}
                  >
                    {r.match_score}% Match
                  </span>
                </div>

                <p
                  className={`text-xs font-semibold mb-3 ${
                    r.is_eligible ? 'text-emerald-600' : 'text-amber-700'
                  }`}
                >
                  {r.is_eligible ? '● 100% Criteria Met' : '○ Review Conditions'}
                </p>

                {/* Match breakdown chips */}
                <div className="space-y-1.5 mb-4 text-xs">
                  {r.matched_reasons.slice(0, 2).map((m, idx) => (
                    <div key={idx} className="flex items-center gap-1.5 text-slate-700">
                      <span className="text-emerald-500 font-bold">✓</span>
                      <span className="truncate">{m}</span>
                    </div>
                  ))}
                  {r.unmatched_reasons.slice(0, 1).map((u, idx) => (
                    <div key={'u' + idx} className="flex items-center gap-1.5 text-slate-400">
                      <span className="text-rose-500 font-bold">✕</span>
                      <span className="truncate">{u}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <Link
                  to={`/schemes/${r.scheme_id}`}
                  className="btn-secondary text-xs py-1.5 px-3.5"
                >
                  View Details & Documents →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
