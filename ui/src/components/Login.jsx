import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'

function Login() {
    const { login, register, loading, error, isAuthenticated, team } = useAuth()
    const [isRegistering, setIsRegistering] = useState(false)
    const [loginSuccess, setLoginSuccess] = useState(false)
    const [loginError, setLoginError] = useState(null)
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        password_confirm: '',
        email: '',
        team_name: ''
    })

    // Redirect to team page if already authenticated
    if (isAuthenticated && team) {
        return <Navigate to={`/teams/${team.id}`} replace />
    }

    // Show success message briefly before redirect
    if (loginSuccess) {
        return (
            <div className="container">
                <div className="card">
                    <h2>Login Successful!</h2>
                    <p>Redirecting to your team page...</p>
                </div>
            </div>
        )
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        
        // Clear any previous errors
        setLoginError(null)
        
        if (isRegistering) {
            if (formData.password !== formData.password_confirm) {
                setLoginError('Passwords do not match')
                // Keep the error visible for 30 seconds
                setTimeout(() => setLoginError(null), 30000)
                return
            }
            
            const result = await register({
                username: formData.username,
                password: formData.password,
                password_confirm: formData.password_confirm,
                email: formData.email,
                team_name: formData.team_name
            })
            
            if (result.success) {
                // Registration successful, user is now logged in
                setLoginSuccess(true)
                // The redirect will happen automatically due to the isAuthenticated check above
                return
            } else {
                // Registration failed
                setLoginError(result.error || 'Registration failed')
                // Keep the error visible for 30 seconds
                setTimeout(() => setLoginError(null), 30000)
            }
        } else {
            const result = await login(formData.username, formData.password)
            if (result.success) {
                // Login successful
                setLoginSuccess(true)
                // The redirect will happen automatically due to the isAuthenticated check above
                return
            } else {
                // Login failed
                setLoginError(result.error || 'Login failed')
                // Keep the error visible for 30 seconds
                setTimeout(() => setLoginError(null), 30000)
            }
        }
    }

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    if (loading) {
        return (
            <div className="container">
                <div className="card">
                    <h2>Loading...</h2>
                    <p>Please wait while we check your authentication status.</p>
                </div>
            </div>
        )
    }

    return (
        <div className="container" style={{ marginTop: loginError ? '60px' : '0' }}>
            {loginError && (
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
                        <strong>Authentication Error:</strong> {loginError}
                    </div>
                    <button 
                        onClick={() => setLoginError(null)}
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
            
            <div className="card">
                <h2>{isRegistering ? 'Register New Team' : 'Login to Your Team'}</h2>
                
                {error && (
                    <div style={{ 
                        backgroundColor: '#fee', 
                        color: '#c33', 
                        padding: '10px', 
                        borderRadius: '5px', 
                        marginBottom: '20px' 
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Username:</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            className="form-control"
                            value={formData.username}
                            onChange={handleInputChange}
                            required
                        />
                    </div>

                    {isRegistering && (
                        <>
                            <div className="form-group">
                                <label htmlFor="email">Email:</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    className="form-control"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="team_name">Team Name:</label>
                                <input
                                    type="text"
                                    id="team_name"
                                    name="team_name"
                                    className="form-control"
                                    value={formData.team_name}
                                    onChange={handleInputChange}
                                    required
                                />
                            </div>
                        </>
                    )}

                    <div className="form-group">
                        <label htmlFor="password">Password:</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            className="form-control"
                            value={formData.password}
                            onChange={handleInputChange}
                            required
                        />
                    </div>

                    {isRegistering && (
                        <div className="form-group">
                            <label htmlFor="password_confirm">Confirm Password:</label>
                            <input
                                type="password"
                                id="password_confirm"
                                name="password_confirm"
                                className="form-control"
                                value={formData.password_confirm}
                                onChange={handleInputChange}
                                required
                            />
                        </div>
                    )}

                    <button 
                        type="submit" 
                        className="btn btn-success"
                        disabled={loading}
                    >
                        {loading ? 'Loading...' : (isRegistering ? 'Register' : 'Login')}
                    </button>
                </form>

                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                    <button 
                        className="btn btn-secondary"
                        onClick={() => setIsRegistering(!isRegistering)}
                    >
                        {isRegistering ? 'Already have an account? Login' : 'Need an account? Register'}
                    </button>
                </div>
            </div>
        </div>
    )
}

export default Login 