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
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
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
        return await this.request(`/bids/${bidId}/place_bid/`, {
            method: 'POST',
            body: JSON.stringify({ amount }),
        });
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