import React, { useState, useEffect, useRef } from 'react'
import api from '../../api/axios'

const DIAL_PAD_BUTTONS = [
  { digit: '1', letters: 'EN' },
  { digit: '2', letters: 'தமிழ்' },
  { digit: '3', letters: 'हिंदी' },
  { digit: '4', letters: 'GHI' },
  { digit: '5', letters: '🎤 Voice' },
  { digit: '6', letters: 'MNO' },
  { digit: '7', letters: 'PQRS' },
  { digit: '8', letters: 'TUV' },
  { digit: '9', letters: 'Menu' },
  { digit: '*', letters: 'Clear' },
  { digit: '0', letters: 'Lang' },
  { digit: '#', letters: 'Help' },
]

export default function IVRHelpline() {
  const [phoneNumber, setPhoneNumber] = useState('+91 1800-555-0199')
  const [callActive, setCallActive] = useState(false)
  const [callConnecting, setCallConnecting] = useState(false)
  const [callDuration, setCallDuration] = useState(0)
  const [callSid, setCallSid] = useState('')
  const [currentStep, setCurrentStep] = useState('welcome')
  const [activeLanguage, setActiveLanguage] = useState('en')
  const [audioPrompt, setAudioPrompt] = useState('')
  const [menuOptions, setMenuOptions] = useState([])
  const [audioMuted, setAudioMuted] = useState(false)
  const [isSpeakingVoice, setIsSpeakingVoice] = useState(false)
  const [speechInputText, setSpeechInputText] = useState('')
  const [callLogs, setCallLogs] = useState([])
  const [loadingLogs, setLoadingLogs] = useState(false)
  const [lastRecommendedSchemes, setLastRecommendedSchemes] = useState([])

  const timerRef = useRef(null)
  const recognitionRef = useRef(null)

  // Load past call logs on mount
  useEffect(() => {
    fetchLogs()
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      if (window.speechSynthesis) window.speechSynthesis.cancel()
    }
  }, [])

  const fetchLogs = async () => {
    setLoadingLogs(true)
    try {
      const { data } = await api.get('/ivr/logs?limit=10')
      setCallLogs(data || [])
    } catch (e) {
      console.warn('Could not fetch IVR logs:', e)
    } finally {
      setLoadingLogs(false)
    }
  }

  // Timer effect for active call
  useEffect(() => {
    if (callActive) {
      timerRef.current = setInterval(() => {
        setCallDuration((prev) => prev + 1)
      }, 1000)
    } else {
      if (timerRef.current) clearInterval(timerRef.current)
      setCallDuration(0)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [callActive])

  // Play spoken prompt using Web Speech Synthesis
  const playIVRPrompt = (text, lang) => {
    if (audioMuted || !window.speechSynthesis) return
    window.speechSynthesis.cancel()

    const clean = text.replace(/[*#_`]/g, '')
    const utterance = new SpeechSynthesisUtterance(clean)
    if (lang === 'ta' || /[\u0B80-\u0BFF]/.test(clean)) {
      utterance.lang = 'ta-IN'
      utterance.rate = 0.95
    } else if (lang === 'hi' || /[\u0900-\u097F]/.test(clean)) {
      utterance.lang = 'hi-IN'
      utterance.rate = 0.95
    } else {
      utterance.lang = 'en-IN'
      utterance.rate = 1.0
    }
    window.speechSynthesis.speak(utterance)
  }

  // Play audio DTMF tone
  const playDTMFTone = () => {
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
      const osc = audioCtx.createOscillator()
      const gain = audioCtx.createGain()
      osc.type = 'sine'
      osc.frequency.setValueAtTime(697, audioCtx.currentTime)
      gain.gain.setValueAtTime(0.1, audioCtx.currentTime)
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.15)
      osc.connect(gain)
      gain.connect(audioCtx.destination)
      osc.start()
      osc.stop(audioCtx.currentTime + 0.15)
    } catch (e) {}
  }

  // Start Call
  const handleStartCall = async () => {
    setCallConnecting(true)
    setLastRecommendedSchemes([])
    try {
      const { data } = await api.post('/ivr/call/start', {
        phone_number: phoneNumber,
      })
      setCallSid(data.call_sid)
      setCurrentStep(data.current_step)
      setAudioPrompt(data.prompt)
      setMenuOptions(data.options || [])
      setCallActive(true)
      playIVRPrompt(data.prompt, 'en')
    } catch (err) {
      alert('Could not connect IVR call: ' + (err.response?.data?.detail || err.message))
    } finally {
      setCallConnecting(false)
    }
  }

  // Send Keypress (DTMF)
  const handlePressDigit = async (digit) => {
    playDTMFTone()
    if (!callActive) {
      // Just typing number into phone display
      if (digit === '*') {
        setPhoneNumber('')
      } else {
        setPhoneNumber((prev) => prev + digit)
      }
      return
    }

    try {
      const { data } = await api.post('/ivr/call/action', {
        call_sid: callSid,
        digit: digit,
        current_step: currentStep,
      })

      setCurrentStep(data.current_step)
      setAudioPrompt(data.prompt)
      setMenuOptions(data.options || [])
      if (data.language) setActiveLanguage(data.language)
      if (data.schemes) setLastRecommendedSchemes(data.schemes)

      playIVRPrompt(data.prompt, data.language || activeLanguage)

      if (data.current_step === 'call_ended') {
        setTimeout(() => handleEndCall(), 3000)
      }
    } catch (err) {
      console.error('IVR action error:', err)
    }
  }

  // Voice Speech via IVR (Option 5)
  const handleVoiceQuestion = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert('Speech recognition is not available in this browser. Please type your query.')
      return
    }

    if (window.speechSynthesis) window.speechSynthesis.cancel()

    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = activeLanguage === 'ta' ? 'ta-IN' : (activeLanguage === 'hi' ? 'hi-IN' : 'en-IN')

    setIsSpeakingVoice(true)

    recognition.onresult = async (event) => {
      const spokenText = event.results[0][0].transcript
      setIsSpeakingVoice(false)
      setSpeechInputText(spokenText)

      try {
        const { data } = await api.post('/ivr/call/action', {
          call_sid: callSid,
          speech_text: spokenText,
          current_step: 'speech_input',
        })

        setCurrentStep(data.current_step)
        setAudioPrompt(data.prompt)
        setMenuOptions(data.options || [])
        if (data.schemes) setLastRecommendedSchemes(data.schemes)
        playIVRPrompt(data.prompt, activeLanguage)
      } catch (err) {
        console.error('Speech action error:', err)
      }
    }

    recognition.onerror = () => {
      setIsSpeakingVoice(false)
    }

    recognitionRef.current = recognition
    recognition.start()
  }

  // End Call
  const handleEndCall = () => {
    if (window.speechSynthesis) window.speechSynthesis.cancel()
    setCallActive(false)
    setCallSid('')
    setCurrentStep('welcome')
    setAudioPrompt('Call ended. Thank you for using SmartGov IVRS Helpline.')
    setMenuOptions([])
    fetchLogs()
  }

  const formatDuration = (secs) => {
    const mins = Math.floor(secs / 60)
    const remaining = secs % 60
    return `${mins.toString().padStart(2, '0')}:${remaining.toString().padStart(2, '0')}`
  }

  return (
    <div className="max-w-6xl mx-auto animate-fade-in pb-8">
      {/* Page Title & Intro */}
      <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="page-title flex items-center gap-2.5">
            <span className="text-2xl">📞</span>
            <span>SmartGov AI — Interactive Voice Response (IVRS)</span>
            <span className="text-xs bg-emerald-100 text-emerald-800 font-bold px-2.5 py-0.5 rounded-full border border-emerald-200">
              Live Phone Helpline 1800-555-0199
            </span>
          </h1>
          <p className="page-subtitle">
            Telephonic citizen assistance with Tamil, English, and Hindi voice navigation, DTMF touch-tone, and AI speech reasoning.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAudioMuted(!audioMuted)}
            className={`btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 ${audioMuted ? 'bg-rose-50 text-rose-700' : ''}`}
            title="Toggle voice prompt speech"
          >
            <span>{audioMuted ? '🔇 Audio Muted' : '🔊 Audio Active'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT COLUMN: Interactive Phone Dialer Simulator */}
        <div className="lg:col-span-5 flex flex-col items-center">
          <div className="w-full max-w-sm bg-gradient-to-b from-slate-900 to-slate-950 rounded-3xl p-5 shadow-2xl border-4 border-slate-800 text-white flex flex-col justify-between">
            {/* Phone Screen Display */}
            <div className="bg-slate-800/90 rounded-2xl p-4 border border-slate-700/80 mb-4 shadow-inner">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span className="flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${callActive ? 'bg-emerald-500 animate-ping' : 'bg-slate-500'}`} />
                  {callActive ? 'CALL IN PROGRESS' : 'STANDBY (TOLL-FREE)'}
                </span>
                <span className="font-mono text-emerald-400 font-bold">
                  {callActive ? formatDuration(callDuration) : '1800-555-0199'}
                </span>
              </div>

              {/* Status / Dialed Number */}
              <div className="text-center py-2">
                <div className="text-lg font-bold tracking-wider font-mono text-white">
                  {phoneNumber || 'SmartGov Helpline'}
                </div>
                <div className="text-xs text-blue-400 font-medium mt-0.5">
                  {callActive ? (
                    <span className="flex items-center justify-center gap-1">
                      <span>Language:</span>
                      <strong className="uppercase font-bold text-amber-300">
                        {activeLanguage === 'ta' ? 'தமிழ் (Tamil)' : (activeLanguage === 'hi' ? 'हिंदी (Hindi)' : 'English')}
                      </strong>
                    </span>
                  ) : (
                    'Ready to connect citizen call'
                  )}
                </div>
              </div>

              {/* Live Speaker Text Display */}
              {callActive && (
                <div className="mt-2 bg-slate-900/90 rounded-xl p-2.5 border border-slate-700 text-xs text-slate-200 min-h-[60px] max-h-[110px] overflow-y-auto leading-relaxed scrollbar-thin">
                  <div className="font-semibold text-blue-400 flex items-center justify-between mb-0.5">
                    <span>📢 Helpline Speaker:</span>
                    <button
                      onClick={() => playIVRPrompt(audioPrompt, activeLanguage)}
                      className="text-[10px] text-slate-400 hover:text-white underline"
                    >
                      Replay ↺
                    </button>
                  </div>
                  {audioPrompt}
                </div>
              )}
            </div>

            {/* Keypad Buttons */}
            <div className="grid grid-cols-3 gap-2.5 mb-5 px-2">
              {DIAL_PAD_BUTTONS.map(({ digit, letters }) => (
                <button
                  key={digit}
                  onClick={() => handlePressDigit(digit)}
                  className="bg-slate-800 hover:bg-slate-700 active:scale-95 transition-all text-white rounded-2xl py-3 flex flex-col items-center justify-center border border-slate-700/60 shadow-sm group"
                >
                  <span className="text-xl font-bold tracking-tight leading-none group-hover:text-blue-400">
                    {digit}
                  </span>
                  <span className="text-[10px] font-medium text-slate-400 tracking-wider uppercase mt-1">
                    {letters}
                  </span>
                </button>
              ))}
            </div>

            {/* Call Control Buttons */}
            <div className="flex items-center justify-center gap-4 pt-1">
              {!callActive ? (
                <button
                  onClick={handleStartCall}
                  disabled={callConnecting}
                  className="w-full bg-emerald-600 hover:bg-emerald-500 active:scale-95 transition-all text-white font-bold py-3.5 px-6 rounded-2xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30 text-sm"
                >
                  <span className="text-lg">📞</span>
                  <span>{callConnecting ? 'Dialing Helpline...' : 'Start Phone Call'}</span>
                </button>
              ) : (
                <div className="w-full flex items-center gap-2.5">
                  {/* Option 5 Voice Speaking Button */}
                  <button
                    onClick={handleVoiceQuestion}
                    className={`flex-1 ${
                      isSpeakingVoice ? 'bg-amber-500 animate-pulse' : 'bg-blue-600 hover:bg-blue-500'
                    } text-white font-semibold py-3 px-3 rounded-2xl flex items-center justify-center gap-1.5 text-xs transition-colors`}
                    title="Speak your question directly"
                  >
                    <span>🎤</span>
                    <span>{isSpeakingVoice ? 'Listening...' : 'Speak Question'}</span>
                  </button>

                  <button
                    onClick={handleEndCall}
                    className="flex-1 bg-rose-600 hover:bg-rose-500 text-white font-bold py-3 px-3 rounded-2xl flex items-center justify-center gap-1.5 text-xs shadow-lg shadow-rose-600/30 transition-colors"
                  >
                    <span>🛑</span>
                    <span>End Call</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Active Menu Flow, Scheme Results & Telephony Status */}
        <div className="lg:col-span-7 space-y-5">
          {/* Active Call Navigation Menu Cards */}
          <div className="card shadow-sm border-l-4 border-l-blue-600">
            <h2 className="text-base font-bold text-slate-900 flex items-center justify-between mb-3">
              <span className="flex items-center gap-2">
                <span>📋</span>
                <span>Active IVR Menu & Options</span>
              </span>
              {callActive && (
                <span className="text-xs bg-blue-50 text-blue-700 font-semibold px-2 py-0.5 rounded-full border border-blue-200">
                  Step: {currentStep}
                </span>
              )}
            </h2>

            {menuOptions.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {menuOptions.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => handlePressDigit(opt.digit)}
                    className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-blue-50/70 hover:border-blue-300 text-left transition-all group"
                  >
                    <span className="w-7 h-7 rounded-lg bg-slate-900 text-white font-bold flex items-center justify-center text-xs group-hover:bg-blue-600 transition-colors">
                      {opt.digit}
                    </span>
                    <span className="text-xs font-semibold text-slate-800 leading-tight">
                      {opt.label}
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 text-slate-500 text-xs">
                {callActive ? (
                  <span>Listening to speech question or processing request...</span>
                ) : (
                  <span>Click <strong>"Start Phone Call"</strong> on the dialer to begin the interactive helpline session.</span>
                )}
              </div>
            )}
          </div>

          {/* Scheme Result Cards (When retrieved via IVR) */}
          {lastRecommendedSchemes.length > 0 && (
            <div className="card shadow-sm border border-emerald-200 bg-emerald-50/30">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 flex items-center gap-1.5 mb-2.5">
                <span>🏛️</span>
                <span>Schemes Retrieved by Phone Agent:</span>
              </h3>
              <div className="space-y-2">
                {lastRecommendedSchemes.map((s, idx) => (
                  <div key={idx} className="bg-white p-3 rounded-xl border border-emerald-100 shadow-xs text-xs">
                    <div className="flex items-center justify-between font-bold text-slate-900 mb-1">
                      <span>{s.title}</span>
                      <span className="text-[11px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold">
                        {s.eligibility_status || 'Eligible'}
                      </span>
                    </div>
                    <p className="text-slate-600 mb-2">{s.benefits}</p>
                    {s.official_link && (
                      <a
                        href={s.official_link}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 font-bold hover:underline inline-flex items-center gap-1"
                      >
                        Official Portal ↗
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Telephony Architecture & Webhook Documentation */}
          <div className="card shadow-sm bg-slate-50 border border-slate-200 text-xs text-slate-600">
            <h3 className="font-bold text-slate-900 text-sm mb-2 flex items-center gap-1.5">
              <span>⚙️</span>
              <span>Twilio / Cloud PBX Live Telephony Integration</span>
            </h3>
            <p className="mb-2">
              SmartGov AI conforms to standard telephony standards. You can bind any real Indian phone number (or Twilio/Exotel number) to the following webhook endpoints:
            </p>
            <div className="space-y-1.5 font-mono text-[11px] bg-white p-3 rounded-xl border border-slate-200">
              <div><strong className="text-emerald-700">POST</strong> /api/ivr/incoming <span className="text-slate-400"># Handles inbound phone calls & language TwiML</span></div>
              <div><strong className="text-blue-700">POST</strong> /api/ivr/menu <span className="text-slate-400"># Handles DTMF digits & voice question speech recognition</span></div>
            </div>
          </div>

          {/* Past Call Logs */}
          <div className="card shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                <span>📞</span>
                <span>Recent Helpline Call History</span>
              </h3>
              <button
                onClick={fetchLogs}
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold"
              >
                Refresh ↺
              </button>
            </div>

            {callLogs.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 uppercase text-[10px] tracking-wider">
                      <th className="py-2 px-2">Call SID</th>
                      <th className="py-2 px-2">Caller</th>
                      <th className="py-2 px-2">Language</th>
                      <th className="py-2 px-2">DTMF Path</th>
                      <th className="py-2 px-2">Status</th>
                      <th className="py-2 px-2">Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {callLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-50">
                        <td className="py-2 px-2 font-mono text-[11px] text-slate-600">{log.call_sid?.slice(0, 14)}...</td>
                        <td className="py-2 px-2 font-medium">{log.caller_phone || 'Citizen'}</td>
                        <td className="py-2 px-2 font-semibold uppercase text-blue-700">{log.language}</td>
                        <td className="py-2 px-2 font-mono text-slate-500">{log.dtmf_digits || 'Voice'}</td>
                        <td className="py-2 px-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${log.status === 'completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'}`}>
                            {log.status}
                          </span>
                        </td>
                        <td className="py-2 px-2 text-slate-400 text-[10px]">
                          {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-400 text-xs italic py-2 text-center">No call logs yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
