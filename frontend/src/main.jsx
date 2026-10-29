import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './index.css'
import './i18n/i18n.js'
import { AuthProvider } from './context/AuthContext.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              borderRadius: '12px',
              padding: '12px 16px',
              fontSize: '14px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            },
            success: { iconTheme: { primary: '#0f7a5c', secondary: '#eefaf3' } },
            error: { iconTheme: { primary: '#dc2626', secondary: '#fef2f2' } },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
