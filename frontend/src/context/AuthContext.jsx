import React, { createContext, useContext, useState, useCallback } from 'react'
import api from '../api/axios'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('sg_user')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(false)

  const persist = (token, userData) => {
    localStorage.setItem('sg_token', token)
    localStorage.setItem('sg_user', JSON.stringify(userData))
    setUser(userData)
  }

  const login = useCallback(async (email, password) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { email, password })
      persist(data.access_token, data.user)
      return data.user
    } finally {
      setLoading(false)
    }
  }, [])

  const register = useCallback(async (full_name, email, password) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/register', { full_name, email, password })
      persist(data.access_token, data.user)
      return data.user
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('sg_token')
    localStorage.removeItem('sg_user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAdmin: user?.role === 'admin' }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
