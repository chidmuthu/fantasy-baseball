import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import { formatDistanceToNow } from 'date-fns'

function BidHistory() {
  const { prospectId } = useParams()
  const navigate = useNavigate()
  const { team } = useAuth()
  const [prospect, setProspect] = useState(null)
  const [bids, setBids] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [bidError, setBidError] = useState(null)
  const [bidAmount, setBidAmount] = useState('')
  const [placingBid, setPlacingBid] = useState(false)

  useEffect(() => {
    loadBidHistory()
    
    // Set up WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws/bidding/')
    
    ws.onopen = () => {
      console.log('WebSocket connected for bid history')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      // Handle different types of WebSocket messages
      if (data.type === 'bid_placed' && data.prospect_id === parseInt(prospectId)) {
        // Refresh bid history when a new bid is placed
        loadBidHistory()
      } else if (data.type === 'bid_completed' && data.prospect_id === parseInt(prospectId)) {
        // Refresh bid history when a bid is completed
        loadBidHistory()
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
  }, [prospectId])

  const loadBidHistory = async () => {
    try {
      setLoading(true)
      const response = await api.getProspectBidHistory(prospectId)
      setProspect(response.prospect)
      setBids(response.bids)
      setError(null)
    } catch (error) {
      setError('Failed to load bid history: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleBid = async (bidId, amount) => {
    try {
      setPlacingBid(true)
      setBidError(null)
      
      await api.placeBid(bidId, amount)
      
      // Refresh bid history after successful bid
      await loadBidHistory()
      
      // Clear bid amount
      setBidAmount('')
      
      console.log(`Bid placed successfully: ${amount} POM`)
    } catch (error) {
      console.error('Bid error:', error)
      setBidError(error.message)
      // Keep the error visible for 10 seconds
      setTimeout(() => setBidError(null), 10000)
    } finally {
      setPlacingBid(false)
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h2>Loading Bid History...</h2>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <h2>Error</h2>
        <p>{error}</p>
        <button className="btn" onClick={() => navigate('/bidding')}>
          Back to Bidding
        </button>
      </div>
    )
  }

  if (!prospect) {
    return (
      <div className="card">
        <h2>Prospect Not Found</h2>
        <button className="btn" onClick={() => navigate('/bidding')}>
          Back to Bidding
        </button>
      </div>
    )
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Bid History: {prospect.name}</h2>
          <button className="btn btn-secondary" onClick={() => navigate('/bidding')}>
            ← Back to Bidding
          </button>
        </div>
        
        {/* Prospect Summary */}
        <div className="prospect-summary" style={{
          backgroundColor: '#f8f9fa',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #dee2e6'
        }}>
          <h3>{prospect.name}</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
            <p><strong>Position:</strong> {prospect.position}</p>
            <p><strong>Organization:</strong> {prospect.organization}</p>
            <p><strong>Level:</strong> {prospect.level}</p>
            <p><strong>ETA:</strong> {prospect.eta}</p>
            <p><strong>Age:</strong> {prospect.age}</p>
            <p><strong>Status:</strong> 
              <span style={{
                color: prospect.is_eligible ? '#28a745' : '#dc3545',
                fontWeight: 'bold',
                marginLeft: '5px'
              }}>
                {prospect.eligibility_status}
              </span>
            </p>
          </div>
        </div>

        {/* Bid Input Section - Only show for active bids */}
        {bids.some(bid => bid.status === 'active') && (
          <div style={{
            backgroundColor: '#e8f5e8',
            padding: '15px',
            borderRadius: '8px',
            marginBottom: '20px',
            border: '1px solid #28a745'
          }}>
            <h3 style={{ margin: '0 0 15px 0', color: '#28a745' }}>Place a Bid</h3>
            
            {bidError && (
              <div style={{
                backgroundColor: '#f8d7da',
                color: '#721c24',
                padding: '10px',
                borderRadius: '4px',
                marginBottom: '15px',
                border: '1px solid #f5c6cb'
              }}>
                <strong>Bid Error:</strong> {bidError}
              </div>
            )}
            
            {bids.filter(bid => bid.status === 'active').map(activeBid => {
              const currentBidder = activeBid.current_bidder
              const canBid = team && team.pom_balance > activeBid.current_bid && team.id !== currentBidder?.id
              
              return (
                <div key={activeBid.id} style={{ marginBottom: '15px' }}>
                  <div style={{ marginBottom: '10px' }}>
                    <p style={{ margin: '0 0 5px 0' }}>
                      <strong>Current Bid:</strong> {activeBid.current_bid} POM
                    </p>
                    <p style={{ margin: '0 0 5px 0' }}>
                      <strong>Current Leader:</strong> {currentBidder?.name}
                    </p>
                    {canBid ? (
                      <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: '10px' }}>
                        <input
                          type="number"
                          min={activeBid.current_bid + 1}
                          placeholder={`Min bid: ${activeBid.current_bid + 1}`}
                          value={bidAmount}
                          onChange={(e) => setBidAmount(e.target.value)}
                          style={{
                            flex: 1,
                            padding: '8px 12px',
                            border: '2px solid #e1e5e9',
                            borderRadius: '6px',
                            fontSize: '1rem'
                          }}
                        />
                        <button 
                          className="btn"
                          onClick={() => {
                            const amount = parseInt(bidAmount)
                            if (amount > activeBid.current_bid) {
                              handleBid(activeBid.id, amount)
                            } else {
                              setBidError(`Bid must be higher than current bid of ${activeBid.current_bid} POM`)
                              setTimeout(() => setBidError(null), 5000)
                            }
                          }}
                          disabled={placingBid || !bidAmount || parseInt(bidAmount) <= activeBid.current_bid}
                        >
                          {placingBid ? 'Placing Bid...' : 'Place Bid'}
                        </button>
                      </div>
                    ) : (
                      <p style={{ 
                        margin: '10px 0 0 0', 
                        color: '#6c757d', 
                        fontStyle: 'italic' 
                      }}>
                        {team?.id === currentBidder?.id 
                          ? "You are currently winning this bid"
                          : "You cannot bid on this prospect"
                        }
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Bid History */}
        <div>
          <h3>Bid History</h3>
          {bids.length === 0 ? (
            <p>No bids found for this prospect.</p>
          ) : (
            <div className="bid-history">
              {bids.map(bid => (
                <div key={bid.id} className="bid-card" style={{
                  border: '1px solid #dee2e6',
                  borderRadius: '8px',
                  padding: '15px',
                  marginBottom: '15px',
                  backgroundColor: bid.status === 'active' ? '#fff3cd' : '#f8f9fa'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                    <div>
                      <h4 style={{ margin: '0 0 5px 0' }}>
                        {bid.current_bid} POM
                        {bid.status === 'active' && (
                          <span style={{
                            backgroundColor: '#28a745',
                            color: 'white',
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            marginLeft: '10px'
                          }}>
                            ACTIVE
                          </span>
                        )}
                        {bid.status === 'completed' && (
                          <span style={{
                            backgroundColor: '#007bff',
                            color: 'white',
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            marginLeft: '10px'
                          }}>
                            COMPLETED
                          </span>
                        )}
                        {bid.status === 'cancelled' && (
                          <span style={{
                            backgroundColor: '#6c757d',
                            color: 'white',
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            marginLeft: '10px'
                          }}>
                            CANCELLED
                          </span>
                        )}
                      </h4>
                      {bid.status === 'completed' ? (
                        <p style={{ margin: '0', color: '#6c757d' }}>
                          <strong>Winner:</strong> {bid.current_bidder?.name}
                        </p>
                      ) : (
                        <p style={{ margin: '0', color: '#6c757d' }}>
                          <strong>Current Leader:</strong> {bid.current_bidder?.name}
                        </p>
                      )}
                      <p style={{ margin: '0', color: '#6c757d' }}>
                        <strong>Nominated by:</strong> {bid.nominator?.name}
                      </p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ margin: '0', fontSize: '0.9rem', color: '#6c757d' }}>
                        Started: {formatDistanceToNow(new Date(bid.created_at), { addSuffix: true })}
                      </p>
                      {bid.last_bid_time && (
                        <p style={{ margin: '0', fontSize: '0.9rem', color: '#6c757d' }}>
                          Last bid: {formatDistanceToNow(new Date(bid.last_bid_time), { addSuffix: true })}
                        </p>
                      )}
                      {bid.completed_at && (
                        <p style={{ margin: '0', fontSize: '0.9rem', color: '#6c757d' }}>
                          Completed: {formatDistanceToNow(new Date(bid.completed_at), { addSuffix: true })}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Bid History Timeline */}
                  {bid.history && bid.history.length > 0 && (
                    <div style={{ marginTop: '15px' }}>
                      <h5 style={{ margin: '0 0 10px 0', color: '#495057' }}>Bid Timeline:</h5>
                      <div style={{ 
                        borderLeft: '3px solid #007bff', 
                        paddingLeft: '15px',
                        marginLeft: '10px'
                      }}>
                        {bid.history.map((historyItem, index) => (
                          <div key={index} style={{
                            marginBottom: '10px',
                            padding: '8px',
                            backgroundColor: 'white',
                            borderRadius: '4px',
                            border: '1px solid #e9ecef'
                          }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div>
                                <strong>{historyItem.team?.name}</strong> bid <strong>{historyItem.amount} POM</strong>
                              </div>
                              <span style={{ fontSize: '0.8rem', color: '#6c757d' }}>
                                {formatDistanceToNow(new Date(historyItem.bid_time), { addSuffix: true })}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default BidHistory 