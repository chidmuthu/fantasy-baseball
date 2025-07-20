const API_BASE_URL = 'http://localhost:8000/api';

class ApiService {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('authToken');
    }

    // Set auth token
    setToken(token) {
        this.token = token;
        localStorage.setItem('authToken', token);
    }

    // Clear auth token
    clearToken() {
        this.token = null;
        localStorage.removeItem('authToken');
    }

    // Get auth headers
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                // Token expired or invalid
                this.clearToken();
                window.location.href = '/login';
                return;
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.log('Error response data:', errorData);
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                
                // Handle different error response formats
                let errorMessage = '';
                
                // First, try to get non-field errors (general validation errors)
                if (errorData.non_field_errors && errorData.non_field_errors.length > 0) {
                    errorMessage = errorData.non_field_errors[0];
                } else if (errorData.error) {
                    errorMessage = errorData.error;
                } else if (errorData.detail) {
                    errorMessage = errorData.detail;
                } else if (typeof errorData === 'string') {
                    errorMessage = errorData;
                } else {
                    // Try to extract error from field-specific errors (Django REST Framework serializer errors)
                    const errorKeys = Object.keys(errorData);
                    if (errorKeys.length > 0) {
                        // Look for common field names that might contain the main error
                        const priorityFields = ['amount', 'starting_bid', 'prospect_data'];
                        let foundError = false;
                        
                        for (const field of priorityFields) {
                            if (errorData[field]) {
                                const fieldError = errorData[field];
                                if (Array.isArray(fieldError)) {
                                    errorMessage = fieldError[0];
                                    foundError = true;
                                    break;
                                } else if (typeof fieldError === 'string') {
                                    errorMessage = fieldError;
                                    foundError = true;
                                    break;
                                }
                            }
                        }
                        
                        // If no priority field found, use the first available error
                        if (!foundError) {
                            const firstKey = errorKeys[0];
                            const firstError = errorData[firstKey];
                            if (Array.isArray(firstError)) {
                                errorMessage = firstError[0];
                            } else if (typeof firstError === 'string') {
                                errorMessage = firstError;
                            } else if (typeof firstError === 'object') {
                                // Handle nested error objects
                                const nestedKeys = Object.keys(firstError);
                                if (nestedKeys.length > 0) {
                                    const nestedError = firstError[nestedKeys[0]];
                                    if (Array.isArray(nestedError)) {
                                        errorMessage = nestedError[0];
                                    } else if (typeof nestedError === 'string') {
                                        errorMessage = nestedError;
                                    }
                                }
                            }
                        }
                    }
                }
                
                if (!errorMessage) {
                    errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                }
                
                throw new Error(errorMessage);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Authentication
    async login(username, password) {
        const response = await this.request('/token/', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        
        this.setToken(response.access);
        return response;
    }

    async register(userData) {
        const response = await this.request('/register/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
        return response;
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await this.request('/token/refresh/', {
            method: 'POST',
            body: JSON.stringify({ refresh: refreshToken }),
        });
        
        this.setToken(response.access);
        return response;
    }

    // Teams
    async getMyTeam() {
        return await this.request('/teams/my_team/');
    }

    async getTeams() {
        return await this.request('/teams/');
    }

    async updateTeam(teamId, data) {
        return await this.request(`/teams/${teamId}/`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async adjustPOM(teamId, amount) {
        return await this.request(`/teams/${teamId}/adjust_pom/`, {
            method: 'POST',
            body: JSON.stringify({ amount }),
        });
    }

    // Prospects
    async getProspects() {
        return await this.request('/prospects/');
    }

    async getMyProspects() {
        return await this.request('/prospects/my_prospects/');
    }

    async getAvailableProspects() {
        return await this.request('/prospects/available/');
    }

    async createProspect(prospectData) {
        return await this.request('/prospects/', {
            method: 'POST',
            body: JSON.stringify(prospectData),
        });
    }

    async updateProspect(prospectId, data) {
        return await this.request(`/prospects/${prospectId}/`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async releaseProspect(prospectId) {
        return await this.request(`/prospects/${prospectId}/release/`, {
            method: 'POST',
        });
    }

    // Bidding
    async getBids() {
        return await this.request('/bids/');
    }

    async getActiveBids() {
        return await this.request('/bids/active/');
    }

    async getMyBids() {
        return await this.request('/bids/my_bids/');
    }

    async getMyWinningBids() {
        return await this.request('/bids/my_winning/');
    }

    async createBid(prospectData, startingBid) {
        return await this.request('/bids/', {
            method: 'POST',
            body: JSON.stringify({
                prospect_data: prospectData,
                starting_bid: startingBid,
            }),
        });
    }

    async placeBid(bidId, amount) {
        console.log(`API: Placing bid ${amount} POM on bid ${bidId}`)
        try {
            const result = await this.request(`/bids/${bidId}/place_bid/`, {
                method: 'POST',
                body: JSON.stringify({ amount }),
            });
            console.log('API: Bid placed successfully:', result)
            return result
        } catch (error) {
            console.error('API: Bid placement failed:', error)
            throw error
        }
    }

    async completeBid(bidId) {
        return await this.request(`/bids/${bidId}/complete/`, {
            method: 'POST',
        });
    }

    async cancelBid(bidId) {
        return await this.request(`/bids/${bidId}/cancel/`, {
            method: 'POST',
        });
    }

    async checkExpiredBids() {
        return await this.request('/bids/check_expired/', {
            method: 'POST',
        });
    }
}

export default new ApiService(); 