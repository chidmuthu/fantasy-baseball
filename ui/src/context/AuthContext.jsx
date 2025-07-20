import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [team, setTeam] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Check if user is logged in on app start
    useEffect(() => {
        checkAuth()
    }, [])

    const checkAuth = async () => {
        const token = localStorage.getItem('authToken')
        if (token) {
            try {
                const teamData = await api.getMyTeam()
                setTeam(teamData)
                setUser({ username: teamData.owner.username })
                setError(null)
            } catch (error) {
                console.error('Auth check failed:', error)
                api.clearToken()
                setUser(null)
                setTeam(null)
            }
        }
        setLoading(false)
    }

    const login = async (username, password) => {
        try {
            setLoading(true)
            setError(null)
            
            const response = await api.login(username, password)
            const teamData = await api.getMyTeam()
            
            setUser({ username })
            setTeam(teamData)
            
            return { success: true }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const register = async (userData) => {
        try {
            setLoading(true)
            setError(null)
            
            await api.register(userData)
            const response = await api.login(userData.username, userData.password)
            const teamData = await api.getMyTeam()
            
            setUser({ username: userData.username })
            setTeam(teamData)
            
            return { success: true }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const logout = () => {
        api.clearToken()
        setUser(null)
        setTeam(null)
        setError(null)
    }

    const updateTeam = async (data) => {
        try {
            const updatedTeam = await api.updateTeam(team.id, data)
            setTeam(updatedTeam)
            return { success: true }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        }
    }

    const refreshTeam = async () => {
        try {
            const teamData = await api.getMyTeam()
            setTeam(teamData)
            return { success: true }
        } catch (error) {
            console.error('Failed to refresh team data:', error)
            return { success: false, error: error.message }
        }
    }

    const value = {
        user,
        team,
        loading,
        error,
        login,
        register,
        logout,
        updateTeam,
        refreshTeam,
        isAuthenticated: !!user,
    }

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
} 