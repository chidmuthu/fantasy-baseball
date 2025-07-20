import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { Link } from 'react-router-dom'
import api from '../services/api'

function FarmSystem() {
  const { team } = useAuth()
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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
      <h2>Farm System Overview</h2>
      <p>View all teams and their prospects in the dynasty league.</p>
      
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
                  {team.prospects.slice(0, 3).map(prospect => (
                    <div key={prospect.id} className="prospect-item">
                      <h4>{prospect.name}</h4>
                      <p><span>Position:</span> {prospect.position}</p>
                      <p><span>Organization:</span> {prospect.organization}</p>
                      <p><span>Level:</span> {prospect.level}</p>
                      <p><span>ETA:</span> {prospect.eta}</p>
                      <p><span>Age:</span> {prospect.age}</p>
                    </div>
                  ))}
                  {team.prospects.length > 3 && (
                    <p style={{ color: '#666', fontStyle: 'italic', textAlign: 'center' }}>
                      +{team.prospects.length - 3} more prospects
                    </p>
                  )}
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