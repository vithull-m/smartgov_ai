import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import api from '../../api/axios'
import SchemeCard from '../../components/SchemeCard'
import LoadingSpinner from '../../components/LoadingSpinner'

export default function Saved() {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.get('/saved').then(({ data }) => setItems(data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleUnsave = async (schemeId) => {
    await api.delete(`/saved/${schemeId}`)
    toast.success('Scheme removed')
    load()
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="page-title">⭐ {t('saved_schemes')}</h1>
        <p className="page-subtitle">Your bookmarked schemes for quick access</p>
      </div>
      {items.length === 0 ? (
        <div className="card text-center py-16">
          <span className="text-5xl">⭐</span>
          <p className="text-slate-500 mt-4">No saved schemes yet.</p>
          <Link to="/schemes" className="btn-primary mt-4 inline-block">Browse Schemes</Link>
        </div>
      ) : (
        <>
          <p className="text-sm text-slate-500 mb-4">{items.length} saved scheme{items.length !== 1 ? 's' : ''}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {items.map((item) => (
              <SchemeCard key={item.id} scheme={item.scheme} onSave={handleUnsave} saved={true} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
