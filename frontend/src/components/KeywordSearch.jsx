/**
 * KeywordSearch component - Search tweets by keyword
 */
import React, { useState } from 'react';
import TweetCard from './TweetCard';
import { searchKeywords } from '../services/api';
import './KeywordSearch.css';

const KeywordSearch = () => {
    const [keyword, setKeyword] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchHistory, setSearchHistory] = useState([]);

    const handleSearch = async (e) => {
        e.preventDefault();

        if (!keyword.trim()) {
            return;
        }

        try {
            setLoading(true);
            setError(null);

            const data = await searchKeywords(keyword.trim(), 20);
            setResults(data);

            // Add to search history
            if (!searchHistory.includes(keyword.trim())) {
                setSearchHistory([keyword.trim(), ...searchHistory.slice(0, 4)]);
            }
        } catch (err) {
            setError('Failed to search tweets. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleHistoryClick = (historyKeyword) => {
        setKeyword(historyKeyword);
    };

    return (
        <div className="keyword-search">
            <div className="search-header">
                <h2>Global Search</h2>
                <p className="search-description">Search for tweets containing specific keywords</p>
            </div>

            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="Enter keyword to search..."
                    className="search-input"
                    disabled={loading}
                />
                <button
                    type="submit"
                    className="search-button"
                    disabled={loading || !keyword.trim()}
                >
                    {loading ? '...' : 'Search'}
                </button>
            </form>

            {searchHistory.length > 0 && (
                <div className="search-history">
                    <span className="history-label">Recent:</span>
                    <div className="history-tags">
                        {searchHistory.map((item, index) => (
                            <button
                                key={index}
                                onClick={() => handleHistoryClick(item)}
                                className="history-tag"
                                disabled={loading}
                            >
                                {item}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {loading ? (
                <div className="search-loading">
                    <div className="spinner"></div>
                    <p>Searching Twitter for "{keyword}"...</p>
                </div>
            ) : error ? (
                <div className="search-error">
                    <p>⚠️ {error}</p>
                </div>
            ) : results.length > 0 ? (
                <div className="search-results">
                    <div className="results-header">
                        <span className="results-count">{results.length} results found</span>
                    </div>
                    <div className="results-list">
                        {results.map((tweet, index) => (
                            <TweetCard key={index} tweet={tweet} />
                        ))}
                    </div>
                </div>
            ) : keyword && !loading ? (
                <div className="search-empty">
                    <p>No results found for "{keyword}"</p>
                    <p className="empty-hint">Try a different keyword</p>
                </div>
            ) : (
                <div className="search-placeholder">
                    <p>🔎 Enter a keyword above to search tweets</p>
                </div>
            )}
        </div>
    );
};

export default KeywordSearch;
