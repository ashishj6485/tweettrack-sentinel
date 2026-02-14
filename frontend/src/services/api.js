/**
 * API service for communicating with backend
 */
import axios from 'axios';

// Use environment variable for production, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Get recent tweets from the last N hours
 */
export const getRecentTweets = async (hours = 24, account = null) => {
    try {
        const params = new URLSearchParams({ hours: hours.toString() });
        if (account) {
            params.append('account', account);
        }
        const response = await api.get(`/api/tweets/recent?${params}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching recent tweets:', error);
        throw error;
    }
};

/**
 * Get tweets from a specific account
 */
export const getTweetsByAccount = async (username, hours = 24) => {
    try {
        const response = await api.get(`/api/tweets/by-account/${username}?hours=${hours}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching tweets for @${username}:`, error);
        throw error;
    }
};

/**
 * Search for tweets by keyword
 */
export const searchKeywords = async (keyword, count = 20) => {
    try {
        const response = await api.post('/api/search/keywords', { keyword, count });
        return response.data;
    } catch (error) {
        console.error(`Error searching for keyword "${keyword}":`, error);
        throw error;
    }
};

/**
 * Get list of monitored accounts
 */
export const getMonitoredAccounts = async (activeOnly = true) => {
    try {
        const response = await api.get(`/api/accounts?active_only=${activeOnly}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching monitored accounts:', error);
        throw error;
    }
};

/**
 * Add a new monitored account
 */
export const addMonitoredAccount = async (username, displayName = null) => {
    try {
        const response = await api.post('/api/accounts', {
            username,
            display_name: displayName
        });
        return response.data;
    } catch (error) {
        console.error(`Error adding account @${username}:`, error);
        throw error;
    }
};

/**
 * Remove a monitored account
 */
export const removeMonitoredAccount = async (username) => {
    try {
        const response = await api.delete(`/api/accounts/${username}`);
        return response.data;
    } catch (error) {
        console.error(`Error removing account @${username}:`, error);
        throw error;
    }
};

/**
 * Health check
 */
export const healthCheck = async () => {
    try {
        const response = await api.get('/api/health');
        return response.data;
    } catch (error) {
        console.error('Error checking API health:', error);
        throw error;
    }
};

export default api;
