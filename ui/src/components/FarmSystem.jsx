import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
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
          <div key={team.id} className="team-farm">
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
                  <div key={prospect.id} className="prospect-item">
                    <h4>{prospect.name}</h4>
                    <p><span>Position:</span> {prospect.position}</p>
                    <p><span>Organization:</span> {prospect.organization}</p>
                    <p><span>Age:</span> {prospect.age}</p>
                    {prospect.notes && (
                      <p><span>Notes:</span> {prospect.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default FarmSystem 