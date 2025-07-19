import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

function Teams() {
  const { team } = useAuth()
  const [teams, setTeams] = useState([])
  const [showAddTeamModal, setShowAddTeamModal] = useState(false)
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
        <h2>League Teams</h2>
        <p>Loading teams...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2>League Teams</h2>
        <div style={{ color: 'red', padding: '10px', backgroundColor: '#fee', borderRadius: '5px' }}>
          {error}
        </div>
      </div>
    )
  }

  const totalProspects = teams.reduce((sum, team) => sum + (team.prospects?.length || 0), 0)
  const totalPOM = teams.reduce((sum, team) => sum + team.pom_balance, 0)

  return (
    <div>
      <div className="card">
        <h2>League Teams</h2>
        <p>Manage teams and their POM balances.</p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '20px' }}>
          <div className="pom-display">
            <h3>Total Teams</h3>
            <div className="pom-amount">{teams.length}</div>
          </div>
          <div className="pom-display">
            <h3>Total Prospects</h3>
            <div className="pom-amount">{totalProspects}</div>
          </div>
          <div className="pom-display">
            <h3>Total POM</h3>
            <div className="pom-amount">{totalPOM}</div>
          </div>
        </div>

        {team && (
          <div style={{ marginBottom: '20px' }}>
            <h3>Your Team: {team.name}</h3>
            <p>POM Balance: {team.pom_balance}</p>
            <p>Prospects: {team.prospects?.length || 0}</p>
          </div>
        )}
      </div>

      <div className="grid">
        {teams.map(team => (
          <div key={team.id} className="card">
            <h3>{team.name}</h3>
            
            <div className="prospect-info">
              <p><span>Team ID:</span> {team.id}</p>
              <p><span>Prospects:</span> {team.prospects?.length || 0}</p>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px' }}>
                <span><strong>POM Balance:</strong></span>
                <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#2a5298' }}>
                  {team.pom_balance}
                </span>
              </div>
            </div>

            {team.prospects && team.prospects.length > 0 && (
              <div style={{ marginTop: '15px' }}>
                <h4>Recent Prospects:</h4>
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {team.prospects.slice(-3).map(prospect => (
                    <div key={prospect.id} style={{ 
                      padding: '8px', 
                      margin: '5px 0', 
                      backgroundColor: '#f8f9fa', 
                      borderRadius: '4px',
                      fontSize: '0.9rem'
                    }}>
                      <strong>{prospect.name}</strong> - {prospect.position} ({prospect.organization})
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Teams 