import React, { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../api/axios'

export default function ApplyTrackerModal({ scheme, isOpen, onClose, onSuccess, familyMembers = [] }) {
  const [target, setTarget] = useState('self')
  const [refNum, setRefNum] = useState('')
  const [status, setStatus] = useState('applied')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)

  if (!isOpen || !scheme) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/applications', {
        scheme_id: scheme.id,
        family_member_name: target === 'self' ? 'Self' : target,
        status: status,
        application_reference: refNum || null,
        notes: notes || null,
      })
      toast.success('Application added to your tracker!')
      if (onSuccess) onSuccess()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not track application')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-slide-up border border-navy-100">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-navy-900 flex items-center gap-2">
            <span>📋</span> Track Scheme Application
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl font-bold">
            ✕
          </button>
        </div>

        <p className="text-xs text-slate-500 mb-4 bg-navy-50/60 p-2.5 rounded-lg border border-navy-100 font-medium">
          Scheme: <strong className="text-navy-900">{scheme.title}</strong>
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3.5 text-sm">
          <div>
            <label className="font-medium text-slate-700 block mb-1">Applying for:</label>
            <select
              className="input-field"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
            >
              <option value="self">Myself (Primary Profile)</option>
              {familyMembers.map((m) => (
                <option key={m.id} value={`${m.name} (${m.relation})`}>
                  {m.name} ({m.relation})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="font-medium text-slate-700 block mb-1">Initial Status:</label>
            <select
              className="input-field"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="applied">Applied (Submitted)</option>
              <option value="in_progress">In Progress (Verification)</option>
              <option value="approved">Approved (Sanctioned)</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div>
            <label className="font-medium text-slate-700 block mb-1">Application / Ack Reference No. (optional):</label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. TN/2026/ED/89412"
              value={refNum}
              onChange={(e) => setRefNum(e.target.value)}
            />
          </div>

          <div>
            <label className="font-medium text-slate-700 block mb-1">Personal Notes (optional):</label>
            <textarea
              className="input-field"
              rows={2}
              placeholder="e.g. Submitted at local Taluk office on Monday"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex-1"
            >
              {saving ? 'Saving...' : 'Add to Tracker'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
