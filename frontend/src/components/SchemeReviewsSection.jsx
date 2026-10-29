import React, { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import api from '../api/axios'

export default function SchemeReviewsSection({ schemeId }) {
  const [stats, setStats] = useState({ average_rating: 0, total_reviews: 0, reviews: [] })
  const [loading, setLoading] = useState(true)
  const [userRating, setUserRating] = useState(5)
  const [userComment, setUserComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [showForm, setShowForm] = useState(false)

  const fetchReviews = () => {
    api.get(`/reviews/scheme/${schemeId}`)
      .then(({ data }) => setStats(data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchReviews()
  }, [schemeId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.post(`/reviews/scheme/${schemeId}`, {
        rating: userRating,
        comment: userComment || null,
      })
      toast.success('Review posted successfully!')
      setUserComment('')
      setShowForm(false)
      fetchReviews()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not submit review')
    } finally {
      setSubmitting(false)
    }
  }

  const renderStars = (rating) => {
    return [1, 2, 3, 4, 5].map((star) => (
      <span key={star} className={star <= rating ? 'text-amber-400' : 'text-slate-300'}>
        ★
      </span>
    ))
  }

  return (
    <div className="card">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="section-title flex items-center gap-2">
            <span>⭐</span> Ratings & Community Reviews
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Real citizen feedback and application experiences
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-lg">
            <span className="text-amber-500 text-lg">★</span>
            <span className="font-bold text-slate-800 text-sm">
              {stats.average_rating > 0 ? stats.average_rating : 'New'}
            </span>
            <span className="text-xs text-slate-500">
              ({stats.total_reviews} {stats.total_reviews === 1 ? 'review' : 'reviews'})
            </span>
          </div>

          <button
            onClick={() => setShowForm(!showForm)}
            className="btn-secondary text-xs py-1.5 px-3"
          >
            {showForm ? 'Cancel' : '✍️ Write Review'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-5 p-4 rounded-xl bg-navy-50/50 border border-navy-100 animate-slide-down">
          <p className="text-xs font-bold text-navy-800 uppercase tracking-wide mb-2">Your Rating</p>
          <div className="flex items-center gap-2 mb-3">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                type="button"
                key={star}
                onClick={() => setUserRating(star)}
                className={`text-2xl transition-transform hover:scale-125 ${
                  star <= userRating ? 'text-amber-400' : 'text-slate-300'
                }`}
              >
                ★
              </button>
            ))}
            <span className="text-xs text-slate-500 font-semibold ml-2">
              {userRating} of 5 stars
            </span>
          </div>

          <textarea
            className="input-field text-sm mb-3"
            rows={2}
            placeholder="Share your experience (e.g. How fast was processing? Were documents easy to obtain?)"
            value={userComment}
            onChange={(e) => setUserComment(e.target.value)}
          />

          <button
            type="submit"
            disabled={submitting}
            className="btn-primary text-xs py-2 px-4"
          >
            {submitting ? 'Submitting...' : 'Post Citizen Review'}
          </button>
        </form>
      )}

      {loading ? (
        <p className="text-xs text-slate-400 py-4 text-center">Loading reviews...</p>
      ) : stats.reviews.length === 0 ? (
        <div className="text-center py-6 bg-slate-50/60 rounded-lg border border-dashed border-slate-200">
          <p className="text-sm text-slate-500">No community reviews yet for this scheme.</p>
          <p className="text-xs text-slate-400 mt-1">Be the first to share your experience!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {stats.reviews.map((rev) => (
            <div key={rev.id} className="p-3.5 rounded-lg bg-navy-50/30 border border-navy-100">
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-xs text-navy-900">{rev.user_name}</span>
                  <div className="text-xs flex">{renderStars(rev.rating)}</div>
                </div>
                <span className="text-[11px] text-slate-400">
                  {new Date(rev.created_at).toLocaleDateString()}
                </span>
              </div>
              {rev.comment && (
                <p className="text-xs text-slate-700 leading-relaxed font-normal">{rev.comment}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
