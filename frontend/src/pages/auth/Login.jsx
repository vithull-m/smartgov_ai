import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'

export default function Login() {
  const { t } = useTranslation()
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(email, password)
      toast.success('Welcome back!')
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-md animate-slide-up">
        <div className="text-center mb-8">
          <span className="text-5xl">🏛️</span>
          <h1 className="page-title mt-4">{t('welcome_back')}</h1>
          <p className="page-subtitle mt-2">{t('tagline')}</p>
        </div>
        <div className="card">
          {error && <div className="alert-error mb-4">{error}</div>}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">{t('email')}</label>
              <input type="email" required className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1 block">{t('password')}</label>
              <input type="password" required className="input-field" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            <button type="submit" disabled={submitting} className="btn-primary w-full">
              {submitting ? t('loading') : t('login')}
            </button>
          </form>
          <div className="mt-5 pt-4 border-t border-navy-100 flex flex-col gap-2">
            <p className="text-sm text-slate-500 text-center">
              {t('no_account')}{' '}
              <Link to="/register" className="text-navy-700 font-semibold hover:underline">{t('register')}</Link>
            </p>
            <p className="text-sm text-center">
              <Link to="/forgot-password" className="text-navy-500 hover:text-navy-700 hover:underline">
                {t('forgot_password') || 'Forgot password?'}
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
