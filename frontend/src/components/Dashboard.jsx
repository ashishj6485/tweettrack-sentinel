/**
 * Dashboard component - Main layout with live feed and keyword search
 */
import React from 'react';
import LiveFeed from './LiveFeed';
import KeywordSearch from './KeywordSearch';
import './Dashboard.css';

const Dashboard = () => {
    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <div className="header-content">
                    <h1 className="app-title">
                        TweetTrack Sentinel
                    </h1>
                    <p className="app-subtitle">Real-time Twitter Monitoring & AI Analysis</p>
                </div>
                <div className="header-status">
                    <div className="status-indicator"></div>
                    <span className="status-text">Live Monitoring Active</span>
                </div>
            </header>

            <div className="dashboard-content">
                <div className="dashboard-left">
                    <LiveFeed />
                </div>
                <div className="dashboard-right">
                    <KeywordSearch />
                </div>
            </div>

            <footer className="dashboard-footer">
                <p>© 2026 TweetTrack Sentinel | Ashish Jaiswal</p>
            </footer>
        </div>
    );
};

export default Dashboard;
