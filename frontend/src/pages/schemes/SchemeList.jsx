import React, { useEffect, useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import api from '../../api/axios'
import SchemeCard from '../../components/SchemeCard'
import LoadingSpinner from '../../components/LoadingSpinner'

const CATEGORIES = [
  { id: '', label: '🌟 All Schemes' },
  { id: 'Education', label: '🎓 Education' },
  { id: 'Agriculture', label: '🌾 Agriculture' },
  { id: 'Healthcare', label: '🏥 Healthcare' },
  { id: 'Housing', label: '🏠 Housing' },
  { id: 'Women Welfare', label: '🌸 Women Welfare' },
  { id: 'Employment & Business', label: '💼 Employment & Business' },
  { id: 'Senior Citizens', label: '👴 Senior Citizens' },
  { id: 'Disability Support', label: '♿ Disability Support' },
]

export default function SchemeList() {
  const { t } = useTranslation()
  const [schemes, setSchemes] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [savedIds, setSavedIds] = useState(new Set())

  const fetchSchemes = useCallback(() => {
    setLoading(true)
    api.get('/schemes', { params: { search: search || undefined, category: category || undefined } })
      .then(({ data }) => setSchemes(data))
      .catch(() => toast.error('Could not load schemes'))
      .finally(() => setLoading(false))
  }, [search, category])

  useEffect(() => {
    fetchSchemes()
  }, [category, fetchSchemes])

  useEffect(() => {
    api.get('/saved')
      .then(({ data }) => setSavedIds(new Set(data.map((s) => s.scheme.id))))
      .catch(() => {})
  }, [])

  const handleSave = async (schemeId) => {
    try {
      if (savedIds.has(schemeId)) {
        await api.delete(`/saved/${schemeId}`)
        setSavedIds((prev) => {
          const next = new Set(prev)
          next.delete(schemeId)
          return next
        })
        toast.success('Removed from saved')
      } else {
        await api.post(`/saved/${schemeId}`)
        setSavedIds((prev) => new Set(prev).add(schemeId))
        toast.success('Scheme saved to bookmarks!')
      }
    } catch {
      toast.error('Action failed')
    }
  }

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      {/* Page Header */}
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title">🏛️ Government Welfare Schemes Catalog</h1>
          <p className="page-subtitle">
            Explore verified central & state government welfare initiatives, subsidies, and grants
          </p>
        </div>
        <div className="flex items-center gap-2 bg-navy-100/70 px-3.5 py-1.5 rounded-full text-navy-800 text-xs font-semibold self-start sm:self-auto">
          <span>📋 Total Available:</span>
          <span className="bg-navy-700 text-white px-2 py-0.5 rounded-full">{schemes.length}</span>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-4 scrollbar-none">
        {CATEGORIES.map((c) => (
          <button
            key={c.id}
            onClick={() => setCategory(c.id)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all duration-200 ${
              category === c.id
                ? 'bg-navy-700 text-white shadow-sm ring-2 ring-navy-700/20'
                : 'bg-white border border-navy-200 text-navy-700 hover:bg-navy-50'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Search Bar & Controls */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">🔍</span>
            <input
              className="input-field pl-10"
              placeholder="Search by scheme name, keywords, or department..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchSchemes()}
            />
          </div>
          <button className="btn-primary flex items-center justify-center gap-1.5" onClick={fetchSchemes}>
            <span>Search</span>
          </button>
          {search && (
            <button
              className="btn-secondary text-xs"
              onClick={() => {
                setSearch('')
                setCategory('')
              }}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Scheme Cards Grid */}
      {loading ? (
        <LoadingSpinner text="Fetching government schemes catalog..." />
      ) : schemes.length === 0 ? (
        <div className="card text-center py-16">
          <span className="text-5xl">📭</span>
          <h3 className="font-semibold text-navy-900 mt-4 text-lg">No matching schemes found</h3>
          <p className="text-slate-500 text-sm mt-1">Try changing your search query or selecting a different category.</p>
          <button
            className="btn-primary mt-4"
            onClick={() => {
              setSearch('')
              setCategory('')
            }}
          >
            View All Schemes
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
              Showing {schemes.length} Government Scheme{schemes.length !== 1 ? 's' : ''}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {schemes.map((s) => (
              <SchemeCard key={s.id} scheme={s} onSave={handleSave} saved={savedIds.has(s.id)} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
