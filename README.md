# 🐦 TweetTrack Sentinel

**Real-time Twitter Monitoring & AI Analysis System**

TweetTrack Sentinel is a full-stack application that monitors 5-20 Twitter accounts in real-time, detects newly posted tweets, generates AI summaries using Google Gemini, and provides a beautiful React dashboard for visualization and keyword search.

## ✨ Features

### Phase 1 (Current Implementation)
- ✅ **Real-time Monitoring**: Continuous polling of configured Twitter accounts (every 5 minutes)
- ✅ **Unofficial Twitter API**: Uses twikit for scraping without API keys
- ✅ **AI Summarization**: Automatic tweet summarization using Google Gemini API
- ✅ **24-Hour History**: Maintains rolling 24-hour tweet database
- ✅ **Live Dashboard**: React-based UI with auto-refreshing feed
- ✅ **Keyword Search**: Search Twitter for specific keywords with instant results
- ✅ **IST Timestamps**: All times displayed in Indian Standard Time with relative timestamps
- ✅ **Modern UI**: Glassmorphic design with gradient backgrounds

### Phase 2 (Planned)
- ⏳ WhatsApp Alerts via Twilio
- ⏳ Web Push Notifications
- ⏳ WebSocket real-time updates
- ⏳ Account management interface
- ⏳ Advanced filtering options

