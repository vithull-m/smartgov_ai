import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'

const LANGS = [
  { code: 'en', label: 'English' },
  { code: 'ta', label: 'தமிழ்' },
  { code: 'hi', label: 'हिंदी' },
]

const NAV_ITEMS = [
  { to: '/dashboard', key: 'nav_dashboard', icon: '📊', label: 'Dashboard' },
  { to: '/schemes', key: 'nav_schemes', icon: '🏛️', label: 'Schemes' },
  { to: '/applications', key: 'nav_applications', icon: '📝', label: 'Tracker' },
  { to: '/family', key: 'nav_family', icon: '👨‍👩‍👧', label: 'Family' },
  { to: '/saved', key: 'nav_saved', icon: '⭐', label: 'Saved' },
  { to: '/compare', key: 'nav_compare', icon: '⚖️', label: 'Compare' },
  { to: '/chatbot', key: 'nav_chatbot', icon: '💬', label: 'AI Assistant' },
  { to: '/ivr', key: 'nav_ivr', icon: '📞', label: 'IVRS Helpline' },
]


export default function Navbar() {
  const { user, logout, isAdmin } = useAuth()
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const [userDropdown, setUserDropdown] = useState(false)

  const changeLang = (code) => {
    i18n.changeLanguage(code)
    localStorage.setItem('sg_lang', code)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
    setMenuOpen(false)
    setUserDropdown(false)
  }

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/')

  return (
    <nav className="bg-slate-900/95 backdrop-blur-md text-white sticky top-0 z-50 border-b border-slate-800 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 group" onClick={() => setMenuOpen(false)}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-sky-400 flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <span className="text-lg">🏛️</span>
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-base tracking-tight text-white group-hover:text-blue-200 transition-colors">
                SmartGov<span className="text-blue-400 font-medium">.ai</span>
              </span>
              <span className="text-[10px] text-slate-400 font-medium tracking-wide -mt-1 uppercase">
                Citizen Portal
              </span>
            </div>
          </Link>

          {/* Desktop Nav Items */}
          {user && (
            <div className="hidden lg:flex items-center gap-1 bg-slate-800/40 px-2 py-1.5 rounded-2xl border border-slate-800/80">
              {NAV_ITEMS.map(({ to, icon, label }) => (
                <Link
                  key={to}
                  to={to}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 ${
                    isActive(to)
                      ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <span className="text-sm">{icon}</span>
                  <span>{label}</span>
                </Link>
              ))}
              {isAdmin && (
                <Link
                  to="/admin"
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 ${
                    isActive('/admin')
                      ? 'bg-amber-600 text-white shadow-sm'
                      : 'text-amber-400 hover:text-amber-300 hover:bg-slate-800'
                  }`}
                >
                  <span>⚙️</span>
                  <span>Admin</span>
                </Link>
              )}
            </div>
          )}

          {/* Right Controls */}
          <div className="flex items-center gap-3">
            {/* Language Switcher */}
            <div className="relative">
              <select
                className="bg-slate-800 text-slate-200 text-xs font-medium rounded-xl px-2.5 py-1.5 border border-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
                value={i18n.language}
                onChange={(e) => changeLang(e.target.value)}
              >
                {LANGS.map((l) => (
                  <option key={l.code} value={l.code} className="bg-slate-800 text-white">
                    {l.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Profile Dropdown or Auth Button */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setUserDropdown(!userDropdown)}
                  className="flex items-center gap-2 p-1.5 pl-2.5 rounded-xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 transition-colors"
                >
                  <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">
                    {user.full_name ? user.full_name[0].toUpperCase() : 'U'}
                  </div>
                  <span className="text-xs font-semibold text-slate-200 hidden sm:inline">
                    {user.full_name ? user.full_name.split(' ')[0] : 'Profile'}
                  </span>
                  <span className="text-[10px] text-slate-400">▼</span>
                </button>

                {userDropdown && (
                  <div className="absolute right-0 mt-2 w-48 rounded-xl bg-white text-slate-800 shadow-xl border border-slate-200 py-1.5 z-50 animate-slide-down">
                    <div className="px-3.5 py-2 border-b border-slate-100">
                      <p className="text-xs font-bold text-slate-900 truncate">{user.full_name}</p>
                      <p className="text-[11px] text-slate-500 truncate">{user.email}</p>
                    </div>
                    <Link
                      to="/profile"
                      onClick={() => setUserDropdown(false)}
                      className="block px-3.5 py-2 text-xs font-medium hover:bg-slate-50 text-slate-700"
                    >
                      👤 Your Citizen Profile
                    </Link>
                    <Link
                      to="/applications"
                      onClick={() => setUserDropdown(false)}
                      className="block px-3.5 py-2 text-xs font-medium hover:bg-slate-50 text-slate-700"
                    >
                      📋 Tracked Applications
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-3.5 py-2 text-xs font-semibold text-rose-600 hover:bg-rose-50 border-t border-slate-100 mt-1"
                    >
                      🚪 Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="text-xs bg-blue-600 hover:bg-blue-500 text-white font-semibold px-4 py-2 rounded-xl transition-colors shadow-sm"
              >
                Sign In
              </Link>
            )}

            {/* Mobile Menu Button */}
            {user && (
              <button
                className="lg:hidden p-2 rounded-xl hover:bg-slate-800 text-slate-300"
                onClick={() => setMenuOpen(!menuOpen)}
                aria-label="Toggle menu"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {menuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Mobile Nav Drawer */}
        {menuOpen && user && (
          <div className="lg:hidden border-t border-slate-800 py-3 space-y-1 animate-slide-down">
            {NAV_ITEMS.map(({ to, icon, label }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isActive(to) ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <span className="text-base">{icon}</span>
                <span>{label}</span>
              </Link>
            ))}
            {isAdmin && (
              <Link
                to="/admin"
                onClick={() => setMenuOpen(false)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-amber-400 hover:bg-slate-800"
              >
                <span>⚙️</span>
                <span>Admin Dashboard</span>
              </Link>
            )}
            <button
              onClick={handleLogout}
              className="w-full text-left flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold text-rose-400 hover:bg-rose-500/10 mt-2"
            >
              <span>🚪</span>
              <span>Sign Out</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
