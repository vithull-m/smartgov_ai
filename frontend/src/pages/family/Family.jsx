import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'
import SchemeCard from '../../components/SchemeCard'

const EMPTY_MEMBER = {
  name: '',
  relation: 'Father',
  age: '',
  gender: 'male',
  income: 0,
  occupation: '',
  education: '',
  state: 'All India',
  category: 'General',
  is_student: false,
  is_farmer: false,
  has_disability: false,
}

const RELATIONS = ['Father', 'Mother', 'Spouse', 'Son', 'Daughter', 'Brother', 'Sister', 'Grandparent', 'Other']

export default function Family() {
  const { t } = useTranslation()
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_MEMBER)
  const [saving, setSaving] = useState(false)
  const [selectedMember, setSelectedMember] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loadingRecs, setLoadingRecs] = useState(false)

  const loadMembers = () => {
    setLoading(true)
    api.get('/family')
      .then(({ data }) => setMembers(data))
      .catch(() => toast.error('Could not load family members'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadMembers()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {
        ...form,
        age: form.age ? Number(form.age) : null,
        income: form.income ? Number(form.income) : 0,
      }
      await api.post('/family', payload)
      toast.success(`${form.name} added to family!`)
      setForm(EMPTY_MEMBER)
      setShowForm(false)
      loadMembers()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not add family member')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Remove ${name} from your family profile?`)) return
    try {
      await api.delete(`/family/${id}`)
      toast.success(`${name} removed`)
      if (selectedMember?.id === id) {
        setSelectedMember(null)
        setRecommendations([])
      }
      loadMembers()
    } catch {
      toast.error('Could not remove family member')
    }
  }

  const handleSelectMember = (member) => {
    setSelectedMember(member)
    setLoadingRecs(true)
    api.get(`/family/${member.id}/recommendations`)
      .then(({ data }) => setRecommendations(data))
      .catch(() => toast.error(`Could not fetch recommendations for ${member.name}`))
      .finally(() => setLoadingRecs(false))
  }

  if (loading) return <LoadingSpinner text="Loading family profiles..." />

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="page-title text-2xl md:text-3xl flex items-center gap-2">
            <span>👨‍👩‍👧‍👦</span> Family Welfare Mode
          </h1>
          <p className="page-subtitle">
            Add family members (parents, spouse, children) and discover schemes tailored for the entire household.
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary text-sm flex items-center gap-1.5"
        >
          <span>{showForm ? '✕' : '+'}</span>
          <span>{showForm ? 'Cancel' : 'Add Family Member'}</span>
        </button>
      </div>

      {/* Add Member Form */}
      {showForm && (
        <div className="card border-t-4 border-t-navy-700 animate-slide-down">
          <h2 className="section-title mb-4">Add Household Member</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <label className="font-medium text-slate-700 block mb-1">Full Name *</label>
              <input
                required
                className="input-field"
                placeholder="e.g. Ramesh Kumar"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Relationship *</label>
              <select
                className="input-field"
                value={form.relation}
                onChange={(e) => setForm({ ...form, relation: e.target.value })}
              >
                {RELATIONS.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Age</label>
              <input
                type="number"
                min="0"
                max="120"
                className="input-field"
                placeholder="e.g. 58"
                value={form.age}
                onChange={(e) => setForm({ ...form, age: e.target.value })}
              />
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Gender</label>
              <select
                className="input-field"
                value={form.gender}
                onChange={(e) => setForm({ ...form, gender: e.target.value })}
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Occupation</label>
              <select
                className="input-field"
                value={form.occupation}
                onChange={(e) => setForm({ ...form, occupation: e.target.value })}
              >
                <option value="">Select occupation</option>
                <option value="unemployed">Unemployed</option>
                <option value="salaried">Salaried</option>
                <option value="self-employed">Self-Employed / Business</option>
                <option value="student">Student</option>
                <option value="retired">Senior / Retired</option>
                <option value="homemaker">Homemaker</option>
              </select>
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Annual Income (INR)</label>
              <input
                type="number"
                className="input-field"
                placeholder="e.g. 0"
                value={form.income}
                onChange={(e) => setForm({ ...form, income: e.target.value })}
              />
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Education Level</label>
              <select
                className="input-field"
                value={form.education}
                onChange={(e) => setForm({ ...form, education: e.target.value })}
              >
                <option value="">Select education</option>
                <option value="below 10th">Below 10th</option>
                <option value="10th pass">10th Pass</option>
                <option value="12th pass">12th Pass</option>
                <option value="graduate">Graduate</option>
                <option value="post-graduate">Post-Graduate</option>
                <option value="diploma">Diploma / ITI</option>
              </select>
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Social Category</label>
              <select
                className="input-field"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
              >
                <option value="General">General</option>
                <option value="OBC">OBC</option>
                <option value="SC">SC</option>
                <option value="ST">ST</option>
                <option value="EWS">EWS</option>
              </select>
            </div>

            <div className="flex flex-col justify-end gap-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.is_farmer}
                  onChange={(e) => setForm({ ...form, is_farmer: e.target.checked })}
                  className="rounded text-navy-700 focus:ring-navy-500"
                />
                <span>🌾 Is Farmer / Agriculturalist</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.has_disability}
                  onChange={(e) => setForm({ ...form, has_disability: e.target.checked })}
                  className="rounded text-navy-700 focus:ring-navy-500"
                />
                <span>♿ Person with Disability</span>
              </label>
            </div>

            <div className="md:col-span-3 flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="btn-secondary text-sm"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="btn-primary text-sm px-6"
              >
                {saving ? 'Adding...' : 'Save Member'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Member Cards Grid */}
      {members.length === 0 ? (
        <div className="card text-center py-16">
          <span className="text-5xl">👨‍👩‍👧‍👦</span>
          <h3 className="text-lg font-bold text-navy-900 mt-4">No Family Members Added Yet</h3>
          <p className="text-slate-500 text-sm mt-1 max-w-md mx-auto">
            Add parents, children, or spouse to check which government schemes they can benefit from individually.
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="btn-primary mt-4 inline-block text-sm"
          >
            + Add First Family Member
          </button>
        </div>
      ) : (
        <div>
          <h2 className="section-title mb-3">Household Members ({members.length})</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {members.map((m) => {
              const isSelected = selectedMember?.id === m.id
              return (
                <div
                  key={m.id}
                  className={`card cursor-pointer transition-all border-2 ${
                    isSelected
                      ? 'border-navy-700 bg-navy-50/40 shadow-md ring-2 ring-navy-300'
                      : 'border-transparent hover:border-navy-200'
                  }`}
                  onClick={() => handleSelectMember(m)}
                >
                  <div className="flex justify-between items-start gap-2 mb-2">
                    <div>
                      <h3 className="font-bold text-navy-900 text-base">{m.name}</h3>
                      <span className="badge bg-navy-100 text-navy-800 text-xs mt-0.5">
                        {m.relation}
                      </span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDelete(m.id, m.name)
                      }}
                      className="text-xs text-red-500 hover:text-red-700 p-1"
                      title="Remove member"
                    >
                      ✕
                    </button>
                  </div>

                  <div className="text-xs text-slate-600 space-y-1 mt-3">
                    <p>🎂 Age: <strong>{m.age || 'N/A'}</strong> · Gender: <strong className="capitalize">{m.gender || 'N/A'}</strong></p>
                    <p>💼 {m.occupation || 'Unspecified'} · 🎓 {m.education || 'N/A'}</p>
                    {m.is_farmer && <p className="text-moss-600 font-semibold">🌾 Farmer</p>}
                    {m.has_disability && <p className="text-clay-600 font-semibold">♿ Disability Support</p>}
                  </div>

                  <div className="mt-4 pt-3 border-t border-navy-100 flex items-center justify-between text-xs">
                    <span className="text-navy-700 font-medium">
                      {isSelected ? '✓ Viewing Recommendations' : 'Tap to View Schemes →'}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Selected Member Scheme Recommendations */}
      {selectedMember && (
        <div className="card mt-2 border-t-4 border-t-moss-600 animate-slide-up">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <h2 className="section-title text-xl flex items-center gap-2">
                <span>🎯</span> Eligible Schemes for {selectedMember.name} ({selectedMember.relation})
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Evaluated against {selectedMember.name}'s specific age, gender, education, and occupation
              </p>
            </div>
            <span className="badge bg-moss-100 text-moss-700 font-bold px-3 py-1">
              {recommendations.filter((r) => r.is_eligible).length} Eligible Schemes Found
            </span>
          </div>

          {loadingRecs ? (
            <LoadingSpinner text={`Analyzing schemes for ${selectedMember.name}...`} />
          ) : recommendations.length === 0 ? (
            <p className="text-sm text-slate-500 py-6 text-center">
              No matching schemes found for this profile.
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.slice(0, 10).map((r) => (
                <div key={r.scheme_id} className="p-4 rounded-xl border border-navy-100 bg-white/90 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start gap-2 mb-2">
                      <h4 className="font-bold text-navy-900 text-sm leading-snug">{r.title}</h4>
                      <span className={`badge shrink-0 text-xs ${
                        r.is_eligible ? 'bg-moss-100 text-moss-700' : 'bg-clay-100 text-clay-700'
                      }`}>
                        {r.match_score}%
                      </span>
                    </div>
                    <ul className="text-xs text-slate-600 space-y-1 mb-3">
                      {r.matched_reasons.slice(0, 2).map((reason, idx) => (
                        <li key={idx} className="flex items-center gap-1.5 text-moss-700">
                          <span>✓</span> <span>{reason}</span>
                        </li>
                      ))}
                      {r.unmatched_reasons.slice(0, 1).map((reason, idx) => (
                        <li key={'u' + idx} className="flex items-center gap-1.5 text-clay-600">
                          <span>✕</span> <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <Link
                    to={`/schemes/${r.scheme_id}`}
                    className="btn-secondary text-xs text-center py-2"
                  >
                    View Scheme Details →
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
