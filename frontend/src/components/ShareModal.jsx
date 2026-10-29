import React, { useState } from 'react'
import toast from 'react-hot-toast'

export default function ShareModal({ scheme, isOpen, onClose }) {
  const [copied, setCopied] = useState(false)
  if (!isOpen || !scheme) return null

  const shareUrl = window.location.href
  const shareText = `Check out this government scheme: ${scheme.title} (${scheme.category || 'Welfare'})\nBenefits: ${scheme.benefits || scheme.description?.slice(0, 100) || 'Government welfare support'}\nLink: ${shareUrl}`

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareUrl).then(() => {
      setCopied(true)
      toast.success('Link copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    }).catch(() => {
      toast.error('Could not copy link')
    })
  }

  const handleWhatsApp = () => {
    const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`
    window.open(url, '_blank')
  }

  const handleTelegram = () => {
    const url = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(scheme.title)}`
    window.open(url, '_blank')
  }

  const handleTwitter = () => {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`
    window.open(url, '_blank')
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl animate-slide-up border border-navy-100">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold text-navy-900 flex items-center gap-2">
            <span>📱</span> Share Scheme
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl font-bold">
            ✕
          </button>
        </div>

        <p className="text-sm text-slate-600 mb-4 line-clamp-2">
          {scheme.title}
        </p>

        <div className="grid grid-cols-2 gap-3 mb-5">
          <button
            onClick={handleWhatsApp}
            className="flex items-center justify-center gap-2 p-3 rounded-xl bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-medium text-sm transition-all border border-emerald-200"
          >
            <span className="text-xl">💬</span> WhatsApp
          </button>
          <button
            onClick={handleTelegram}
            className="flex items-center justify-center gap-2 p-3 rounded-xl bg-sky-50 text-sky-700 hover:bg-sky-100 font-medium text-sm transition-all border border-sky-200"
          >
            <span className="text-xl">✈️</span> Telegram
          </button>
          <button
            onClick={handleTwitter}
            className="flex items-center justify-center gap-2 p-3 rounded-xl bg-blue-50 text-blue-700 hover:bg-blue-100 font-medium text-sm transition-all border border-blue-200"
          >
            <span className="text-xl">🐦</span> Twitter / X
          </button>
          <button
            onClick={handleCopyLink}
            className="flex items-center justify-center gap-2 p-3 rounded-xl bg-navy-50 text-navy-700 hover:bg-navy-100 font-medium text-sm transition-all border border-navy-200"
          >
            <span className="text-xl">🔗</span> {copied ? 'Copied!' : 'Copy Link'}
          </button>
        </div>

        <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-xs text-slate-500 break-all select-all">
          {shareUrl}
        </div>
      </div>
    </div>
  )
}
