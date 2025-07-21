import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import FarmSystem from './components/FarmSystem'
import Bidding from './components/Bidding'
import TeamDetail from './components/TeamDetail'
import Landing from './components/Landing'
import Login from './components/Login'
import { AuthProvider, useAuth } from './context/AuthContext'

function Navigation() {
  const location = useLocation()
  const { user, team, logout } = useAuth()
  
  return (
    <nav className="nav">
      {user && team && (
        <Link 
          to={`/teams/${team.id}`}
          className={`nav-link ${location.pathname === `/teams/${team.id}` ? 'active' : ''}`}
        >
          My Team
        </Link>
      )}
      <Link 
        to="/farm-system" 
        className={`nav-link ${location.pathname === '/farm-system' ? 'active' : ''}`}
      >
        Farm System
      </Link>
      <Link 
        to="/bidding" 
        className={`nav-link ${location.pathname === '/bidding' ? 'active' : ''}`}
      >
        Bidding
      </Link>
      {user && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ color: 'white', fontSize: '0.9rem' }}>
            Welcome, {team.name}!
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
              <Landing />
            </ProtectedRoute>
          } />
          <Route path="/farm-system" element={
            <ProtectedRoute>
              <FarmSystem />
            </ProtectedRoute>
          } />
          <Route path="/bidding" element={
            <ProtectedRoute>
              <Bidding />
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