import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'

const STATUS_BADGES = {
  applied: { label: 'Applied', color: 'bg-blue-100 text-blue-700 border-blue-200' },
  in_progress: { label: 'In Progress', color: 'bg-amber-100 text-amber-800 border-amber-200' },
  approved: { label: 'Approved', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
  rejected: { label: 'Rejected', color: 'bg-rose-100 text-rose-800 border-rose-200' },
}

export default function Applications() {
  const { t } = useTranslation()
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  const loadApps = () => {
    setLoading(true)
    api.get('/applications')
      .then(({ data }) => setApps(data))
      .catch(() => toast.error('Could not load applications'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadApps()
  }, [])

  const handleStatusChange = async (appId, newStatus) => {
    try {
      await api.put(`/applications/${appId}`, { status: newStatus })
      toast.success('Status updated!')
      loadApps()
    } catch {
      toast.error('Failed to update status')
    }
  }

  const handleDelete = async (appId) => {
    if (!window.confirm('Delete this tracked application?')) return
    try {
      await api.delete(`/applications/${appId}`)
      toast.success('Record removed')
      loadApps()
    } catch {
      toast.error('Could not delete record')
    }
  }

  const filteredApps = filter === 'all' ? apps : apps.filter((a) => a.status === filter)

  if (loading) return <LoadingSpinner text="Loading applications..." />

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="page-title text-2xl md:text-3xl flex items-center gap-2">
            <span>📋</span> Application Status Tracker
          </h1>
          <p className="page-subtitle">
            Keep track of all government scheme submissions for you and your household in one central pipeline.
          </p>
        </div>
        <Link to="/schemes" className="btn-primary text-sm">
          + Track Another Scheme
        </Link>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="card text-center py-4 bg-white/90">
          <p className="text-3xl font-bold text-navy-800">{apps.length}</p>
          <p className="text-xs text-slate-500 mt-1">Total Tracked</p>
        </div>
        <div className="card text-center py-4 bg-blue-50/50 border-blue-100">
          <p className="text-3xl font-bold text-blue-700">{apps.filter((a) => a.status === 'applied').length}</p>
          <p className="text-xs text-slate-500 mt-1">Submitted / Applied</p>
        </div>
        <div className="card text-center py-4 bg-amber-50/50 border-amber-100">
          <p className="text-3xl font-bold text-amber-700">{apps.filter((a) => a.status === 'in_progress').length}</p>
          <p className="text-xs text-slate-500 mt-1">In Verification</p>
        </div>
        <div className="card text-center py-4 bg-emerald-50/50 border-emerald-100">
          <p className="text-3xl font-bold text-emerald-700">{apps.filter((a) => a.status === 'approved').length}</p>
          <p className="text-xs text-slate-500 mt-1">Sanctioned / Approved</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 border-b border-navy-100 pb-2 overflow-x-auto text-sm">
        {['all', 'applied', 'in_progress', 'approved', 'rejected'].map((st) => (
          <button
            key={st}
            onClick={() => setFilter(st)}
            className={`px-3.5 py-1.5 rounded-lg font-medium capitalize transition-all ${
              filter === st
                ? 'bg-navy-800 text-white shadow-sm'
                : 'text-slate-600 hover:bg-navy-50'
            }`}
          >
            {st.replace('_', ' ')} ({st === 'all' ? apps.length : apps.filter((a) => a.status === st).length})
          </button>
        ))}
      </div>

      {/* Application List */}
      {filteredApps.length === 0 ? (
        <div className="card text-center py-16">
          <span className="text-5xl">📭</span>
          <h3 className="text-lg font-bold text-navy-900 mt-4">No Applications Found</h3>
          <p className="text-slate-500 text-sm mt-1 max-w-md mx-auto">
            You haven't tracked any applications with this status. Browse schemes and click "Track Application" to get started.
          </p>
          <Link to="/schemes" className="btn-primary mt-4 inline-block text-sm">
            Browse Schemes Catalog
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredApps.map((item) => {
            const badge = STATUS_BADGES[item.status] || STATUS_BADGES.applied
            return (
              <div
                key={item.id}
                className="card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border-l-4 border-l-navy-700"
              >
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <span className={`badge border text-xs font-semibold ${badge.color}`}>
                      ● {badge.label}
                    </span>
                    <span className="text-xs text-slate-400">
                      Applied: {new Date(item.applied_date).toLocaleDateString()}
                    </span>
                    {item.family_member_name && (
                      <span className="badge bg-slate-100 text-slate-700 text-xs">
                        👤 For: {item.family_member_name}
                      </span>
                    )}
                  </div>

                  <h3 className="font-bold text-navy-900 text-lg leading-tight">
                    {item.scheme?.title || `Scheme #${item.scheme_id}`}
                  </h3>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-2">
                    {item.application_reference && (
                      <p className="font-mono bg-navy-50 px-2 py-0.5 rounded border border-navy-100 text-navy-800">
                        Ref #: {item.application_reference}
                      </p>
                    )}
                    {item.notes && (
                      <p className="italic text-slate-600">
                        "{item.notes}"
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end md:self-center shrink-0">
                  <select
                    className="input-field text-xs py-1.5 w-36"
                    value={item.status}
                    onChange={(e) => handleStatusChange(item.id, e.target.value)}
                  >
                    <option value="applied">Applied</option>
                    <option value="in_progress">In Progress</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>

                  <Link
                    to={`/schemes/${item.scheme_id}`}
                    className="btn-secondary text-xs py-1.5 px-3"
                  >
                    View
                  </Link>

                  <button
                    onClick={() => handleDelete(item.id)}
                    className="btn-danger text-xs py-1.5 px-2.5"
                    title="Delete record"
                  >
                    ✕
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
