import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { Link } from 'react-router-dom'
import api from '../services/api'

function FarmSystem() {
  const { team } = useAuth()
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updatingStats, setUpdatingStats] = useState(false)
  const [statsUpdateMessage, setStatsUpdateMessage] = useState(null)

  useEffect(() => {
    loadTeams()
  }, [])

  const loadTeams = async () => {
    try {
      setLoading(true)
      const teamsData = await api.getTeams()
      setTeams(teamsData.results || teamsData)
      setError(null)
    } catch (error) {
      setError('Failed to load teams: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const updateAllStats = async () => {
    try {
      setUpdatingStats(true)
      setStatsUpdateMessage(null)
      
      const response = await api.updateAllProspectStats()
      setStatsUpdateMessage(`Stats update started! Updating ${response.total_prospects} prospects.`)
      
      // Clear the message after 5 seconds
      setTimeout(() => setStatsUpdateMessage(null), 5000)
      
    } catch (error) {
      setStatsUpdateMessage(`Error: ${error.message}`)
      setTimeout(() => setStatsUpdateMessage(null), 5000)
    } finally {
      setUpdatingStats(false)
    }
  }

  if (loading) {
    return (
      <div>
        <h2>Farm System Overview</h2>
        <p>Loading teams...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2>Farm System Overview</h2>
        <div style={{ color: 'red', padding: '10px', backgroundColor: '#fee', borderRadius: '5px' }}>
          {error}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2>Farm System Overview</h2>
          <p>View all teams and their prospects in the dynasty league.</p>
        </div>
        <button 
          onClick={updateAllStats}
          disabled={updatingStats}
          className="btn btn-primary"
          style={{ 
            padding: '10px 20px',
            fontSize: '0.9rem',
            backgroundColor: updatingStats ? '#ccc' : '#007bff',
            cursor: updatingStats ? 'not-allowed' : 'pointer'
          }}
        >
          {updatingStats ? 'Updating...' : 'Update All Stats'}
        </button>
      </div>
      
      {statsUpdateMessage && (
        <div style={{ 
          padding: '10px', 
          marginBottom: '20px',
          borderRadius: '5px',
          backgroundColor: statsUpdateMessage.includes('Error') ? '#fee' : '#e8f5e8',
          color: statsUpdateMessage.includes('Error') ? '#c62828' : '#2e7d32',
          border: `1px solid ${statsUpdateMessage.includes('Error') ? '#f44336' : '#4caf50'}`
        }}>
          {statsUpdateMessage}
        </div>
      )}
      
      <div className="grid">
        {teams.map(team => (
          <Link 
            key={team.id} 
            to={`/teams/${team.id}`} 
            className="team-card-link"
          >
            <div className="team-farm" style={{ cursor: 'pointer' }}>
              <h3>{team.name}</h3>
              <div className="pom-display">
                <h3>POM Balance</h3>
                <div className="pom-amount">{team.pom_balance}</div>
              </div>
              
              <h4>Prospects ({team.prospects?.length || 0})</h4>
              {!team.prospects || team.prospects.length === 0 ? (
                <p style={{ color: '#666', fontStyle: 'italic' }}>No prospects yet</p>
              ) : (
                <div className="prospect-list">
                  {team.prospects.map(prospect => (
                    <div key={prospect.id} style={{ 
                      padding: '6px 12px', 
                      margin: '1px 0', 
                      backgroundColor: '#f8f9fa', 
                      borderRadius: '2px',
                      fontSize: '0.9rem',
                      borderLeft: `3px solid ${prospect.is_eligible ? '#28a745' : '#dc3545'}`
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <strong>{prospect.name}</strong> - {prospect.position}
                        </div>
                        <div style={{ 
                          fontSize: '0.8rem',
                          color: prospect.is_eligible ? '#28a745' : '#dc3545',
                          fontWeight: 'bold'
                        }}>
                          {prospect.is_eligible ? '✓' : '✗'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <div style={{ 
                marginTop: '15px', 
                paddingTop: '15px', 
                borderTop: '1px solid #eee',
                textAlign: 'center'
              }}>
                <span style={{ 
                  color: '#2a5298', 
                  fontSize: '0.9rem',
                  fontWeight: 'bold'
                }}>
                  Click to view all prospects →
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default FarmSystem 