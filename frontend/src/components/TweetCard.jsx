/**
 * TweetCard component - Displays a single tweet
 */
import React from 'react';
import './TweetCard.css';

const TweetCard = ({ tweet }) => {
    return (
        <div className="tweet-card">
            <div className="tweet-header">
                <div className="tweet-author">
                    <span className="username">@{tweet.account_username}</span>
                    <span className="timestamp">{tweet.posted_at_relative}</span>
                </div>
                <a
                    href={tweet.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="tweet-link-button"
                >
                    View Tweet →
                </a>
            </div>

            <div className="tweet-text">
                {tweet.text}
            </div>

            <div className="tweet-summary">
                <div className="summary-badge">AI INSIGHT</div>
                <div className="summary-text">{tweet.summary}</div>
            </div>

            <div className="tweet-footer">
                <span className="posted-time">Posted: {tweet.posted_at}</span>
            </div>
        </div>
    );
};

export default TweetCard;
