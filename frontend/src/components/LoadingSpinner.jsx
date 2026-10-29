import React from 'react'
import { useTranslation } from 'react-i18next'

export default function LoadingSpinner({ text }) {
  const { t } = useTranslation()
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 animate-fade-in">
      <div className="relative">
        <div className="h-10 w-10 rounded-full border-3 border-navy-100" />
        <div className="absolute inset-0 h-10 w-10 rounded-full border-3 border-t-navy-600 animate-spin" />
      </div>
      <p className="text-sm text-navy-500 font-medium">{text || t('loading')}</p>
    </div>
  )
}
