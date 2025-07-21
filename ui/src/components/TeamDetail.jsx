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
  const [editingProspect, setEditingProspect] = useState(null)
  const [editForm, setEditForm] = useState({})

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

  const startEditing = (prospect) => {
    setEditingProspect(prospect.id)
    setEditForm({
      position: prospect.position,
      organization: prospect.organization,
      level: prospect.level,
      eta: prospect.eta
    })
  }

  const cancelEditing = () => {
    setEditingProspect(null)
    setEditForm({})
  }

  const saveProspect = async (prospectId) => {
    try {
      // Only send the fields that are actually editable
      const updateData = {
        position: editForm.position,
        organization: editForm.organization,
        level: editForm.level,
        eta: editForm.eta
      }
      
      await api.updateProspect(prospectId, updateData)
      
      // Update the prospects list with the edited prospect, preserving original data
      setProspects(prospects.map(p => 
        p.id === prospectId 
          ? { ...p, ...updateData }
          : p
      ))
      
      setEditingProspect(null)
      setEditForm({})
    } catch (error) {
      alert('Failed to update prospect: ' + error.message)
    }
  }

  const handleEditChange = (field, value) => {
    setEditForm(prev => ({ ...prev, [field]: value }))
  }

  const tagProspect = async (prospectId) => {
    try {
      const response = await api.tagProspect(prospectId)
      
      // Update the prospects list with the tagged prospect
      setProspects(prospects.map(p => 
        p.id === prospectId 
          ? response.prospect
          : p
      ))
      
      // Show success message
      alert(response.message)
    } catch (error) {
      alert('Failed to tag prospect: ' + error.message)
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
        <Link to="/" className="btn btn-primary" style={{ marginTop: '10px' }}>
          Back to Farm System
        </Link>
      </div>
    )
  }

  if (!team) {
    return (
      <div>
        <h2>Team Details</h2>
        <p>Team not found.</p>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '10px' }}>
          Back to Farm System
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>{team.name}</h2>
          <Link to="/" className="btn btn-secondary">
            Back to Farm System
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
                {editingProspect === prospect.id ? (
                  // Edit mode
                  <div>
                    <div className="form-group">
                      <label>Name:</label>
                      <input
                        type="text"
                        className="form-control"
                        value={prospect.name}
                        disabled
                        style={{ backgroundColor: '#f8f9fa', color: '#666' }}
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Position:</label>
                      <select
                        className="form-control"
                        value={editForm.position}
                        onChange={(e) => handleEditChange('position', e.target.value)}
                      >
                        <option value="P">Pitcher</option>
                        <option value="C">Catcher</option>
                        <option value="1B">First Base</option>
                        <option value="2B">Second Base</option>
                        <option value="3B">Third Base</option>
                        <option value="SS">Shortstop</option>
                        <option value="OF">Outfield</option>
                        <option value="UTIL">Utility</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>Organization:</label>
                      <input
                        type="text"
                        className="form-control"
                        value={editForm.organization}
                        onChange={(e) => handleEditChange('organization', e.target.value)}
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Level:</label>
                      <select
                        className="form-control"
                        value={editForm.level}
                        onChange={(e) => handleEditChange('level', e.target.value)}
                      >
                        <option value="ROK">Rookie</option>
                        <option value="A">A</option>
                        <option value="A+">A+</option>
                        <option value="AA">AA</option>
                        <option value="AAA">AAA</option>
                        <option value="MLB">MLB</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>ETA:</label>
                      <input
                        type="number"
                        className="form-control"
                        value={editForm.eta}
                        onChange={(e) => handleEditChange('eta', parseInt(e.target.value))}
                        min={new Date().getFullYear()}
                        max={new Date().getFullYear() + 10}
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>At Bats:</label>
                      <input
                        type="number"
                        className="form-control"
                        value={editForm.at_bats}
                        onChange={(e) => handleEditChange('at_bats', parseInt(e.target.value) || 0)}
                        min={0}
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Innings Pitched:</label>
                      <input
                        type="number"
                        className="form-control"
                        value={editForm.innings_pitched}
                        onChange={(e) => handleEditChange('innings_pitched', parseFloat(e.target.value) || 0)}
                        min={0}
                        step={0.1}
                      />
                    </div>
                    
                    <div style={{ 
                      display: 'flex', 
                      gap: '10px', 
                      marginTop: '15px',
                      justifyContent: 'flex-end'
                    }}>
                      <button 
                        className="btn btn-secondary"
                        onClick={cancelEditing}
                      >
                        Cancel
                      </button>
                      <button 
                        className="btn btn-success"
                        onClick={() => saveProspect(prospect.id)}
                      >
                        Save
                      </button>
                    </div>
                  </div>
                ) : (
                  // View mode
                  <div>
                    <h4>{prospect.name}</h4>
                    
                    <div className="prospect-info">
                      <p><span>Position:</span> {prospect.position}</p>
                      <p><span>Organization:</span> {prospect.organization}</p>
                      <p><span>Level:</span> {prospect.level}</p>
                      <p><span>ETA:</span> {prospect.eta}</p>
                      <p><span>Age:</span> {prospect.age}</p>
                      
                      {/* Eligibility Information */}
                      <div style={{ 
                        marginTop: '10px', 
                        padding: '8px', 
                        backgroundColor: prospect.is_eligible ? '#e8f5e8' : '#ffe8e8',
                        borderRadius: '4px',
                        border: `1px solid ${prospect.is_eligible ? '#4caf50' : '#f44336'}`
                      }}>
                        <p style={{ 
                          margin: '0', 
                          fontWeight: 'bold',
                          color: prospect.is_eligible ? '#2e7d32' : '#c62828'
                        }}>
                          {prospect.eligibility_status}
                        </p>
                        {prospect.position === 'P' ? (
                          <p style={{ margin: '2px 0 0 0', fontSize: '0.9rem' }}>
                            IP: {prospect.innings_pitched} / {prospect.eligibility_threshold_ip}
                          </p>
                        ) : (
                          <p style={{ margin: '2px 0 0 0', fontSize: '0.9rem' }}>
                            AB: {prospect.at_bats} / {prospect.eligibility_threshold_ab}
                          </p>
                        )}                    
                          <p style={{ margin: '2px 0 0 0', fontSize: '0.9rem', fontStyle: 'italic' }}>
                            Tags applied: {prospect.tags_applied}
                          </p>
                      </div>
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
                        Added: {new Date(prospect.created_at).toLocaleDateString()}
                      </span>
                      {userTeam && userTeam.id === team.id && (
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button 
                            className="btn btn-secondary"
                            style={{ fontSize: '0.8rem', padding: '5px 10px' }}
                            onClick={() => startEditing(prospect)}
                          >
                            Edit
                          </button>
                          <button 
                            className="btn btn-warning"
                            style={{ fontSize: '0.8rem', padding: '5px 10px' }}
                            onClick={() => {
                              if (window.confirm(`Tag this prospect to extend eligibility? This will cost ${prospect.next_tag_cost} POM.`)) {
                                tagProspect(prospect.id)
                              }
                            }}
                          >
                            Tag ({prospect.next_tag_cost} POM)
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default TeamDetail 