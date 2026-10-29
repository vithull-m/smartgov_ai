import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import api from '../../api/axios'

export default function ResetPassword() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [form, setForm] = useState({ otp: '', new_password: '', confirm_password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (form.new_password !== form.confirm_password) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)
    try {
      const { data } = await api.post('/auth/reset-password', {
        otp: form.otp,
        new_password: form.new_password,
      })
      toast.success(data.message)
      setTimeout(() => navigate('/login'), 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to reset your password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-md animate-slide-up">
        <div className="text-center mb-8">
          <span className="text-5xl">🔒</span>
          <h1 className="page-title mt-4">Reset Password</h1>
          <p className="page-subtitle mt-2">Create a new password for your account</p>
        </div>
        <div className="card">
          {error && <div className="alert-error mb-4">{error}</div>}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">6-digit OTP</label>
              <input type="password" name="otp" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} required className="input-field tracking-[0.35em] text-center text-lg font-semibold" value={form.otp} onChange={handleChange} placeholder="6-digit code" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">New Password</label>
              <input type="password" name="new_password" required minLength={6} className="input-field" value={form.new_password} onChange={handleChange} placeholder="Min 6 characters" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">Confirm Password</label>
              <input type="password" name="confirm_password" required minLength={6} className="input-field" value={form.confirm_password} onChange={handleChange} placeholder="Repeat password" />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>

          <div className="mt-5 pt-4 border-t border-navy-100">
            <Link to="/login" className="text-sm text-navy-600 hover:underline">← Back to login</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
