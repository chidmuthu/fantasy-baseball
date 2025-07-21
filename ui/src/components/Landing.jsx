import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function Landing() {
  const { team, loading } = useAuth()

  // Show loading while team data is being fetched
  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <h2>Loading your team...</h2>
          <p>Please wait while we load your team information.</p>
        </div>
      </div>
    )
  }

  // Redirect to user's team page
  if (team) {
    return <Navigate to={`/teams/${team.id}`} replace />
  }

  // Fallback - shouldn't happen if user is authenticated
  return (
    <div className="container">
      <div className="card">
        <h2>Welcome to Dynasty Baseball Farm System</h2>
        <p>Redirecting to your team...</p>
      </div>
    </div>
  )
}

export default Landing 