import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

export default function Register() {
  const { t } = useTranslation()
  const { register } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    setSubmitting(true)
    try {
      await register(fullName, email, password)
      toast.success('Account created! Complete your profile.')
      navigate('/profile')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-md animate-slide-up">
        <div className="text-center mb-8">
          <span className="text-5xl">🏛️</span>
          <h1 className="page-title mt-4">{t('create_account')}</h1>
          <p className="page-subtitle mt-2">{t('tagline')}</p>
        </div>
        <div className="card">
          {error && <div className="alert-error mb-4">{error}</div>}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">{t('full_name')}</label>
              <input required className="input-field" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Your full name" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">{t('email')}</label>
              <input type="email" required className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">{t('password')}</label>
              <input type="password" required minLength={6} className="input-field" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min 6 characters" />
            </div>
            <button type="submit" disabled={submitting} className="btn-primary w-full">
              {submitting ? t('loading') : t('register')}
            </button>
          </form>
          <div className="mt-5 pt-4 border-t border-navy-100">
            <p className="text-sm text-slate-500 text-center">
              {t('have_account')}{' '}
              <Link to="/login" className="text-navy-700 font-semibold hover:underline">{t('login')}</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
