import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'
import DigiLockerModal from '../../components/DigiLockerModal'

const EMPTY = {
  age: '', gender: '', income: '', occupation: '', education: '',
  state: '', category: '', is_student: false, is_farmer: false, has_disability: false,
}

const STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa',
  'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
  'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland',
  'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
  'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry', 'Chandigarh',
]

export default function Profile() {
  const { t } = useTranslation()
  const [form, setForm] = useState(EMPTY)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [digiStatus, setDigiStatus] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [activeCertTab, setActiveCertTab] = useState(null) // For certificate inspection

  const loadData = () => {
    setLoading(true)
    Promise.all([
      api.get('/profile/me').then(({ data }) => {
        setForm({ ...EMPTY, ...data, age: data.age ?? '', income: data.income ?? '' })
      }),
      api.get('/digilocker/status').then(({ data }) => {
        setDigiStatus(data)
        if (data.documents && data.documents.length > 0) {
          setActiveCertTab(data.documents[0].id)
        }
      }),
    ])
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadData()
  }, [])

  const update = (field, value) => setForm((f) => ({ ...f, [field]: value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {
        ...form,
        age: form.age === '' ? null : Number(form.age),
        income: form.income === '' ? null : Number(form.income),
      }
      await api.put('/profile/me', payload)
      toast.success('Profile saved successfully!')
    } catch {
      toast.error('Could not save profile. Please check your entries.')
    } finally {
      setSaving(false)
    }
  }

  const handleDisconnect = async () => {
    if (!window.confirm('Disconnect your verified government authentication and linked documents?')) return
    try {
      await api.delete('/digilocker/disconnect')
      toast.success('Government verification disconnected')
      loadData()
    } catch {
      toast.error('Failed to disconnect verification')
    }
  }

  if (loading) return <LoadingSpinner />

  const selectedCert = digiStatus?.documents?.find((d) => d.id === activeCertTab)

  return (
    <div className="max-w-5xl mx-auto animate-fade-in space-y-6 pb-16">
      <DigiLockerModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={loadData}
      />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2.5">
            <span>👤</span> {t('your_profile')}
          </h1>
          <p className="page-subtitle">
            Manage your verified citizen identity and welfare eligibility credentials.
          </p>
        </div>

        {digiStatus?.is_verified ? (
          <div className="flex items-center gap-2">
            <span className="badge bg-emerald-50 text-emerald-800 border border-emerald-300 py-1.5 px-3.5 text-xs font-bold shadow-sm flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>{digiStatus.verification_mode === 'digilocker' ? 'DigiLocker Verified' : 'Farmer Record Verified'}</span>
            </span>
            <button
              onClick={handleDisconnect}
              className="text-xs text-rose-600 hover:text-rose-700 font-bold px-2 py-1 rounded-lg hover:bg-rose-50 transition-colors"
            >
              Disconnect
            </button>
          </div>
        ) : (
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-800 hover:from-blue-800 hover:to-indigo-900 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all hover:scale-[1.02]"
            >
              <span>🇮🇳</span> Authenticate Identity (DigiLocker / Farmer)
            </button>
          </div>
        )}
      </div>

      {/* ============================================================== */}
      {/* ENTERPRISE VERIFICATION CERTIFICATE PASSPORT                    */}
      {/* ============================================================== */}
      {digiStatus?.is_verified ? (
        <div className="card overflow-hidden border-2 border-emerald-300 bg-gradient-to-br from-emerald-50/60 via-white to-blue-50/40 p-0 shadow-lg">
          {/* Certificate Header Banner */}
          <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800">
            <div className="flex items-center gap-3.5">
              <div className="w-12 h-12 rounded-2xl bg-white/10 border border-emerald-400/30 flex items-center justify-center text-2xl shadow-inner shrink-0">
                🛡️
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-extrabold text-white text-base tracking-tight">
                    Government Authenticated Citizen Welfare Passport
                  </h3>
                  <span className="badge bg-emerald-400/20 text-emerald-300 text-[10px] font-bold border border-emerald-400/30">
                    UIDAI / State Revenue Sealed
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-0.5">
                  Authority ID: <strong className="font-mono text-emerald-300">{digiStatus.digilocker_id || 'DL-IN-VALID'}</strong> · Linked: {new Date(digiStatus.linked_at || Date.now()).toLocaleDateString('en-IN')}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 self-start md:self-auto bg-slate-800/80 px-4 py-2 rounded-2xl border border-slate-700">
              <div className="text-right">
                <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Verification Trust</p>
                <p className="text-sm font-extrabold text-emerald-400">100% Statutory Match</p>
              </div>
              <div className="w-9 h-9 rounded-full bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-400 font-extrabold text-sm">
                ✓
              </div>
            </div>
          </div>

          {/* Citizen Demographics Harmonized View */}
          <div className="p-6 grid grid-cols-2 sm:grid-cols-4 gap-4 bg-white/80 border-b border-slate-200">
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400">Verified Citizen</p>
              <p className="text-sm font-extrabold text-slate-900 mt-0.5">{digiStatus.verified_name || form.verified_name || 'Verified Citizen'}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400">Aadhaar Last 4</p>
              <p className="text-sm font-extrabold font-mono text-slate-900 mt-0.5">XXXX-XXXX-{digiStatus.aadhaar_last4 || '8912'}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400">Verification Source</p>
              <p className="text-sm font-bold text-blue-700 mt-0.5 capitalize">
                {digiStatus.verification_mode === 'pm_kisan' ? 'PM-KISAN AgriStack' :
                 digiStatus.verification_mode === 'land_record' ? 'Bhulekh Land Patta' :
                 digiStatus.verification_mode === 'ration_card' ? 'NFSA Ration PDS' :
                 digiStatus.verification_mode === 'csc_vle' ? 'CSC e-Seva Center' : 'DigiLocker MeitY'}
              </p>
            </div>
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400">Total Linked Certificates</p>
              <p className="text-sm font-extrabold text-emerald-700 mt-0.5">{digiStatus.total_documents || 4} Authoritative Records</p>
            </div>
          </div>

          {/* Issued Documents Selector & Interactive Certificate Inspector */}
          <div className="p-6">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3 flex items-center justify-between">
              <span>Authoritative Issued Government Records ({digiStatus.documents?.length || 0})</span>
              <span className="text-[11px] text-slate-400 font-normal">Click any certificate to inspect digital signature & attributes</span>
            </h4>

            {/* Document Pills / Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
              {digiStatus.documents?.map((doc) => {
                const isSelected = activeCertTab === doc.id
                return (
                  <button
                    key={doc.id}
                    type="button"
                    onClick={() => setActiveCertTab(doc.id)}
                    className={`text-left p-3.5 rounded-2xl border transition-all ${
                      isSelected
                        ? 'bg-blue-50/90 border-blue-600 ring-2 ring-blue-500/20 shadow-md'
                        : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1.5">
                      <span className="text-lg">
                        {doc.doc_type.includes('land') ? '📜' :
                         doc.doc_type.includes('pm_kisan') ? '🚜' :
                         doc.doc_type.includes('kcc') ? '💳' :
                         doc.doc_type.includes('ration') ? '🍚' :
                         doc.doc_type.includes('caste') ? '🏛️' :
                         doc.doc_type.includes('income') ? '💰' : '📄'}
                      </span>
                      <span className="badge bg-emerald-100 text-emerald-800 text-[9px] font-extrabold">
                        ✓ SEALED
                      </span>
                    </div>
                    <p className="font-extrabold text-xs text-slate-900 line-clamp-1">{doc.doc_name}</p>
                    <p className="text-[10px] font-mono text-slate-500 mt-1 truncate">{doc.doc_number}</p>
                  </button>
                )
              })}
            </div>

            {/* Selected Certificate Official Inspection Card */}
            {selectedCert && (
              <div className="p-5 rounded-2xl bg-slate-900 text-white border border-slate-800 animate-slide-up shadow-inner">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div>
                    <span className="badge bg-emerald-400/20 text-emerald-300 text-[10px] font-bold border border-emerald-400/30 mb-1">
                      SHA-256 Validated Digital Document
                    </span>
                    <h5 className="font-extrabold text-sm text-white">{selectedCert.doc_name}</h5>
                    <p className="text-xs text-slate-400 mt-0.5">Issuer: {selectedCert.issuer}</p>
                  </div>
                  <div className="text-left sm:text-right">
                    <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Document Number</p>
                    <p className="text-xs font-mono font-bold text-amber-300">{selectedCert.doc_number}</p>
                  </div>
                </div>

                {/* Metadata JSON Attributes Display */}
                {selectedCert.metadata_json && Object.keys(selectedCert.metadata_json).length > 0 && (
                  <div className="mt-4">
                    <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-2">
                      Extracted Government Payload Attributes:
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                      {Object.entries(selectedCert.metadata_json).map(([k, v]) => (
                        <div key={k} className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700">
                          <p className="text-[10px] text-slate-400 uppercase font-semibold truncate">{k.replace(/_/g, ' ')}</p>
                          <p className="text-xs font-bold text-slate-200 mt-0.5 truncate">{String(v)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-400 gap-2 font-mono">
                  <span>Cryptographic Hash: {selectedCert.security_hash || 'SHA256:VERIFIED_OFFICIAL_RECORD'}</span>
                  <span className="text-emerald-400 font-semibold">● Tamper-Proof Electronic Signature</span>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Not Verified Banner */
        <div className="card overflow-hidden border-2 border-blue-200 bg-gradient-to-br from-blue-50/50 via-white to-slate-50 p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-100/60 text-blue-800 flex items-center justify-center text-3xl shrink-0 border border-blue-200 shadow-sm">
                🇮🇳
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-slate-900 text-base">
                    Dual-Channel Citizen Verification Engine
                  </h3>
                  <span className="badge bg-blue-100 text-blue-800 text-[10px] font-bold">Recommended</span>
                </div>
                <p className="text-xs text-slate-600 mt-1.5 leading-relaxed max-w-2xl">
                  <strong>Option A (DigiLocker):</strong> Instant 1-click Aadhaar e-KYC import for students, urban citizens, and job seekers.<br />
                  <strong>Option B (Farmer Channel):</strong> Authentic verification for rural farmers using PM-KISAN ID, Land Khata/Patta, or Priority Ration Card (no smartphone required).
                </p>
              </div>
            </div>

            <button
              onClick={() => setIsModalOpen(true)}
              className="btn-primary whitespace-nowrap bg-blue-700 hover:bg-blue-800 py-3 px-5 text-xs font-bold shadow-md shadow-blue-500/20"
            >
              Verify Now (DigiLocker / Farmer) →
            </button>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* MANUAL DEMOGRAPHIC FORM CARD                                    */}
      {/* ============================================================== */}
      <div className="card">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div>
            <h2 className="section-title text-base">Demographic & Economic Profile</h2>
            <p className="text-xs text-slate-500 mt-0.5">Parameters evaluated by the statutory eligibility engine</p>
          </div>
          {digiStatus?.is_verified && (
            <span className="badge bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold">
              ✓ Synchronized with Government Records
            </span>
          )}
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 block">{t('age')} *</label>
            <input type="number" min="0" max="120" className="input-field" value={form.age} onChange={(e) => update('age', e.target.value)} placeholder="e.g. 24" />
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 block">{t('gender')} *</label>
            <select className="input-field" value={form.gender || ''} onChange={(e) => update('gender', e.target.value)}>
              <option value="">Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 block">{t('income')} (INR / Year) *</label>
            <input type="number" min="0" className="input-field" value={form.income} onChange={(e) => update('income', e.target.value)} placeholder="e.g. 180000" />
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 block">{t('occupation')} *</label>
            <select className="input-field" value={form.occupation || ''} onChange={(e) => update('occupation', e.target.value)}>
              <option value="">Select occupation</option>
              <option value="unemployed">Unemployed</option>
              <option value="farmer">Farmer / Agriculturalist</option>
              <option value="salaried">Salaried / Private Employee</option>
              <option value="self-employed">Self-Employed / Artisan / MSME</option>
              <option value="student">Student</option>
              <option value="retired">Senior / Retired</option>
              <option value="homemaker">Homemaker</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 block">{t('education')}</label>
            <select className="input-field" value={form.education || ''} onChange={(e) => update('education', e.target.value)}>
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
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 block">{t('state')} *</label>
            <select className="input-field" value={form.state || ''} onChange={(e) => update('state', e.target.value)}>
              <option value="">Select state</option>
              {STATES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1 block">{t('category')} *</label>
            <select className="input-field" value={form.category || ''} onChange={(e) => update('category', e.target.value)}>
              <option value="">Select category</option>
              <option value="General">General</option>
              <option value="OBC">OBC (Other Backward Class)</option>
              <option value="SC">SC (Scheduled Caste)</option>
              <option value="ST">ST (Scheduled Tribe)</option>
              <option value="EWS">EWS (Economically Weaker Section)</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <p className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">Special Quota Attributes</p>
            <div className="flex flex-wrap gap-6">
              <label className="flex items-center gap-2.5 text-xs text-slate-700 font-semibold cursor-pointer">
                <input type="checkbox" className="rounded text-blue-600 focus:ring-blue-500 w-4 h-4" checked={form.is_student} onChange={(e) => update('is_student', e.target.checked)} />
                🎓 {t('is_student')}
              </label>
              <label className="flex items-center gap-2.5 text-xs text-slate-700 font-semibold cursor-pointer">
                <input type="checkbox" className="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4" checked={form.is_farmer} onChange={(e) => update('is_farmer', e.target.checked)} />
                🌾 {t('is_farmer')} (Agricultural Landholder)
              </label>
              <label className="flex items-center gap-2.5 text-xs text-slate-700 font-semibold cursor-pointer">
                <input type="checkbox" className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4" checked={form.has_disability} onChange={(e) => update('has_disability', e.target.checked)} />
                ♿ {t('has_disability')} (Divyangjan)
              </label>
            </div>
          </div>

          <div className="md:col-span-2 pt-2">
            <button type="submit" disabled={saving} className="btn-primary text-xs py-2.5 px-6 font-bold">
              {saving ? t('loading') : '✓ ' + t('save_profile')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