### Phase 3 (Planned)
- ⏳ Proxy rotation & anti-blocking
- ⏳ Production deployment guide
- ⏳ PostgreSQL migration
- ⏳ Monitoring & logging

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  ┌──────────────┐              ┌──────────────┐         │
│  │  Live Feed   │              │Keyword Search│         │
│  │ (Auto-refresh│              │ (Real-time)  │         │
│  └──────────────┘              └──────────────┘         │
└────────────────────┬────────────────────────────────────┘
                     │ REST API + WebSocket
┌────────────────────┴────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Polling  │  │  Scraper │  │    AI    │              │
│  │ Service  │─▶│ (twikit) │─▶│Summarizer│              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                      │              │                    │
└──────────────────────┼──────────────┼───────────────────┘
                       │              │
              ┌────────┴────┐  ┌──────┴─────┐
              │   Twitter   │  │Gemini API  │
              │ (Unofficial)│  │            │
              └─────────────┘  └────────────┘
                       │
                  ┌────┴────┐
                  │SQLite DB│
                  │(24h data│
                  └─────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Twitter account (for scraping)
- Google Gemini API key

### Backend Setup

1. **Clone and navigate:**
```bash
cd "d:\Twitter Scraper"
```

2. **Create virtual environment:**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
```

Edit `.env` file:
```env
# Twitter Authentication
TWITTER_USERNAME=your_twitter_username
TWITTER_EMAIL=your_twitter_email  
TWITTER_PASSWORD=your_twitter_password

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Monitored Accounts (comma-separated)
MONITORED_ACCOUNTS=elonmusk,BillGates,SundarPichai,satyanadella,narendramodi

# Polling (5 minutes = 300 seconds)
POLL_INTERVAL_SECONDS=300
```

5. **Run backend:**
```bash
python main.py
```

Backend will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies (if not already done):**
```bash
npm install
```

3. **Run development server:**
```bash
npm run dev
```

Frontend will start on `http://localhost:5173`

## 📖 Usage

1. **Start the backend** (see above) - this initializes the database and starts polling
2. **Start the frontend** - opens the dashboard in your browser
3. **Monitor live feed** - Left panel shows tweets from monitored accounts (last 24 hours)
4. **Search keywords** - Right panel lets you search Twitter for any keyword
5. **View AI summaries** - Every tweet includes a concise AI-generated summary

## 🔧 Configuration

### Monitored Accounts
Edit `MONITORED_ACCOUNTS` in `.env`:
```env
MONITORED_ACCOUNTS=username1,username2,username3
```

### Polling Interval
Adjust `POLL_INTERVAL_SECONDS` in `.env` (default: 300 = 5 minutes):
```env
POLL_INTERVAL_SECONDS=180  # 3 minutes
```

### Database
Default: SQLite (`tweettrack.db`)  
For production: PostgreSQL/Supabase (see [Cloud Deployment Guide](CLOUD_DEPLOYMENT.md))

## ☁️ Cloud Deployment

Deploy to production for **$0/month** using:
- **Frontend**: Vercel (Free tier)
- **Backend**: Render (Free tier)
- **Database**: Supabase (Free tier)

**📖 See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) for complete step-by-step guide**

Quick summary:
1. Create Supabase database (5 min)
2. Push code to GitHub (3 min)
3. Deploy backend to Render (10 min)
4. Deploy frontend to Vercel (5 min)
5. Verify everything works (2 min)

**Total time: ~30 minutes**

## 📁 Project Structure

```
d:\Twitter Scraper\
├── src/
│   ├── ai/
│   │   └── summarizer.py          # Gemini AI integration
│   ├── api/
│   │   └── main.py                # FastAPI endpoints
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── db.py                  # Database connection
│   │   └── operations.py          # CRUD operations
│   ├── scraper/
│   │   ├── twitter_scraper.py     # Twikit scraper
│   │   └── polling_service.py     # Background polling
│   └── utils/
│       ├── config.py              # Settings management
│       └── timezone.py            # IST conversion
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Dashboard.jsx      # Main layout
│       │   ├── LiveFeed.jsx       # Live tweet feed
│       │   ├── KeywordSearch.jsx  # Search interface
│       │   └── TweetCard.jsx      # Tweet display
│       └── services/
│           └── api.js             # Backend API client
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
└── .env                          # Configuration (create from .env.example)
```

## 🎨 UI Features

- **Glassmorphic Design**: Modern frosted glass effects
- **Gradient Backgrounds**: Beautiful purple/blue gradients
- **Auto-refresh**: Live feed updates every 30 seconds
- **Relative Timestamps**: "5 minutes ago" style timestamps
- **Search History**: Recent keyword searches saved
- **Responsive Layout**: Works on desktop and tablet
- **Loading States**: Clean loading and error handling

## 🔑 Getting API Keys

### Twitter Account
Use any Twitter account. Create a dedicated account for scraping to avoid issues with your personal account.

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key or use existing
4. Copy key to `.env` file

## 🐛 Troubleshooting

### Backend won't start
- Check `.env` file exists and has correct credentials
- Verify Python version: `python --version` (needs 3.10+)
- Check if port 8000 is available

### Frontend can't connect  
- Ensure backend is running on `http://localhost:8000`
- Check console for CORS errors
- Verify API endpoints in `frontend/src/services/api.js`

### Twitter authentication fails
- Verify credentials in `.env` are correct
- Twitter may require verification - check your email
- Consider using a fresh Twitter account

### No tweets appearing
- Check backend logs for scraping errors
- Verify monitored accounts exist and have recent tweets
- Check polling interval - may need to wait 5 minutes

## 📊 API Endpoints

### Tweets
- `GET /api/tweets/recent?hours=24` - Get recent tweets
- `GET /api/tweets/by-account/{username}?hours=24` - Account tweets

### Search
- `POST /api/search/keywords` - Search by keyword
  ```json
  {
    "keyword": "AI",
    "count": 20
  }
  ```

### Accounts
- `GET /api/accounts` - List monitored accounts
- `POST /api/accounts` - Add monitored account
- `DELETE /api/accounts/{username}` - Remove account

### Health
- `GET /api/health` - API health check

## 🚧 Roadmap

### Phase 2 (Next)
- [ ] WhatsApp alerts via Twilio
- [ ] WebSocket real-time updates
- [ ] Web push notifications
- [ ] Account management UI
- [ ] Filtering by account/date

### Phase 3 (Future)
- [ ] Proxy rotation
- [ ] Anti-blocking strategies
- [ ] PostgreSQL migration
- [ ] Docker deployment
- [ ] Production monitoring
- [ ] Cost tracking

## 📝 License

This project is for educational purposes. Respect Twitter's Terms of Service and rate limits.

## 🤝 Contributing

This is a personal project. Feel free to fork and customize for your needs.

---

**Built with ❤️ using React, FastAPI, twikit, and Google Gemini**
