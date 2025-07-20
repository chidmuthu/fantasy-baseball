import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

function TeamDetail() {
  const { teamId } = useParams()
  const { team: userTeam } = useAuth()
  const [team, setTeam] = useState(null)
  const [prospects, setProspects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadTeamData()
  }, [teamId])

  const loadTeamData = async () => {
    try {
      setLoading(true)
      
      // Get all teams to find the specific team
      const teamsData = await api.getTeams()
      const teams = teamsData.results || teamsData
      const foundTeam = teams.find(t => t.id === parseInt(teamId))
      
      if (!foundTeam) {
        setError('Team not found')
        return
      }
      
      setTeam(foundTeam)
      
      // Use the prospects that come with the team data
      // This ensures we get all prospects for this team regardless of permissions
      if (foundTeam.prospects && Array.isArray(foundTeam.prospects)) {
        setProspects(foundTeam.prospects)
      } else {
        // Fallback: try to get prospects separately
        try {
          const prospectsData = await api.getProspects()
          const allProspects = prospectsData.results || prospectsData
          const teamProspects = allProspects.filter(p => p.team === parseInt(teamId))
          setProspects(teamProspects)
        } catch (prospectError) {
          console.warn('Could not load prospects separately:', prospectError)
          setProspects([])
        }
      }
      
      setError(null)
    } catch (error) {
      setError('Failed to load team data: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div>
        <h2>Team Details</h2>
        <p>Loading team information...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2>Team Details</h2>
        <div style={{ color: 'red', padding: '10px', backgroundColor: '#fee', borderRadius: '5px' }}>
          {error}
        </div>
        <Link to="/teams" className="btn btn-primary" style={{ marginTop: '10px' }}>
          Back to Teams
        </Link>
      </div>
    )
  }

  if (!team) {
    return (
      <div>
        <h2>Team Details</h2>
        <p>Team not found.</p>
        <Link to="/teams" className="btn btn-primary" style={{ marginTop: '10px' }}>
          Back to Teams
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>{team.name}</h2>
          <Link to="/teams" className="btn btn-secondary">
            Back to Teams
          </Link>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          <div className="pom-display">
            <h3>Prospects</h3>
            <div className="pom-amount">{prospects.length}</div>
          </div>
          <div className="pom-display">
            <h3>POM Balance</h3>
            <div className="pom-amount">{team.pom_balance}</div>
          </div>
        </div>

        {userTeam && userTeam.id === team.id && (
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#e3f2fd', 
            borderRadius: '5px', 
            marginBottom: '20px',
            border: '1px solid #2196f3'
          }}>
            <h3>Your Team</h3>
            <p>This is your team. You can manage your prospects from the Farm System tab.</p>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Prospects ({prospects.length})</h3>
        
        {prospects.length === 0 ? (
          <p>No prospects on this team.</p>
        ) : (
          <div className="grid">
            {prospects.map(prospect => (
              <div key={prospect.id} className="card">
                <h4>{prospect.name}</h4>
                
                <div className="prospect-info">
                  <p><span>Position:</span> {prospect.position}</p>
                  <p><span>Organization:</span> {prospect.organization}</p>
                  <p><span>Level:</span> {prospect.level}</p>
                  <p><span>ETA:</span> {prospect.eta}</p>
                  <p><span>Age:</span> {prospect.age}</p>
                </div>

                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  marginTop: '15px',
                  paddingTop: '15px',
                  borderTop: '1px solid #eee'
                }}>
                  <span style={{ fontSize: '0.8rem', color: '#666' }}>
                    Added: {new Date(prospect.acquired_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default TeamDetail 