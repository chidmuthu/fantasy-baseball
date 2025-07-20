import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import FarmSystem from './components/FarmSystem'
import Bidding from './components/Bidding'
import Teams from './components/Teams'
import TeamDetail from './components/TeamDetail'
import Login from './components/Login'
import { AuthProvider, useAuth } from './context/AuthContext'

function Navigation() {
  const location = useLocation()
  const { user, logout } = useAuth()
  
  return (
    <nav className="nav">
      <Link 
        to="/" 
        className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
      >
        Farm System
      </Link>
      <Link 
        to="/bidding" 
        className={`nav-link ${location.pathname === '/bidding' ? 'active' : ''}`}
      >
        Bidding
      </Link>
      <Link 
        to="/teams" 
        className={`nav-link ${location.pathname === '/teams' ? 'active' : ''}`}
      >
        Teams
      </Link>
      {user && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ color: 'white', fontSize: '0.9rem' }}>
            Welcome, {user.username}!
          </span>
          <button 
            onClick={logout}
            className="btn btn-secondary"
            style={{ padding: '5px 10px', fontSize: '0.8rem' }}
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  )
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <h2>Loading...</h2>
        </div>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

function AppContent() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="App">
      <header className="header">
        <h1>⚾ Dynasty Baseball Farm System</h1>
        {isAuthenticated && <Navigation />}
      </header>
      
      <div className="container">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <FarmSystem />
            </ProtectedRoute>
          } />
          <Route path="/bidding" element={
            <ProtectedRoute>
              <Bidding />
            </ProtectedRoute>
          } />
          <Route path="/teams" element={
            <ProtectedRoute>
              <Teams />
            </ProtectedRoute>
          } />
          <Route path="/teams/:teamId" element={
            <ProtectedRoute>
              <TeamDetail />
            </ProtectedRoute>
          } />
        </Routes>
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  )
}

export default App 