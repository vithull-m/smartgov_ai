import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'

const EMPTY_FORM = {
  title: '', department: '', description: '', benefits: '', category: '',
  target_group: '', state: 'All India', official_link: '', is_active: true,
  rules: [], documents: [], steps: [],
}

export default function AdminPanel() {
  const { t } = useTranslation()
  const [tab, setTab] = useState('analytics') // 'analytics' or 'schemes'
  const [schemes, setSchemes] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  const loadSchemes = () => {
    api.get('/admin/schemes').then(({ data }) => setSchemes(data)).catch(() => {})
  }

  const loadAnalytics = () => {
    api.get('/admin/analytics').then(({ data }) => setAnalytics(data)).catch(() => {})
  }

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.get('/admin/schemes').then(({ data }) => setSchemes(data)),
      api.get('/admin/analytics').then(({ data }) => setAnalytics(data)),
    ])
      .catch(() => toast.error('Could not load admin data'))
      .finally(() => setLoading(false))
  }, [])

  const update = (field, value) => setForm((f) => ({ ...f, [field]: value }))

  const addRule = () => update('rules', [...form.rules, { field_name: 'age', operator: 'gte', value: '', description: '' }])
  const updateRule = (i, key, value) => {
    const rules = [...form.rules]
    rules[i] = { ...rules[i], [key]: value }
    update('rules', rules)
  }
  const removeRule = (i) => update('rules', form.rules.filter((_, idx) => idx !== i))

  const addDocument = () => update('documents', [...form.documents, { document_name: '', is_mandatory: true }])
  const updateDocument = (i, key, value) => {
    const docs = [...form.documents]
    docs[i] = { ...docs[i], [key]: value }
    update('documents', docs)
  }
  const removeDocument = (i) => update('documents', form.documents.filter((_, idx) => idx !== i))

  const addStep = () => update('steps', [...form.steps, { step_number: form.steps.length + 1, instruction: '' }])
  const updateStep = (i, key, value) => {
    const steps = [...form.steps]
    steps[i] = { ...steps[i], [key]: value }
    update('steps', steps)
  }
  const removeStep = (i) => update('steps', form.steps.filter((_, idx) => idx !== i))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/admin/schemes', form)
      toast.success('Scheme created successfully!')
      setForm(EMPTY_FORM)
      setShowForm(false)
      loadSchemes()
      loadAnalytics()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not save scheme.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this scheme?')) return
    try {
      await api.delete(`/admin/schemes/${id}`)
      toast.success('Scheme deleted')
      loadSchemes()
      loadAnalytics()
    } catch {
      toast.error('Could not delete scheme')
    }
  }

  if (loading) return <LoadingSpinner text="Loading admin analytics..." />

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="page-title text-2xl md:text-3xl flex items-center gap-2">
            <span>⚙️</span> {t('admin_panel')} & Analytics
          </h1>
          <p className="page-subtitle">
            System overview, citizen metrics, scheme performance, and catalog administration
          </p>
        </div>

        {tab === 'schemes' && (
          <button className={showForm ? 'btn-danger text-sm' : 'btn-primary text-sm'} onClick={() => setShowForm((s) => !s)}>
            {showForm ? '✕ Cancel' : '+ ' + t('add_scheme')}
          </button>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-2 border-b border-navy-100 pb-2">
        <button
          onClick={() => setTab('analytics')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            tab === 'analytics'
              ? 'bg-navy-900 text-white shadow-sm'
              : 'text-slate-600 hover:bg-navy-50'
          }`}
        >
          📊 Analytics & Insights
        </button>
        <button
          onClick={() => setTab('schemes')}
          className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            tab === 'schemes'
              ? 'bg-navy-900 text-white shadow-sm'
              : 'text-slate-600 hover:bg-navy-50'
          }`}
        >
          📋 Scheme Management ({schemes.length})
        </button>
      </div>

      {/* Tab 1: Analytics Dashboard */}
      {tab === 'analytics' && analytics && (
        <div className="space-y-6 animate-slide-up">
          {/* Top KPI Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
            <div className="card text-center py-4 bg-white/90">
              <p className="text-3xl font-bold text-navy-900">{analytics.total_users}</p>
              <p className="text-xs text-slate-500 mt-1">Registered Citizens</p>
            </div>
            <div className="card text-center py-4 bg-white/90">
              <p className="text-3xl font-bold text-navy-800">{analytics.total_schemes}</p>
              <p className="text-xs text-slate-500 mt-1">Active Schemes</p>
            </div>
            <div className="card text-center py-4 bg-blue-50/50 border-blue-200">
              <p className="text-3xl font-bold text-blue-700">{analytics.total_applications}</p>
              <p className="text-xs text-slate-500 mt-1">Tracked Applications</p>
            </div>
            <div className="card text-center py-4 bg-emerald-50/50 border-emerald-200">
              <p className="text-3xl font-bold text-emerald-700">{analytics.total_saved}</p>
              <p className="text-xs text-slate-500 mt-1">Bookmarked</p>
            </div>
            <div className="card text-center py-4 bg-amber-50/50 border-amber-200">
              <p className="text-3xl font-bold text-amber-700">{analytics.total_reviews}</p>
              <p className="text-xs text-slate-500 mt-1">Citizen Reviews</p>
            </div>
            <div className="card text-center py-4 bg-indigo-50/50 border-indigo-200">
              <p className="text-3xl font-bold text-indigo-700">★ {analytics.average_rating_overall}</p>
              <p className="text-xs text-slate-500 mt-1">Avg Satisfaction</p>
            </div>
          </div>

          {/* Visual Breakdown Grids */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Schemes by Category */}
            <div className="card">
              <h3 className="section-title text-base mb-3 flex items-center gap-2">
                <span>📁</span> Schemes by Sector / Category
              </h3>
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {analytics.schemes_by_category.map((item, idx) => {
                  const percent = analytics.total_schemes > 0 ? Math.round((item.count / analytics.total_schemes) * 100) : 0
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium text-slate-700">
                        <span>{item.category}</span>
                        <span className="text-slate-500">{item.count} schemes ({percent}%)</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-navy-700 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Applications by Status */}
            <div className="card flex flex-col justify-between">
              <div>
                <h3 className="section-title text-base mb-3 flex items-center gap-2">
                  <span>📈</span> Application Status Pipeline
                </h3>
                {analytics.applications_by_status.length === 0 ? (
                  <p className="text-xs text-slate-400 py-8 text-center">No applications tracked yet in system.</p>
                ) : (
                  <div className="space-y-3">
                    {analytics.applications_by_status.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-navy-50/50 border border-navy-100">
                        <span className="capitalize font-semibold text-xs text-navy-900">
                          {item.status.replace('_', ' ')}
                        </span>
                        <span className="badge bg-navy-800 text-white font-bold">
                          {item.count}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200 mt-4 text-xs text-emerald-800">
                💡 <strong>Admin Tip:</strong> Promote underrepresented sectors (e.g. Disability Support) by pinning relevant schemes.
              </div>
            </div>
          </div>

          {/* Recent Applications Table */}
          {analytics.recent_applications.length > 0 && (
            <div className="card">
              <h3 className="section-title text-base mb-3">🕒 Recent Citizen Applications</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-left border-b border-navy-100 text-slate-500">
                      <th className="py-2">Scheme</th>
                      <th>Citizen</th>
                      <th>Beneficiary</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-navy-50">
                    {analytics.recent_applications.map((app) => (
                      <tr key={app.id} className="hover:bg-navy-50/30">
                        <td className="py-2.5 font-medium text-navy-900">{app.scheme_title}</td>
                        <td className="text-slate-600">{app.user_name}</td>
                        <td className="text-slate-500">{app.family_member_name || 'Self'}</td>
                        <td>
                          <span className="badge bg-navy-100 text-navy-800 uppercase text-[10px]">
                            {app.status}
                          </span>
                        </td>
                        <td className="text-slate-400">{new Date(app.applied_date).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Scheme Management CRUD */}
      {tab === 'schemes' && (
        <div className="space-y-6 animate-slide-up">
          {showForm && (
            <form onSubmit={handleSubmit} className="card flex flex-col gap-5 animate-slide-down border-t-4 border-t-navy-700">
              <h2 className="section-title">New Government Scheme</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input className="input-field" placeholder="Title *" required value={form.title} onChange={(e) => update('title', e.target.value)} />
                <input className="input-field" placeholder="Department" value={form.department} onChange={(e) => update('department', e.target.value)} />
                <input className="input-field" placeholder="Category" value={form.category} onChange={(e) => update('category', e.target.value)} />
                <input className="input-field" placeholder="Target Group" value={form.target_group} onChange={(e) => update('target_group', e.target.value)} />
                <input className="input-field" placeholder="State (default: All India)" value={form.state} onChange={(e) => update('state', e.target.value)} />
                <input className="input-field" placeholder="Official Link" value={form.official_link} onChange={(e) => update('official_link', e.target.value)} />
              </div>
              <textarea className="input-field" placeholder="Description" rows={2} value={form.description} onChange={(e) => update('description', e.target.value)} />
              <textarea className="input-field" placeholder="Benefits" rows={2} value={form.benefits} onChange={(e) => update('benefits', e.target.value)} />

              {/* Rules */}
              <div className="border border-navy-100 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <p className="font-medium text-sm text-navy-800">📌 Eligibility Rules</p>
                  <button type="button" onClick={addRule} className="btn-secondary text-xs">+ Add Rule</button>
                </div>
                {form.rules.map((r, i) => (
                  <div key={i} className="flex flex-wrap gap-2 mb-2 items-center">
                    <select className="input-field w-32" value={r.field_name} onChange={(e) => updateRule(i, 'field_name', e.target.value)}>
                      {['age', 'income', 'gender', 'occupation', 'education', 'state', 'category', 'is_student', 'is_farmer', 'has_disability'].map((f) => (
                        <option key={f} value={f}>{f}</option>
                      ))}
                    </select>
                    <select className="input-field w-24" value={r.operator} onChange={(e) => updateRule(i, 'operator', e.target.value)}>
                      {['eq', 'neq', 'lte', 'gte', 'lt', 'gt', 'in'].map((op) => <option key={op} value={op}>{op}</option>)}
                    </select>
                    <input className="input-field w-36" placeholder="Value" value={r.value} onChange={(e) => updateRule(i, 'value', e.target.value)} />
                    <input className="input-field flex-1 min-w-[150px]" placeholder="Reason" value={r.description} onChange={(e) => updateRule(i, 'description', e.target.value)} />
                    <button type="button" onClick={() => removeRule(i)} className="btn-danger text-xs px-2 py-1">✕</button>
                  </div>
                ))}
              </div>

              {/* Documents */}
              <div className="border border-navy-100 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <p className="font-medium text-sm text-navy-800">📄 {t('documents_required')}</p>
                  <button type="button" onClick={addDocument} className="btn-secondary text-xs">+ Add Document</button>
                </div>
                {form.documents.map((d, i) => (
                  <div key={i} className="flex gap-2 mb-2 items-center">
                    <input className="input-field flex-1" placeholder="Document name" value={d.document_name} onChange={(e) => updateDocument(i, 'document_name', e.target.value)} />
                    <label className="text-sm flex items-center gap-1.5 whitespace-nowrap">
                      <input type="checkbox" checked={d.is_mandatory} onChange={(e) => updateDocument(i, 'is_mandatory', e.target.checked)} /> Mandatory
                    </label>
                    <button type="button" onClick={() => removeDocument(i)} className="btn-danger text-xs px-2 py-1">✕</button>
                  </div>
                ))}
              </div>

              {/* Steps */}
              <div className="border border-navy-100 rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <p className="font-medium text-sm text-navy-800">📝 {t('application_steps')}</p>
                  <button type="button" onClick={addStep} className="btn-secondary text-xs">+ Add Step</button>
                </div>
                {form.steps.map((s, i) => (
                  <div key={i} className="flex gap-2 mb-2 items-center">
                    <input type="number" className="input-field w-16" value={s.step_number} onChange={(e) => updateStep(i, 'step_number', Number(e.target.value))} />
                    <input className="input-field flex-1" placeholder="Instruction" value={s.instruction} onChange={(e) => updateStep(i, 'instruction', e.target.value)} />
                    <button type="button" onClick={() => removeStep(i)} className="btn-danger text-xs px-2 py-1">✕</button>
                  </div>
                ))}
              </div>

              <button type="submit" disabled={saving} className="btn-primary self-start">
                {saving ? 'Saving...' : '✓ Save Scheme'}
              </button>
            </form>
          )}

          {/* Schemes table */}
          <div className="card">
            <h3 className="section-title mb-4">{t('manage_schemes')}</h3>
            {schemes.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">No schemes yet. Create one above.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left border-b-2 border-navy-100">
                      <th className="py-3 text-navy-700">Title</th>
                      <th className="text-navy-700">Category</th>
                      <th className="text-navy-700">State</th>
                      <th className="text-navy-700">Active</th>
                      <th className="text-navy-700 w-20"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {schemes.map((s) => (
                      <tr key={s.id} className="border-b border-navy-50 hover:bg-navy-50/50 transition-colors">
                        <td className="py-3 font-medium text-navy-800">{s.title}</td>
                        <td><span className="badge bg-navy-100 text-navy-600">{s.category}</span></td>
                        <td className="text-xs text-slate-500">{s.state || 'All India'}</td>
                        <td>{s.is_active ? <span className="text-moss-600 font-medium">✓ Yes</span> : <span className="text-slate-400">No</span>}</td>
                        <td>
                          <button onClick={() => handleDelete(s.id)} className="btn-danger text-xs">Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
