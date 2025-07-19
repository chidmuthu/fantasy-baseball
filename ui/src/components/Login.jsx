import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'

function Login() {
    const { login, register, loading, error } = useAuth()
    const [isRegistering, setIsRegistering] = useState(false)
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        password_confirm: '',
        email: '',
        team_name: ''
    })

    const handleSubmit = async (e) => {
        e.preventDefault()
        
        if (isRegistering) {
            if (formData.password !== formData.password_confirm) {
                alert('Passwords do not match')
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
                return
            }
        } else {
            const result = await login(formData.username, formData.password)
            if (result.success) {
                // Login successful
                return
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
                </div>
            </div>
        )
    }

    return (
        <div className="container">
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

                {!isRegistering && (
                    <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
                        <h4>Test Accounts</h4>
                        <p>For testing, you can use these pre-created accounts:</p>
                        <ul style={{ textAlign: 'left' }}>
                            <li><strong>Username:</strong> test_user_1, <strong>Password:</strong> testpass123</li>
                            <li><strong>Username:</strong> test_user_2, <strong>Password:</strong> testpass123</li>
                            <li><strong>Username:</strong> test_user_3, <strong>Password:</strong> testpass123</li>
                            <li><strong>Username:</strong> test_user_4, <strong>Password:</strong> testpass123</li>
                            <li><strong>Username:</strong> test_user_5, <strong>Password:</strong> testpass123</li>
                        </ul>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Login 