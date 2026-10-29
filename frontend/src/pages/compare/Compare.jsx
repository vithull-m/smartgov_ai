import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'

export default function Compare() {
  const { t } = useTranslation()
  const [allSchemes, setAllSchemes] = useState([])
  const [selected, setSelected] = useState([])
  const [compared, setCompared] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/schemes').then(({ data }) => setAllSchemes(data))
  }, [])

  const toggleSelect = (id) => {
    setSelected((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id)
      if (prev.length >= 4) {
        toast.error('Maximum 4 schemes allowed')
        return prev
      }
      return [...prev, id]
    })
  }

  const runCompare = async () => {
    if (selected.length < 2) {
      toast.error('Select at least 2 schemes to compare')
      return
    }
    setLoading(true)
    try {
      const { data } = await api.get('/compare', { params: { ids: selected.join(',') } })
      setCompared(data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not compare schemes.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="page-title">⚖️ {t('compare_schemes')}</h1>
        <p className="page-subtitle">Select 2-4 schemes to compare side by side</p>
      </div>

      <div className="card mb-6">
        <p className="text-sm font-medium text-slate-700 mb-3">
          Selected: <span className="font-bold text-navy-700">{selected.length}/4</span>
        </p>
        <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
          {allSchemes.map((s) => (
            <label
              key={s.id}
              className={`flex items-center gap-2 text-sm px-3 py-2 rounded-lg cursor-pointer transition-all ${
                selected.includes(s.id)
                  ? 'bg-navy-700 text-white shadow-sm'
                  : 'bg-navy-50 text-slate-700 hover:bg-navy-100'
              }`}
            >
              <input
                type="checkbox"
                checked={selected.includes(s.id)}
                onChange={() => toggleSelect(s.id)}
                className="sr-only"
              />
              {selected.includes(s.id) ? '✓ ' : ''}{s.title}
            </label>
          ))}
        </div>
        <button
          className="btn-primary mt-4"
          onClick={runCompare}
          disabled={selected.length < 2}
        >
          {t('compare_schemes')}
        </button>
      </div>

      {loading && <LoadingSpinner />}

      {compared.length > 0 && (
        <div className="card overflow-x-auto animate-slide-up">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left p-3 bg-navy-50 rounded-tl-lg font-semibold text-navy-700">Attribute</th>
                {compared.map((s) => (
                  <th key={s.id} className="text-left p-3 bg-navy-50 font-semibold text-navy-700">{s.title}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {['department', 'category', 'target_group', 'state', 'benefits'].map((field) => (
                <tr key={field} className="border-t border-navy-100">
                  <td className="p-3 font-medium text-navy-800 capitalize bg-navy-50/30">{field.replace('_', ' ')}</td>
                  {compared.map((s) => (
                    <td key={s.id} className="p-3 text-slate-700">{s[field] || '—'}</td>
                  ))}
                </tr>
              ))}
              <tr className="border-t border-navy-100">
                <td className="p-3 font-medium text-navy-800 bg-navy-50/30">{t('documents_required')}</td>
                {compared.map((s) => (
                  <td key={s.id} className="p-3 text-slate-700">
                    {s.documents.length > 0
                      ? s.documents.map((d) => d.document_name).join(', ')
                      : '—'}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
