import React, { useState, useRef, useEffect } from 'react'
import api from '../../api/axios'

const PROMPT_SUGGESTIONS = [
  { text: '🎓 I am a college student, what scholarships can I get?', query: 'I am a college student. Which government scholarships might I qualify for?' },
  { text: '🌾 விவசாயிகளுக்கு ₹6000 உதவித்தொகை திட்டம் எப்படி பெறுவது?', query: 'விவசாயிகளுக்கு ₹6000 உதவித்தொகை திட்டம் எப்படி பெறுவது? என்ன ஆவணங்கள் தேவை?' },
  { text: '🏥 ஆயுஷ்மான் பாரத் ₹5 லட்சம் மருத்துவ காப்பீடு தகுதி என்ன?', query: 'ஆயுஷ்மான் பாரத் மருத்துவ காப்பீடு தகுதி என்ன? யார் விண்ணப்பிக்கலாம்?' },
  { text: '💼 Enakku business thodanga Mudra loan kedaikkuma?', query: 'Enakku puthiya business thodanga Mudra loan kedaikkuma? How to apply?' },
  { text: '🌸 What schemes are available for women and girl children?', query: 'What schemes are available for women and girl child welfare?' },
  { text: '👴 முதியோர் உதவித்தொகை திட்டம் மற்றும் ஓய்வூதியம்', query: 'முதியோர் உதவித்தொகை மற்றும் ஓய்வூதிய திட்டங்கள் என்னென்ன உள்ளன?' },
]

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'வணக்கம்! Welcome to SMARTGOV AI.\n\nI am your verified Government Scheme Assistant. You can speak or type in English, தமிழ் (Tamil), Tanglish, or any Indian language. I will automatically recognize your language and answer using official government records.',
      schemes: [],
      followUps: [],
      detectedLang: 'en',
    },
  ])
  const [input, setInput] = useState('')
  const [interimText, setInterimText] = useState('')
  const [sending, setSending] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(false)
  const [speechError, setSpeechError] = useState('')
  const [lastUpdateInfo, setLastUpdateInfo] = useState(null)
  const [recordingMode, setRecordingMode] = useState('browser') // 'browser' or 'cloud'

  const endRef = useRef(null)
  const inputRef = useRef(null)
  const recognitionRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  useEffect(() => {
    inputRef.current?.focus()

    // Fetch update status
    api.get('/updates/status')
      .then((res) => setLastUpdateInfo(res.data))
      .catch(() => {})

    // Check Speech Recognition support in browser
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      setSpeechSupported(true)
    } else if (navigator.mediaDevices && window.MediaRecorder) {
      // Browser doesn't have Web Speech API, but has MediaRecorder (cloud fallback)
      setSpeechSupported(true)
      setRecordingMode('cloud')
    }
  }, [])

  const startBrowserRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) return false

    try {
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = true
      recognition.maxAlternatives = 3

      // Try device locale or default
      const userLang = navigator.language || 'ta-IN'
      // If user language includes ta, set ta-IN, else keep browser default
      if (userLang.startsWith('ta')) {
        recognition.lang = 'ta-IN'
      } else if (userLang.startsWith('hi')) {
        recognition.lang = 'hi-IN'
      } else {
        recognition.lang = 'en-IN'
      }

      let finalTranscript = ''

      recognition.onstart = () => {
        setIsListening(true)
        setSpeechError('')
        setInterimText('Listening... பேசலாம் / Speak now')
      }

      recognition.onresult = (event) => {
        let currentInterim = ''
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const item = event.results[i]
          if (item.isFinal) {
            finalTranscript += item[0].transcript
          } else {
            currentInterim += item[0].transcript
          }
        }

        if (currentInterim) {
          setInterimText(currentInterim)
          setInput(finalTranscript + (finalTranscript ? ' ' : '') + currentInterim)
        } else if (finalTranscript) {
          setInterimText('')
          setInput(finalTranscript)
        }
      }

      recognition.onerror = (event) => {
        setIsListening(false)
        setInterimText('')
        console.warn('SpeechRecognition error:', event.error)
        if (event.error === 'no-speech') {
          setSpeechError('No speech detected. Please speak clearly into your microphone.')
        } else if (event.error === 'not-allowed') {
          setSpeechError('Microphone permission denied. Please allow microphone access in your browser settings.')
        } else if (event.error === 'network') {
          setSpeechError('Network issue with speech recognition. Switching to audio recording fallback...')
          // Fallback to audio recorder
          startMediaRecording()
          return
        } else {
          setSpeechError(`Speech error: ${event.error}. You can also type your question directly.`)
        }
        setTimeout(() => setSpeechError(''), 5000)
      }

      recognition.onend = () => {
        setIsListening(false)
        setInterimText('')
        if (finalTranscript && finalTranscript.trim()) {
          sendMessage(finalTranscript.trim())
        }
      }

      recognitionRef.current = recognition
      recognition.start()
      return true
    } catch (err) {
      console.warn('Could not start SpeechRecognition:', err)
      return false
    }
  }

  const startMediaRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setSpeechError('Microphone audio recording is not supported in this browser.')
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []
      const mediaRecorder = new MediaRecorder(stream)

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop())
        setIsListening(false)
        setInterimText('Transcribing audio...')

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        if (audioBlob.size < 500) {
          setInterimText('')
          setSpeechError('Audio recording was too short. Please speak clearly.')
          setTimeout(() => setSpeechError(''), 4000)
          return
        }

        const formData = new FormData()
        formData.append('file', audioBlob, 'speech_input.webm')

        try {
          const { data } = await api.post('/speech/transcribe', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })
          setInterimText('')
          if (data.text && data.text.trim()) {
            setInput(data.text)
            sendMessage(data.text)
          } else {
            setSpeechError('Could not transcribe audio. Please type your query.')
            setTimeout(() => setSpeechError(''), 4000)
          }
        } catch (postErr) {
          setInterimText('')
          const errMsg = postErr.response?.data?.detail || 'Speech service unavailable. Please type your query.'
          setSpeechError(`Speech service: ${errMsg}`)
          setTimeout(() => setSpeechError(''), 6000)
        }
      }

      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start()
      setIsListening(true)
      setRecordingMode('cloud')
      setInterimText('Recording audio... Click stop when finished.')
    } catch (err) {
      setIsListening(false)
      setInterimText('')
      setSpeechError('Microphone permission was denied or not available.')
      setTimeout(() => setSpeechError(''), 5000)
    }
  }

  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop() } catch (e) {}
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        try { mediaRecorderRef.current.stop() } catch (e) {}
      }
      setIsListening(false)
      setInterimText('')
      return
    }

    setSpeechError('')
    const started = startBrowserRecognition()
    if (!started) {
      startMediaRecording()
    }
  }

  const speakText = (text) => {
    if (!window.speechSynthesis) return
    window.speechSynthesis.cancel()
    const cleanText = text.replace(/[*#_`]/g, '')
    const utterance = new SpeechSynthesisUtterance(cleanText.slice(0, 300))
    // Automatically match voice to text script if possible
    if (/[\u0B80-\u0BFF]/.test(cleanText)) {
      utterance.lang = 'ta-IN'
    } else if (/[\u0900-\u097F]/.test(cleanText)) {
      utterance.lang = 'hi-IN'
    } else {
      utterance.lang = 'en-IN'
    }
    window.speechSynthesis.speak(utterance)
  }

  const sendMessage = async (textToSend) => {
    const text = textToSend || input
    if (!text.trim() || sending) return

    const userMsg = { role: 'user', text: text.trim() }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setInterimText('')
    setSending(true)

    try {
      const { data } = await api.post('/chatbot', {
        message: userMsg.text,
      })

      const botMsg = {
        role: 'assistant',
        text: data.reply,
        schemes: data.schemes_recommended || [],
        followUps: data.follow_up_questions || [],
        detectedLang: data.detected_language || 'en',
        tools: data.tool_calls_executed || [],
        disclaimer: data.disclaimer,
      }

      setMessages((m) => [...m, botMsg])
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          text: 'மன்னிக்கவும் / Sorry, an error occurred while connecting to the government schemes knowledge base. Please try asking again.',
          schemes: [],
          followUps: [],
        },
      ])
    } finally {
      setSending(false)
      inputRef.current?.focus()
    }
  }

  const handleSend = (e) => {
    e.preventDefault()
    sendMessage()
  }

  const handleClear = () => {
    setMessages([
      {
        role: 'assistant',
        text: 'Chat history cleared. How can I assist you with government schemes today?',
        schemes: [],
        followUps: [],
      },
    ])
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'likely_eligible':
        return <span className="bg-emerald-100 text-emerald-800 text-xs px-2.5 py-0.5 rounded-full font-semibold">✅ Likely Eligible</span>
      case 'needs_more_information':
        return <span className="bg-amber-100 text-amber-800 text-xs px-2.5 py-0.5 rounded-full font-semibold">ℹ️ Needs More Info</span>
      case 'not_eligible':
        return <span className="bg-rose-100 text-rose-800 text-xs px-2.5 py-0.5 rounded-full font-semibold">❌ Not Eligible</span>
      default:
        return <span className="bg-slate-100 text-slate-800 text-xs px-2.5 py-0.5 rounded-full font-semibold">🔍 Unverified</span>
    }
  }

  return (
    <div className="max-w-4xl mx-auto animate-fade-in pb-4">
      {/* Header */}
      <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <span>💬 SmartGov AI Agent</span>
            <span className="text-xs bg-blue-100 text-blue-800 font-medium px-2 py-0.5 rounded-md">
              Multilingual (Tamil • English • Indian Languages)
            </span>
          </h1>
          <p className="page-subtitle">
            Deterministic rule-based eligibility evaluation & verified government welfare assistance
          </p>
        </div>
        <div className="flex items-center gap-2">
          {lastUpdateInfo && (
            <span className="text-[11px] text-slate-500 bg-slate-100 border border-slate-200 px-2.5 py-1 rounded-lg">
              🛡️ Verified: {new Date(lastUpdateInfo.last_successful_update || Date.now()).toLocaleDateString()}
            </span>
          )}
          <button
            onClick={handleClear}
            className="btn-secondary text-xs py-1.5 px-3 hover:bg-slate-100"
            title="Clear conversation history"
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      {speechError && (
        <div className="mb-3 bg-amber-50 border border-amber-200 text-amber-800 text-xs p-2.5 rounded-lg flex items-center justify-between animate-fade-in">
          <span>⚠️ {speechError}</span>
          <button onClick={() => setSpeechError('')} className="font-bold ml-2">×</button>
        </div>
      )}

      {/* Main Chat Box */}
      <div className="card flex flex-col shadow-sm bg-white" style={{ height: 'calc(100vh - 210px)' }}>
        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto flex flex-col gap-4 pr-2 pb-3">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-[92%] md:max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed animate-slide-up ${
                m.role === 'user'
                  ? 'bg-gradient-to-r from-blue-700 to-indigo-800 text-white self-end rounded-br-none shadow-sm'
                  : 'bg-slate-50 text-slate-800 self-start rounded-bl-none border border-slate-200 shadow-xs'
              }`}
            >
              {m.role === 'assistant' && (
                <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-200/70">
                  <div className="flex items-center gap-1.5">
                    <span className="text-base">🏛️</span>
                    <span className="text-xs font-bold text-slate-800">SmartGov AI Agent</span>
                    {m.detectedLang && (
                      <span className="text-[10px] bg-slate-200/80 text-slate-700 font-semibold px-1.5 py-0.2 rounded">
                        {m.detectedLang.toUpperCase()} Auto-Detected
                      </span>
                    )}
                  </div>
                  {window.speechSynthesis && (
                    <button
                      onClick={() => speakText(m.text)}
                      className="text-xs text-slate-500 hover:text-blue-600 transition-colors p-1"
                      title="Read out response"
                    >
                      🔊 Listen
                    </button>
                  )}
                </div>
              )}

              {/* Message text */}
              <div className="whitespace-pre-wrap leading-relaxed font-sans">{m.text}</div>

              {/* Follow-up Question Chips */}
              {m.followUps && m.followUps.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-200/60">
                  <div className="flex items-center gap-2 flex-wrap">
                    {m.followUps.map((q, idx) => (
                      <div key={idx} className="bg-amber-50 border border-amber-200 text-amber-900 text-xs px-3 py-1.5 rounded-lg flex items-center gap-1.5">
                        <span>❓</span>
                        <span>{q}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommended Scheme Cards */}
              {m.schemes && m.schemes.length > 0 && (
                <div className="mt-3.5 space-y-3">
                  <p className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    📋 Verified Scheme Details:
                  </p>
                  {m.schemes.map((scheme, sIdx) => (
                    <div
                      key={sIdx}
                      className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-xs hover:border-blue-300 transition-all text-xs"
                    >
                      <div className="flex items-start justify-between gap-2 mb-1.5">
                        <div>
                          <h4 className="font-bold text-sm text-slate-900 leading-snug">
                            {scheme.title}
                          </h4>
                          <p className="text-[11px] text-slate-500">
                            {scheme.department || 'Government of India'} • For: {scheme.target_group || 'Eligible Citizens'}
                          </p>
                        </div>
                        {getStatusBadge(scheme.eligibility_status)}
                      </div>

                      <div className="mt-2 bg-slate-50 rounded-lg p-2 border border-slate-100">
                        <span className="font-semibold text-slate-700">🎁 Benefits: </span>
                        <span className="text-slate-600">{scheme.benefits}</span>
                      </div>

                      {/* Reasons & missing info */}
                      {scheme.reasons && scheme.reasons.length > 0 && (
                        <div className="mt-2 text-slate-700">
                          <span className="font-semibold text-slate-800">Criteria Evaluated:</span>
                          <ul className="list-disc list-inside mt-0.5 space-y-0.5 text-slate-600">
                            {scheme.reasons.map((r, rIdx) => (
                              <li key={rIdx}>{r}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Required Documents */}
                      {scheme.required_documents && scheme.required_documents.length > 0 && (
                        <div className="mt-2">
                          <span className="font-semibold text-slate-800">📄 Required Documents:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {scheme.required_documents.map((doc, dIdx) => (
                              <span key={dIdx} className="bg-blue-50 text-blue-800 text-[11px] px-2 py-0.5 rounded border border-blue-100">
                                {doc}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Application Steps */}
                      {scheme.application_steps && scheme.application_steps.length > 0 && (
                        <div className="mt-2">
                          <span className="font-semibold text-slate-800">🚀 Application Steps:</span>
                          <div className="text-slate-600 space-y-0.5 mt-0.5 text-[11px]">
                            {scheme.application_steps.slice(0, 3).map((step, stIdx) => (
                              <div key={stIdx}>{step}</div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Official Link & Provenance */}
                      <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between flex-wrap gap-2 text-[11px]">
                        <span className="text-slate-400">
                          {scheme.data_confidence}
                        </span>
                        {scheme.official_link && (
                          <a
                            href={scheme.official_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 hover:underline"
                          >
                            <span>Official Portal</span>
                            <span>↗</span>
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Disclaimer */}
              {m.role === 'assistant' && (
                <div className="mt-2 text-[10px] text-slate-400 italic">
                  * SmartGov AI preliminary evaluation does not constitute final government approval.
                </div>
              )}
            </div>
          ))}

          {isListening && interimText && (
            <div className="self-start bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl rounded-bl-none px-4 py-2.5 text-xs animate-pulse flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-600 animate-ping"></span>
              <span className="font-medium">🎤 {interimText}</span>
            </div>
          )}

          {sending && (
            <div className="self-start bg-slate-50 border border-slate-200 rounded-2xl rounded-bl-none px-4 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-blue-700">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span>Identifying language & querying verified government scheme engine...</span>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Suggested Questions */}
        {messages.length <= 2 && (
          <div className="py-2.5 px-2 border-t border-slate-100">
            <p className="text-[11px] font-semibold text-slate-500 mb-1.5">⚡ Suggested queries (Tamil & English):</p>
            <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
              {PROMPT_SUGGESTIONS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(s.query)}
                  className="bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-200 text-slate-700 text-xs px-3 py-1.5 rounded-full whitespace-nowrap transition-colors"
                >
                  {s.text}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Bar */}
        <form onSubmit={handleSend} className="flex gap-2 pt-2.5 border-t border-slate-100">
          <input
            ref={inputRef}
            className="input-field flex-1 text-sm"
            placeholder={isListening ? "Listening to your voice..." : "Type in Tamil, English, Tanglish, or any language... (எ.கா. கல்லூரி மாணவர் உதவித்தொகை)"}
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          {/* Voice input button with dual engine (Web Speech + Audio Recorder fallback) */}
          {speechSupported && (
            <button
              type="button"
              onClick={toggleListening}
              className={`px-3 py-2 rounded-xl border text-sm transition-all flex items-center gap-1.5 justify-center font-medium ${
                isListening
                  ? 'bg-rose-600 text-white border-rose-700 shadow-md animate-pulse'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200 hover:border-slate-300'
              }`}
              title={isListening ? 'Listening... Click to send or stop' : 'Click to speak in Tamil, English, or any Indian language'}
            >
              <span>{isListening ? '🛑' : '🎤'}</span>
              <span className="text-xs hidden sm:inline">{isListening ? 'Stop' : 'Speak'}</span>
            </button>
          )}

          <button
            type="submit"
            className="btn-primary px-5 flex items-center gap-1.5"
            disabled={sending || !input.trim()}
          >
            <span>Send</span>
            <span>→</span>
          </button>
        </form>
      </div>
    </div>
  )
}
