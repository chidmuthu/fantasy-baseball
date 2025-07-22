import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { formatDistanceToNow } from 'date-fns'

function Bidding() {
  const { team, refreshTeam } = useAuth()
  const navigate = useNavigate()
  const [activeBids, setActiveBids] = useState([])
  const [completedBids, setCompletedBids] = useState([])
  const [currentTab, setCurrentTab] = useState('active')
  const [showNominateModal, setShowNominateModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [bidError, setBidError] = useState(null)
  const [nominationForm, setNominationForm] = useState({
    name: '',
    position: '',
    organization: '',
    dateOfBirth: '',
    level: 'A',
    eta: new Date().getFullYear() + 2,
    startingBid: 5
  })

  useEffect(() => {
    loadBids()
    
    // Set up WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws/bidding/')
    
    ws.onopen = () => {
      console.log('WebSocket connected for bidding')
    }
    
    ws.onmessage = (event) => {
      console.log('WebSocket message received:', event.data)
      const data = JSON.parse(event.data)
      
      // Handle different types of WebSocket messages
      if (data.type === 'bid_placed' || data.type === 'bid_completed' || data.type === 'new_bid') {
        console.log('Refreshing bids due to:', data.type)
        // Refresh bids when any bid activity occurs
        loadBids()
        refreshTeam()
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }
    
    // Cleanup WebSocket on component unmount
    return () => {
      ws.close()
    }
  }, [refreshTeam])

  const loadBids = async () => {
    try {
      setLoading(true)
      const [activeBidsData, completedBidsData] = await Promise.all([
        api.getActiveBids(),
        api.getCompletedBids()
      ])
      setActiveBids(activeBidsData.results || activeBidsData)
      setCompletedBids(completedBidsData.results || completedBidsData)
      setError(null)
    } catch (error) {
      setError('Failed to load bids: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleNominate = async (e) => {
    e.preventDefault()
    try {
      setBidError(null) // Clear any previous errors
      const prospectData = {
        name: nominationForm.name,
        position: nominationForm.position,
        organization: nominationForm.organization,
        date_of_birth: nominationForm.dateOfBirth,
        level: nominationForm.level,
        eta: parseInt(nominationForm.eta)
      }
      
      console.log('Creating bid with data:', { prospectData, startingBid: nominationForm.startingBid })
      await api.createBid(prospectData, nominationForm.startingBid)
      setShowNominateModal(false)
      setNominationForm({
        name: '',
        position: '',
        organization: '',
        dateOfBirth: '',
        level: 'A',
        eta: new Date().getFullYear() + 2,
        startingBid: 5
      })
      
      // Refresh both bids and team data
      await Promise.all([
        loadBids(),
        refreshTeam()
      ])
    } catch (error) {
      console.error('Nomination error:', error)
      setBidError(error.message)
      // Keep the error visible for 30 seconds
      setTimeout(() => setBidError(null), 30000)
    }
  }

  const handleBid = async (bidId, amount) => {
    try {
      console.log(`Frontend: Attempting to place bid ${amount} POM`)
      await api.placeBid(bidId, amount)
      
      // Refresh both bids and team data
      await Promise.all([
        loadBids(),
        refreshTeam()
      ])
      
      console.log(`Bid placed successfully: ${amount} POM`)
    } catch (error) {
      console.error('Bid error:', error)
      setBidError(error.message)
      // Keep the error visible for 10 seconds
      setTimeout(() => setBidError(null), 10000)
    }
  }

  const getTimeRemaining = (expiresAt) => {
    if (!expiresAt) return 'No expiration set'
    
    const now = new Date()
    const expires = new Date(expiresAt)
    const diff = expires - now
    
    if (diff <= 0) return 'Expired'
    
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    
    if (hours > 0) {
      return `${hours}h ${minutes}m remaining`
    } else {
      return `${minutes}m remaining`
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h2>Loading...</h2>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2>Bidding</h2>
        <div style={{ color: 'red', padding: '10px', backgroundColor: '#fee', borderRadius: '5px' }}>
          {error}
        </div>
      </div>
    )
  }

  return (
    <div style={{ marginTop: bidError ? '60px' : '0' }}>
      <div className="card">
        <h2>Bidding</h2>
        <p>Bid on prospects and nominate new ones for your farm system.</p>
        
        {/* Tab Navigation */}
        <div className="tab-navigation" style={{
          display: 'flex',
          borderBottom: '2px solid #e1e5e9',
          marginBottom: '20px'
        }}>
          <button
            className={`tab-button ${currentTab === 'active' ? 'active' : ''}`}
            onClick={() => setCurrentTab('active')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: currentTab === 'active' ? '#2a5298' : 'transparent',
              color: currentTab === 'active' ? 'white' : '#666',
              cursor: 'pointer',
              borderBottom: currentTab === 'active' ? '2px solid #2a5298' : '2px solid transparent',
              fontWeight: currentTab === 'active' ? '600' : '400',
              transition: 'all 0.2s ease'
            }}
          >
            Active Bids ({activeBids.length})
          </button>
          <button
            className={`tab-button ${currentTab === 'completed' ? 'active' : ''}`}
            onClick={() => setCurrentTab('completed')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: currentTab === 'completed' ? '#2a5298' : 'transparent',
              color: currentTab === 'completed' ? 'white' : '#666',
              cursor: 'pointer',
              borderBottom: currentTab === 'completed' ? '2px solid #2a5298' : '2px solid transparent',
              fontWeight: currentTab === 'completed' ? '600' : '400',
              transition: 'all 0.2s ease'
            }}
          >
            Completed Bids ({completedBids.length})
          </button>
        </div>
        
        {bidError && (
          <div style={{ 
            position: 'fixed',
            top: '0',
            left: '0',
            right: '0',
            zIndex: 9999,
            color: 'white', 
            padding: '15px', 
            backgroundColor: '#dc3545', 
            borderBottom: '2px solid #c82333',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
          }}>
            <div style={{ flex: 1 }}>
              <strong>Bid Error:</strong> {bidError}
            </div>
            <button 
              onClick={() => setBidError(null)}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '1.2rem',
                cursor: 'pointer',
                padding: '0 10px'
              }}
            >
              ×
            </button>
          </div>
        )}
        
        {team && (
          <div className="pom-display">
            <h3>Your POM Balance</h3>
            <div className="pom-amount">{team.pom_balance}</div>
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          {currentTab === 'active' && (
            <button 
              className="btn btn-success"
              onClick={() => setShowNominateModal(true)}
              disabled={!team || team.pom_balance < 5}
            >
              Nominate New Prospect
            </button>
          )}
        </div>
      </div>

      {/* Active Bids Tab */}
      {currentTab === 'active' && (
        <div className="grid">
          {activeBids.map(bid => {
            const currentBidder = bid.current_bidder
            const canBid = team && team.pom_balance > bid.current_bid && team.id !== currentBidder?.id
            
            return (
              <div key={bid.id} className="prospect-card">
                <h3 
                  className="clickable-prospect-name" 
                  onClick={() => navigate(`/bidding/prospect/${bid.prospect.id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  {bid.prospect.name}
                </h3>
                <div className="prospect-info">
                  <p><span>Position:</span> {bid.prospect.position}</p>
                  <p><span>Organization:</span> {bid.prospect.organization}</p>
                  <p><span>Level:</span> {bid.prospect.level}</p>
                  <p><span>ETA:</span> {bid.prospect.eta}</p>
                  <p><span>Age:</span> {bid.prospect.age}</p>
                  
                  {/* Eligibility Information */}
                  <div style={{ 
                    marginTop: '8px', 
                    padding: '6px', 
                    backgroundColor: bid.prospect.is_eligible ? '#e8f5e8' : '#ffe8e8',
                    borderRadius: '4px',
                    border: `1px solid ${bid.prospect.is_eligible ? '#4caf50' : '#f44336'}`
                  }}>
                    <p style={{ 
                      margin: '0', 
                      fontWeight: 'bold',
                      fontSize: '0.9rem',
                      color: bid.prospect.is_eligible ? '#2e7d32' : '#c62828'
                    }}>
                      {bid.prospect.eligibility_status}
                    </p>
                    {bid.prospect.position === 'P' ? (
                      <p style={{ margin: '5px 0 0 0', fontSize: '0.8rem' }}>
                        {bid.prospect.innings_pitched} IP / {bid.prospect.eligibility_threshold_ip} IP threshold
                      </p>
                    ) : (
                      <p style={{ margin: '5px 0 0 0', fontSize: '0.8rem' }}>
                        {bid.prospect.at_bats} AB / {bid.prospect.eligibility_threshold_ab} AB threshold
                      </p>
                    )}
                  </div>
                </div>

                <div className="bid-section">
                  <p><strong>Current Bid:</strong> {bid.current_bid} POM</p>
                  <p><strong>Current Leader:</strong> {currentBidder?.name}</p>
                  <p><strong>Started:</strong> {formatDistanceToNow(new Date(bid.created_at), { addSuffix: true })}</p>
                  <div className="timer">
                    <strong>Time Remaining:</strong> {getTimeRemaining(bid.expires_at)}
                  </div>
                  
                  {canBid && (
                    <div className="bid-input">
                      <input
                        type="number"
                        min={bid.current_bid + 1}
                        placeholder={`Min bid: ${bid.current_bid + 1}`}
                        id={`bid-${bid.id}`}
                        onClick={(e) => e.stopPropagation()} // Prevent navigation to bid history
                      />
                      <button 
                        className="btn"
                        onClick={(e) => {
                          e.stopPropagation() // Prevent navigation to bid history
                          const input = document.getElementById(`bid-${bid.id}`)
                          const amount = parseInt(input.value)
                          if (amount > bid.current_bid) {
                            console.log(`Frontend: Attempting to place bid ${amount} POM`)
                            handleBid(bid.id, amount)
                            input.value = ''
                          } else {
                            console.log(`Frontend: Bid amount ${amount} must be higher than current bid ${bid.current_bid}`)
                            setBidError(`Bid must be higher than current bid of ${bid.current_bid} POM`)
                            setTimeout(() => setBidError(null), 5000)
                          }
                        }}
                      >
                        Place Bid
                      </button>
                    </div>
                  )}
                  
                  {!canBid && team?.id === currentBidder?.id && (
                    <p style={{ color: '#28a745', fontWeight: 'bold' }}>
                      You are currently winning this bid!
                    </p>
                  )}
                  
                  {!canBid && team?.id !== currentBidder?.id && (
                    <p style={{ color: '#dc3545' }}>
                      {team?.pom_balance <= bid.current_bid 
                        ? 'Insufficient POM to bid' 
                        : 'You cannot outbid yourself'}
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {currentTab === 'active' && activeBids.length === 0 && (
        <div className="card">
          <h3>No Active Bids</h3>
          <p>Be the first to nominate a prospect for bidding!</p>
        </div>
      )}

      {/* Completed Bids Tab */}
      {currentTab === 'completed' && (
        <div className="grid">
          {completedBids.map(bid => {
            const currentBidder = bid.current_bidder
            const isWinner = team?.id === currentBidder?.id
            
            return (
              <div key={bid.id} className="prospect-card" style={{
                backgroundColor: bid.status === 'completed' ? '#e8f5e8' : '#f8f9fa',
                borderLeft: bid.status === 'completed' ? '4px solid #28a745' : '4px solid #6c757d'
              }}>
                <h3 
                  className="clickable-prospect-name" 
                  onClick={() => navigate(`/bidding/prospect/${bid.prospect.id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  {bid.prospect.name}
                </h3>
                <div className="prospect-info">
                  <p><span>Position:</span> {bid.prospect.position}</p>
                  <p><span>Organization:</span> {bid.prospect.organization}</p>
                  <p><span>Level:</span> {bid.prospect.level}</p>
                  <p><span>ETA:</span> {bid.prospect.eta}</p>
                  <p><span>Age:</span> {bid.prospect.age}</p>
                  
                  {/* Status Information */}
                  <div style={{ 
                    marginTop: '8px', 
                    padding: '6px', 
                    backgroundColor: bid.status === 'completed' ? '#e8f5e8' : '#f8f9fa',
                    borderRadius: '4px',
                    border: `1px solid ${bid.status === 'completed' ? '#28a745' : '#6c757d'}`
                  }}>
                    <p style={{ 
                      margin: '0', 
                      fontWeight: 'bold',
                      fontSize: '0.9rem',
                      color: bid.status === 'completed' ? '#2e7d32' : '#6c757d'
                    }}>
                      {bid.status === 'completed' ? 'COMPLETED' : 'CANCELLED'}
                    </p>
                  </div>
                </div>

                <div className="bid-section">
                  <p><strong>Final Bid:</strong> {bid.current_bid} POM</p>
                  <p><strong>Winner:</strong> {currentBidder?.name}</p>
                  <p><strong>Nominated by:</strong> {bid.nominator?.name}</p>
                  <p><strong>Started:</strong> {formatDistanceToNow(new Date(bid.created_at), { addSuffix: true })}</p>
                  {bid.completed_at && (
                    <p><strong>Completed:</strong> {formatDistanceToNow(new Date(bid.completed_at), { addSuffix: true })}</p>
                  )}
                  
                  {isWinner && (
                    <p style={{ color: '#28a745', fontWeight: 'bold', marginTop: '10px' }}>
                      🏆 You won this prospect!
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {currentTab === 'completed' && completedBids.length === 0 && (
        <div className="card">
          <h3>No Completed Bids</h3>
          <p>No bids have been completed yet.</p>
        </div>
      )}

      {/* Nomination Modal */}
      {showNominateModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Nominate New Prospect</h3>
              <button 
                className="modal-close"
                onClick={() => setShowNominateModal(false)}
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleNominate}>
              <div className="form-group">
                <label htmlFor="name">Prospect Name:</label>
                <input
                  id="name"
                  type="text"
                  className="form-control"
                  value={nominationForm.name}
                  onChange={(e) => setNominationForm({...nominationForm, name: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="position">Position:</label>
                <select
                  id="position"
                  className="form-control"
                  value={nominationForm.position}
                  onChange={(e) => setNominationForm({...nominationForm, position: e.target.value})}
                  required
                >
                  <option value="">Select Position</option>
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
                <label htmlFor="organization">Organization:</label>
                <input
                  id="organization"
                  type="text"
                  className="form-control"
                  value={nominationForm.organization}
                  onChange={(e) => setNominationForm({...nominationForm, organization: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="dateOfBirth">Date of Birth:</label>
                <input
                  id="dateOfBirth"
                  type="date"
                  className="form-control"
                  value={nominationForm.dateOfBirth}
                  onChange={(e) => setNominationForm({...nominationForm, dateOfBirth: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="level">Level:</label>
                <select
                  id="level"
                  className="form-control"
                  value={nominationForm.level}
                  onChange={(e) => setNominationForm({...nominationForm, level: e.target.value})}
                  required
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
                <label htmlFor="eta">ETA (Expected Year of MLB Arrival):</label>
                <input
                  id="eta"
                  type="number"
                  className="form-control"
                  value={nominationForm.eta}
                  onChange={(e) => setNominationForm({...nominationForm, eta: e.target.value})}
                  min={new Date().getFullYear()}
                  max={new Date().getFullYear() + 10}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="startingBid">Starting Bid (POM):</label>
                <input
                  id="startingBid"
                  type="number"
                  className="form-control"
                  value={nominationForm.startingBid}
                  onChange={(e) => setNominationForm({...nominationForm, startingBid: parseInt(e.target.value)})}
                  min="5"
                  max={team?.pom_balance || 100}
                  required
                />
              </div>
              
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setShowNominateModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-success"
                  disabled={!team || team.pom_balance < nominationForm.startingBid}
                >
                  Nominate Prospect
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Bidding 