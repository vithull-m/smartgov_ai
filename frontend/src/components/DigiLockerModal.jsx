import React, { useState } from 'react'
import toast from 'react-hot-toast'
import api from '../api/axios'

const INDIAN_STATES = [
  'Tamil Nadu', 'Uttar Pradesh', 'Maharashtra', 'Karnataka', 'Madhya Pradesh',
  'Bihar', 'Gujarat', 'Rajasthan', 'Punjab', 'Haryana', 'Andhra Pradesh', 'Odisha'
]

export default function DigiLockerModal({ isOpen, onClose, onSuccess }) {
  const [activeTab, setActiveTab] = useState('digilocker') // 'digilocker' or 'farmer'
  const [farmerSubTab, setFarmerSubTab] = useState('pm_kisan') // 'pm_kisan', 'land_record', 'ration_card', 'csc_vle'

  // DigiLocker Form State
  const [dlStep, setDlStep] = useState(1) // 1: Input, 2: OTP, 3: Success
  const [aadhaar, setAadhaar] = useState('')
  const [dlOtp, setDlOtp] = useState('')
  const [dlConsent, setDlConsent] = useState(true)
  const [dlLoading, setDlLoading] = useState(false)
  const [demoOtp, setDemoOtp] = useState('123456')

  // Farmer Auth State
  const [farmerStep, setFarmerStep] = useState(1) // 1: Input, 2: OTP, 3: Success
  const [farmerIdVal, setFarmerIdVal] = useState('')
  const [farmerState, setFarmerState] = useState('Tamil Nadu')
  const [vleId, setVleId] = useState('VLE-TN-4821')
  const [farmerOtp, setFarmerOtp] = useState('')
  const [farmerConsent, setFarmerConsent] = useState(true)
  const [farmerLoading, setFarmerLoading] = useState(false)

  if (!isOpen) return null

  // ---------------- DigiLocker Handlers ----------------
  const handleDlSendOtp = async (e) => {
    e.preventDefault()
    if (aadhaar.length !== 12 || !/^\d+$/.test(aadhaar)) {
      toast.error('Please enter a valid 12-digit Aadhaar number')
      return
    }
    if (!dlConsent) {
      toast.error('Citizen consent is statutory requirement under DPDP Act 2023')
      return
    }

    setDlLoading(true)
    try {
      const { data } = await api.post('/digilocker/send-otp', {
        aadhaar_number: aadhaar,
        channel: 'aadhaar_uidai'
      })
      setDemoOtp(data.demo_otp || '123456')
      setDlStep(2)
      toast.success(data.message || 'OTP sent to UIDAI registered mobile!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to connect to UIDAI Gateway')
    } finally {
      setDlLoading(false)
    }
  }

  const handleDlVerify = async (e) => {
    e.preventDefault()
    if (!dlOtp) {
      toast.error('Please enter the 6-digit OTP')
      return
    }

    setDlLoading(true)
    try {
      await api.post('/digilocker/verify-connect', {
        aadhaar_number: aadhaar,
        otp: dlOtp,
        consent: true,
      })
      toast.success('DigiLocker Government Certificates Authenticated!')
      setDlStep(3)
      setTimeout(() => {
        if (onSuccess) onSuccess()
        onClose()
        setDlStep(1)
        setAadhaar('')
        setDlOtp('')
      }, 1400)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Authentication failed')
    } finally {
      setDlLoading(false)
    }
  }

  // ---------------- Farmer Channel Handlers ----------------
  const handleFarmerSendOtp = async (e) => {
    e.preventDefault()
    if (!farmerIdVal.trim()) {
      toast.error('Please enter the registration or card number')
      return
    }
    if (!farmerConsent) {
      toast.error('Authorization consent is required')
      return
    }

    setFarmerLoading(true)
    try {
      const { data } = await api.post('/digilocker/send-otp', {
        aadhaar_number: farmerIdVal,
        channel: farmerSubTab === 'pm_kisan' ? 'pm_kisan' : 'ration_pds'
      })
      setDemoOtp(data.demo_otp || '123456')
      setFarmerStep(2)
      toast.success(data.message || 'OTP dispatched to registered mobile!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Portal connection failed')
    } finally {
      setFarmerLoading(false)
    }
  }

  const handleFarmerVerify = async (e) => {
    e.preventDefault()
    if (!farmerOtp) {
      toast.error('Please enter the OTP')
      return
    }

    setFarmerLoading(true)
    try {
      await api.post('/digilocker/farmer-auth', {
        auth_type: farmerSubTab,
        identifier: farmerIdVal,
        state: farmerState,
        otp: farmerOtp,
        csc_vle_id: vleId,
        consent: true,
      })
      toast.success('Farmer & Land Records Authenticated via AgriStack!')
      setFarmerStep(3)
      setTimeout(() => {
        if (onSuccess) onSuccess()
        onClose()
        setFarmerStep(1)
        setFarmerIdVal('')
        setFarmerOtp('')
      }, 1400)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Farmer verification failed')
    } finally {
      setFarmerLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/75 backdrop-blur-md flex items-center justify-center p-3 sm:p-4 animate-fade-in overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-xl w-full shadow-2xl border border-slate-200 animate-slide-up relative overflow-hidden my-auto">
        
        {/* National Emblem & Security Header */}
        <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white p-5 border-b border-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center text-2xl shadow-inner">
                🏛️
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-white text-base tracking-tight">
                    National Citizen & Farmer Authentication Gateway
                  </h3>
                </div>
                <div className="flex items-center gap-2 text-[11px] text-blue-200 mt-0.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span>MeitY DigiLocker · PM-KISAN AgriStack · State Revenue Bhulekh</span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white font-bold text-lg p-1 transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Primary Authentication Channels Tab Switcher */}
          <div className="grid grid-cols-2 gap-2 mt-4 bg-slate-800/80 p-1 rounded-2xl border border-slate-700">
            <button
              type="button"
              onClick={() => { setActiveTab('digilocker'); setDlStep(1); }}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                activeTab === 'digilocker'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <span>🇮🇳</span> DigiLocker Online (Aadhaar e-KYC)
            </button>

            <button
              type="button"
              onClick={() => { setActiveTab('farmer'); setFarmerStep(1); }}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                activeTab === 'farmer'
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <span>🌾</span> Farmer & Rural Channel (No DigiLocker)
            </button>
          </div>
        </div>

        {/* ===================== TAB 1: DIGILOCKER ===================== */}
        {activeTab === 'digilocker' && (
          <div className="p-6">
            {dlStep === 1 && (
              <form onSubmit={handleDlSendOtp} className="space-y-4">
                <div className="p-3.5 rounded-2xl bg-blue-50/80 border border-blue-200 text-xs text-blue-900 leading-relaxed flex items-start gap-2.5">
                  <span className="text-xl shrink-0">🛡️</span>
                  <div>
                    <strong className="block font-bold">Government of India National Locker (OAuth 2.0)</strong>
                    Pulls digitally signed certificates from UIDAI, Revenue Department, and State Examination Boards directly into your profile.
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    12-Digit Aadhaar Identification Number *
                  </label>
                  <input
                    type="text"
                    required
                    maxLength={12}
                    placeholder="XXXX XXXX XXXX"
                    className="input-field text-center font-mono text-base font-extrabold tracking-widest text-slate-900 bg-slate-50 focus:bg-white"
                    value={aadhaar}
                    onChange={(e) => setAadhaar(e.target.value.replace(/\D/g, ''))}
                  />
                  <p className="text-[11px] text-slate-500 mt-1">
                    Direct handshake via UIDAI Authentication Server (CIDR). Zero Aadhaar number is stored.
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={dlConsent}
                      onChange={(e) => setDlConsent(e.target.checked)}
                      className="mt-0.5 rounded text-blue-600 focus:ring-blue-500 w-4 h-4"
                    />
                    <span className="text-[11px] text-slate-600 leading-relaxed">
                      <strong>Statutory Consent:</strong> I authorize <em>SmartGov AI</em> to query the National DigiLocker repository for my authenticated certificates (Aadhaar, Income, Community, 12th Marksheet) solely for automated statutory welfare eligibility verification.
                    </span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={dlLoading || aadhaar.length !== 12 || !dlConsent}
                  className="btn-primary w-full py-3 bg-blue-700 hover:bg-blue-800 font-bold text-sm shadow-lg shadow-blue-600/20"
                >
                  {dlLoading ? 'Connecting to UIDAI Gateway...' : 'Send UIDAI Aadhaar OTP →'}
                </button>
              </form>
            )}

            {dlStep === 2 && (
              <form onSubmit={handleDlVerify} className="space-y-4">
                <div className="text-center py-2">
                  <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-700 flex items-center justify-center text-2xl mx-auto mb-2 border border-blue-200">
                    📱
                  </div>
                  <h4 className="font-extrabold text-slate-900 text-sm">Enter UIDAI Verification OTP</h4>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Dispatched to phone registered with Aadhaar ending in <strong>{aadhaar.slice(-4)}</strong>
                  </p>
                </div>

                <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-center">
                  <span className="text-[11px] text-amber-800 font-bold uppercase">Demo Sandbox OTP: </span>
                  <span className="font-mono font-extrabold text-amber-900 tracking-wider text-sm">{demoOtp}</span>
                </div>

                <div>
                  <input
                    type="text"
                    required
                    maxLength={6}
                    placeholder="••••••"
                    className="input-field text-center font-mono text-xl font-bold tracking-[0.4em] text-slate-900"
                    value={dlOtp}
                    onChange={(e) => setDlOtp(e.target.value.replace(/\D/g, ''))}
                    autoFocus
                  />
                </div>

                <div className="flex gap-2.5 pt-2">
                  <button
                    type="button"
                    onClick={() => setDlStep(1)}
                    className="btn-secondary flex-1 py-2.5 text-xs font-semibold"
                  >
                    ← Back
                  </button>
                  <button
                    type="submit"
                    disabled={dlLoading || dlOtp.length < 6}
                    className="btn-primary flex-1 py-2.5 bg-blue-700 hover:bg-blue-800 font-bold text-xs"
                  >
                    {dlLoading ? 'Authenticating with MeitY...' : 'Verify & Fetch Certificates'}
                  </button>
                </div>
              </form>
            )}

            {dlStep === 3 && (
              <div className="py-8 text-center space-y-3">
                <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-3xl mx-auto shadow-inner animate-bounce">
                  ✓
                </div>
                <h3 className="font-extrabold text-slate-900 text-base">DigiLocker Identity Verified!</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Aadhaar e-KYC, Official Income Certificate, Community/Caste Certificate, and HSC Marksheet have been digitally imported with cryptographic SHA-256 signatures.
                </p>
              </div>
            )}
          </div>
        )}

        {/* ===================== TAB 2: FARMER CHANNELS (NO DIGILOCKER) ===================== */}
        {activeTab === 'farmer' && (
          <div className="p-6">
            {farmerStep === 1 && (
              <div className="space-y-4">
                <div className="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-start gap-2.5">
                  <span className="text-xl shrink-0">🌾</span>
                  <div>
                    <strong className="block font-bold">Inclusive Rural & Agricultural Citizen Channels</strong>
                    Tailored for Indian farmers, landholders, and rural citizens who do not use DigiLocker smartphone app.
                  </div>
                </div>

                {/* Farmer Sub-channel Selector */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  {[
                    { id: 'pm_kisan', label: 'PM-KISAN ID', icon: '🚜' },
                    { id: 'land_record', label: 'Land Khata/Patta', icon: '📜' },
                    { id: 'ration_card', label: 'Ration / PDS', icon: '🍚' },
                    { id: 'csc_vle', label: 'CSC e-Seva Center', icon: '🏪' },
                  ].map((sub) => (
                    <button
                      key={sub.id}
                      type="button"
                      onClick={() => setFarmerSubTab(sub.id)}
                      className={`p-2.5 rounded-xl border font-bold text-center transition-all ${
                        farmerSubTab === sub.id
                          ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                          : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      <div className="text-base mb-1">{sub.icon}</div>
                      <div>{sub.label}</div>
                    </button>
                  ))}
                </div>

                <form onSubmit={handleFarmerSendOtp} className="space-y-4 pt-2">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        Home State *
                      </label>
                      <select
                        className="input-field text-xs font-semibold"
                        value={farmerState}
                        onChange={(e) => setFarmerState(e.target.value)}
                      >
                        {INDIAN_STATES.map((st) => (
                          <option key={st} value={st}>{st}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                        {farmerSubTab === 'pm_kisan' && 'PM-KISAN Farmer / Beneficiary ID *'}
                        {farmerSubTab === 'land_record' && 'Land Record / Khata / Patta No *'}
                        {farmerSubTab === 'ration_card' && 'Ration Card / NFSA Smart Card No *'}
                        {farmerSubTab === 'csc_vle' && 'Aadhaar (Assisted Biometric Entry) *'}
                      </label>
                      <input
                        type="text"
                        required
                        className="input-field text-xs font-mono font-bold"
                        placeholder={
                          farmerSubTab === 'pm_kisan' ? 'e.g. TN/2024/98412' :
                          farmerSubTab === 'land_record' ? 'e.g. Khata-482 / Patta-109' :
                          farmerSubTab === 'ration_card' ? 'e.g. 331489201948' :
                          '12-digit Aadhaar number'
                        }
                        value={farmerIdVal}
                        onChange={(e) => setFarmerIdVal(e.target.value)}
                      />
                    </div>
                  </div>

                  {farmerSubTab === 'csc_vle' && (
                    <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs">
                      <label className="block font-bold text-blue-900 mb-1">
                        Authorized CSC Village Level Entrepreneur (VLE) ID
                      </label>
                      <input
                        type="text"
                        className="input-field text-xs font-mono"
                        value={vleId}
                        onChange={(e) => setVleId(e.target.value)}
                        placeholder="VLE-TN-4821"
                      />
                      <p className="text-[11px] text-blue-700 mt-1">
                        Common Service Centre operator physical biometric verification stamp.
                      </p>
                    </div>
                  )}

                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                    <label className="flex items-start gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={farmerConsent}
                        onChange={(e) => setFarmerConsent(e.target.checked)}
                        className="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                      />
                      <span className="text-[11px] text-slate-600 leading-relaxed">
                        I hereby authorize authentication via <strong>{
                          farmerSubTab === 'pm_kisan' ? 'Department of Agriculture PM-KISAN Portal' :
                          farmerSubTab === 'land_record' ? 'State Revenue Land Record (Bhulekh / Patta)' :
                          farmerSubTab === 'ration_card' ? 'Public Distribution System (PDS) e-KYC' :
                          'CSC Village Level Entrepreneur Assisted Verification'
                        }</strong> to link agricultural landholdings and subsidy entitlements.
                      </span>
                    </label>
                  </div>

                  <button
                    type="submit"
                    disabled={farmerLoading || !farmerIdVal.trim() || !farmerConsent}
                    className="btn-primary w-full py-3 bg-emerald-600 hover:bg-emerald-700 font-bold text-sm shadow-lg shadow-emerald-600/20"
                  >
                    {farmerLoading ? 'Connecting to Department Portal...' : 'Verify Farmer Record & Send OTP →'}
                  </button>
                </form>
              </div>
            )}

            {farmerStep === 2 && (
              <form onSubmit={handleFarmerVerify} className="space-y-4">
                <div className="text-center py-2">
                  <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center text-2xl mx-auto mb-2 border border-emerald-200">
                    🌾
                  </div>
                  <h4 className="font-extrabold text-slate-900 text-sm">
                    Enter Verification OTP
                  </h4>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Dispatched to mobile linked with registration <strong>{farmerIdVal}</strong>
                  </p>
                </div>

                <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-center">
                  <span className="text-[11px] text-amber-800 font-bold uppercase">Demo Sandbox OTP: </span>
                  <span className="font-mono font-extrabold text-amber-900 tracking-wider text-sm">{demoOtp}</span>
                </div>

                <div>
                  <input
                    type="text"
                    required
                    maxLength={6}
                    placeholder="••••••"
                    className="input-field text-center font-mono text-xl font-bold tracking-[0.4em] text-slate-900"
                    value={farmerOtp}
                    onChange={(e) => setFarmerOtp(e.target.value.replace(/\D/g, ''))}
                    autoFocus
                  />
                </div>

                <div className="flex gap-2.5 pt-2">
                  <button
                    type="button"
                    onClick={() => setFarmerStep(1)}
                    className="btn-secondary flex-1 py-2.5 text-xs font-semibold"
                  >
                    ← Back
                  </button>
                  <button
                    type="submit"
                    disabled={farmerLoading || farmerOtp.length < 6}
                    className="btn-primary flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-700 font-bold text-xs"
                  >
                    {farmerLoading ? 'Verifying with Department Database...' : 'Authenticate & Link Records'}
                  </button>
                </div>
              </form>
            )}

            {farmerStep === 3 && (
              <div className="py-8 text-center space-y-3">
                <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-3xl mx-auto shadow-inner animate-bounce">
                  ✓
                </div>
                <h3 className="font-extrabold text-slate-900 text-base">Agricultural Identity Verified!</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  PM-KISAN Samman Nidhi Electronic Ledger, Digital Land Record (Patta/Chitta 1.85 Acres), Kisan Credit Card (KCC), and Priority Ration Card authenticated successfully.
                </p>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  )
}
