/**
 * LiveFeed component - Displays monitored tweets in real-time
 */
import React, { useState, useEffect } from 'react';
import TweetCard from './TweetCard';
import { getRecentTweets, getMonitoredAccounts } from '../services/api';
import './LiveFeed.css';

const LiveFeed = () => {
    const [tweets, setTweets] = useState([]);
    const [accounts, setAccounts] = useState([]);
    const [selectedAccount, setSelectedAccount] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);

    const fetchAccounts = async () => {
        try {
            const data = await getMonitoredAccounts();
            setAccounts(data);
        } catch (err) {
            console.error('Failed to fetch accounts:', err);
        }
    };

    const fetchTweets = async () => {
        try {
            setLoading(true);
            const data = await getRecentTweets(24, selectedAccount || null);
            setTweets(data);
            setLastUpdate(new Date().toLocaleTimeString('en-US', {
                hour12: true,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }));
            setError(null);
        } catch (err) {
            setError('Failed to fetch tweets. Please check if the backend is running.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Fetch accounts once
        fetchAccounts();
    }, []);

    useEffect(() => {
        // Fetch tweets when account filter changes
        fetchTweets();

        // Poll every 30 seconds
        const interval = setInterval(fetchTweets, 30000);

        return () => clearInterval(interval);
    }, [selectedAccount]);

    return (
        <div className="live-feed">
            <div className="feed-header">
                <h2>Live Monitoring Feed</h2>
                <div className="feed-controls">
                    <select
                        className="account-filter"
                        value={selectedAccount}
                        onChange={(e) => {
                            setSelectedAccount(e.target.value);
                            e.target.blur(); // Collapse after selection
                        }}
                        onFocus={(e) => {
                            if (accounts.length > 5) {
                                e.target.size = 6;
                            }
                        }}
                        onBlur={(e) => {
                            e.target.size = 1;
                        }}
                    >
                        <option value="">All Accounts</option>
                        {accounts.map((account) => (
                            <option key={account.id} value={account.username}>
                                @{account.username}
                            </option>
                        ))}
                    </select>
                </div>
            </div>
            <div className="feed-info">
                <span className="tweet-count">{tweets.length} tweets</span>
                {lastUpdate && (
                    <span className="last-update">Updated: {lastUpdate}</span>
                )}
            </div>

            {loading && tweets.length === 0 ? (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading tweets...</p>
                </div>
            ) : error ? (
                <div className="error-state">
                    <p>⚠️ {error}</p>
                    <button onClick={fetchTweets} className="retry-button">
                        Retry
                    </button>
                </div>
            ) : tweets.length === 0 ? (
                <div className="empty-state">
                    <p>📭 No tweets found in the last 24 hours</p>
                    <p className="empty-hint">Tweets will appear here as they are posted</p>
                </div>
            ) : (
                <div className="tweets-list">
                    {tweets.map((tweet) => (
                        <TweetCard key={tweet.id} tweet={tweet} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default LiveFeed;
