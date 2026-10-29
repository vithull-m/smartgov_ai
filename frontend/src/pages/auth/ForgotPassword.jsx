import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../../api/axios'

export default function ForgotPassword() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [otp, setOtp] = useState('')
  const [emailSent, setEmailSent] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setOtp('')
    setEmailSent(false)
    setLoading(true)

    try {
      const { data } = await api.post('/auth/forgot-password', { email })
      setMessage(data.message)
      setEmailSent(data.email_sent)
      if (data.otp) {
        setOtp(data.otp)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to process your request.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-md animate-slide-up">
        <div className="text-center mb-8">
          <span className="text-5xl">🔑</span>
          <h1 className="page-title mt-4">Forgot Password</h1>
          <p className="page-subtitle mt-2">Enter your registered email to receive a six-digit OTP</p>
        </div>
        <div className="card">
          {error && <div className="alert-error mb-4">{error}</div>}
          {message && <div className="alert-success mb-4">{message}</div>}

          {/* If OTP is shown on screen (dev fallback or SMTP issue) */}
          {otp && (
            <div className="alert-warning text-center mb-4">
              <p className="text-xs uppercase tracking-wide font-semibold text-amber-800">
                Your 6-Digit Reset OTP
              </p>
              <p className="text-3xl font-bold tracking-[0.35em] mt-2 text-amber-900 font-mono">{otp}</p>
              <button
                type="button"
                className="btn-primary mt-3 w-full"
                onClick={() => navigate(`/reset-password?otp=${otp}`)}
              >
                Continue to Reset Password →
              </button>
            </div>
          )}

          {/* If email sent successfully */}
          {emailSent && !otp && (
            <div className="mb-4">
              <button
                type="button"
                className="btn-primary w-full"
                onClick={() => navigate('/reset-password')}
              >
                Enter OTP Received in Email →
              </button>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">{t('email')}</label>
              <input
                type="email"
                required
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Generating OTP...' : 'Send Reset Code'}
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
