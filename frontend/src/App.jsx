import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import ForgotPassword from './pages/auth/ForgotPassword'
import ResetPassword from './pages/auth/ResetPassword'
import Profile from './pages/profile/Profile'
import Dashboard from './pages/dashboard/Dashboard'
import SchemeList from './pages/schemes/SchemeList'
import SchemeDetail from './pages/schemes/SchemeDetail'
import Compare from './pages/compare/Compare'
import Saved from './pages/saved/Saved'
import Chatbot from './pages/chatbot/Chatbot'
import AdminPanel from './pages/admin/AdminPanel'
import Family from './pages/family/Family'
import Applications from './pages/applications/Applications'
import IVRHelpline from './pages/ivr/IVRHelpline'

export default function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="p-4 md:p-8">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/family" element={<ProtectedRoute><Family /></ProtectedRoute>} />
          <Route path="/applications" element={<ProtectedRoute><Applications /></ProtectedRoute>} />
          <Route path="/schemes" element={<ProtectedRoute><SchemeList /></ProtectedRoute>} />
          <Route path="/schemes/:id" element={<ProtectedRoute><SchemeDetail /></ProtectedRoute>} />
          <Route path="/saved" element={<ProtectedRoute><Saved /></ProtectedRoute>} />
          <Route path="/compare" element={<ProtectedRoute><Compare /></ProtectedRoute>} />
          <Route path="/chatbot" element={<ProtectedRoute><Chatbot /></ProtectedRoute>} />
          <Route path="/ivr" element={<ProtectedRoute><IVRHelpline /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedRoute adminOnly><AdminPanel /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  )
}


