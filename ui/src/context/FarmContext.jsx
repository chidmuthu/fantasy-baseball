import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'

const FarmContext = createContext()

const initialState = {
  teams: [
    { id: '1', name: 'Team Alpha', pom: 100, prospects: [] },
    { id: '2', name: 'Team Beta', pom: 100, prospects: [] },
    { id: '3', name: 'Team Gamma', pom: 100, prospects: [] },
    { id: '4', name: 'Team Delta', pom: 100, prospects: [] },
  ],
  activeBids: [],
  completedBids: [],
  selectedTeam: '1'
}

function farmReducer(state, action) {
  switch (action.type) {
    case 'ADD_TEAM':
      return {
        ...state,
        teams: [...state.teams, { 
          id: uuidv4(), 
          name: action.payload.name, 
          pom: 100, 
          prospects: [] 
        }]
      }
    
    case 'UPDATE_TEAM_POM':
      return {
        ...state,
        teams: state.teams.map(team => 
          team.id === action.payload.teamId 
            ? { ...team, pom: action.payload.pom }
            : team
        )
      }
    
    case 'ADD_PROSPECT_TO_TEAM':
      return {
        ...state,
        teams: state.teams.map(team => 
          team.id === action.payload.teamId 
            ? { ...team, prospects: [...team.prospects, action.payload.prospect] }
            : team
        )
      }
    
    case 'REMOVE_PROSPECT_FROM_TEAM':
      return {
        ...state,
        teams: state.teams.map(team => 
          team.id === action.payload.teamId 
            ? { 
                ...team, 
                prospects: team.prospects.filter(p => p.id !== action.payload.prospectId) 
              }
            : team
        )
      }
    
    case 'CREATE_BID':
      return {
        ...state,
        activeBids: [...state.activeBids, {
          id: uuidv4(),
          prospect: action.payload.prospect,
          startingBid: action.payload.startingBid,
          currentBid: action.payload.startingBid,
          currentBidder: action.payload.nominatorId,
          nominatorId: action.payload.nominatorId,
          createdAt: new Date().toISOString(),
          lastBidTime: new Date().toISOString(),
          status: 'active'
        }]
      }
    
    case 'PLACE_BID':
      return {
        ...state,
        activeBids: state.activeBids.map(bid => 
          bid.id === action.payload.bidId 
            ? { 
                ...bid, 
                currentBid: action.payload.amount,
                currentBidder: action.payload.bidderId,
                lastBidTime: new Date().toISOString()
              }
            : bid
        )
      }
    
    case 'COMPLETE_BID':
      const completedBid = state.activeBids.find(bid => bid.id === action.payload.bidId)
      const winningTeam = state.teams.find(team => team.id === completedBid.currentBidder)
      
      return {
        ...state,
        activeBids: state.activeBids.filter(bid => bid.id !== action.payload.bidId),
        completedBids: [...state.completedBids, { ...completedBid, status: 'completed' }],
        teams: state.teams.map(team => 
          team.id === completedBid.currentBidder 
            ? { 
                ...team, 
                pom: team.pom - completedBid.currentBid,
                prospects: [...team.prospects, completedBid.prospect]
              }
            : team
        )
      }
    
    case 'SET_SELECTED_TEAM':
      return {
        ...state,
        selectedTeam: action.payload.teamId
      }
    
    default:
      return state
  }
}

export function FarmProvider({ children }) {
  const [state, dispatch] = useReducer(farmReducer, initialState)



  // Load data from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem('farmSystemState')
    if (savedState) {
      const parsedState = JSON.parse(savedState)
      // We'll implement a more sophisticated state restoration if needed
    }
  }, [])

  // Save state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('farmSystemState', JSON.stringify(state))
  }, [state])

  const value = {
    state,
    dispatch,
    actions: {
      addTeam: (name) => dispatch({ type: 'ADD_TEAM', payload: { name } }),
      updateTeamPOM: (teamId, pom) => dispatch({ type: 'UPDATE_TEAM_POM', payload: { teamId, pom } }),
      addProspectToTeam: (teamId, prospect) => dispatch({ type: 'ADD_PROSPECT_TO_TEAM', payload: { teamId, prospect } }),
      removeProspectFromTeam: (teamId, prospectId) => dispatch({ type: 'REMOVE_PROSPECT_FROM_TEAM', payload: { teamId, prospectId } }),
      createBid: (prospect, startingBid, nominatorId) => dispatch({ type: 'CREATE_BID', payload: { prospect, startingBid, nominatorId } }),
      placeBid: (bidId, amount, bidderId) => dispatch({ type: 'PLACE_BID', payload: { bidId, amount, bidderId } }),
      setSelectedTeam: (teamId) => dispatch({ type: 'SET_SELECTED_TEAM', payload: { teamId } })
    }
  }

  return (
    <FarmContext.Provider value={value}>
      {children}
    </FarmContext.Provider>
  )
}

export function useFarm() {
  const context = useContext(FarmContext)
  if (!context) {
    throw new Error('useFarm must be used within a FarmProvider')
  }
  return context
} 