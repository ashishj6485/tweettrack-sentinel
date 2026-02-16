# 🐦 TweetTrack Sentinel

**TweetTrack Sentinel** is a professional-grade, live monitoring and analysis platform designed to track specific Twitter (X) profiles, analyze their content using state-of-the-art AI, and deliver real-time alerts via WhatsApp.

---

## 🏗️ Architecture & Design

The system follows a modern decoupled architecture designed for high availability and near-zero latency in AI processing.

### 🎨 Frontend (React + Vite)
- **Live Feed**: Real-time monitoring of targeted accounts with integrated AI insights.
- **Global Search**: Search keywords globally across Twitter with on-the-fly AI analysis and categorization.
- **24h Rolling Window**: Displays a continuous 24-hour archive of processed tweets, keeping the dashboard relevant and focused.
- **Tech Stack**: React 18, Vite, Vanilla CSS.

### ⚙️ Backend (FastAPI + Python)
- **Twikit Library**: Utilizes the advanced Twikit library for high-speed, browser-less tweet scraping and account interaction.
- **Asynchronous Task Queue**: Handles concurrent AI processing and WhatsApp delivery without blocking the main scraper.
- **Core Libraries**: FastAPI for the API layer, SQLAlchemy for ORM, and Pydantic for strict data validation.

### 🧠 AI Engine (Groq + Llama 3.1)
- **Lightning Fast**: Powered by Groq's LPUs, delivering AI summaries and political risk analysis in under 500ms.
- **Intelligent Summarization**: Automatically condenses long tweets into single, punchy sentences.
- **Political Risk Analysis**: Classifies tweets (ATTACK, GRIEVANCE, SUPPORT, NEUTRAL) and assigns urgency scores (1-5).

### 🗄️ Database & Infrastructure
- **Hybrid Storage**: Uses local Python-based SQLite for rapid prototyping and caching, alongside Supabase (PostgreSQL) for high-availability production storage.
- **Twilio**: Securely delivers real-time notifications to WhatsApp recipients.
- **Cloudflare Tunneling**: Integrated support for Cloudflare (ngrok-style) tunneling to allow secure communication between local scrapers and cloud-based APIs.

---

## 🚀 Key Features

- **Live Monitoring**: Track multiple high-profile accounts simultaneously.
- **AI Insights**: Instant summaries and deep political analysis for every post.
- **Real-Time Alerts**: High-urgency tweets are delivered directly to WhatsApp recipients.
- **Historical Analysis**: View and search through archives of monitored data.
- **Cloud-Native**: Fully prepared for deployment on modern cloud platforms.

---

## 🛠️ Setup & Installation

### 1. Backend Configuration
Navigate to the `backend` directory and create a `.env` file with the following:
```env
# Twitter Credentials
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email

# AI & Database
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql://user:pass@host:5432/postgres

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+91xxxx,whatsapp:+91yyyy

# Polling
POLL_INTERVAL_SECONDS=600
MONITORED_ACCOUNTS=Username1,Username2
```

### 2. Local Run
**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## ☁️ Cloud Deployment

- **Backend (Render)**: Host the FastAPI server. Use `RUN_MODE=api` for a decoupled API-only instance.
- **Frontend (Vercel)**: Host the React dashboard with environment variables pointing to the Render API.
- **Tunneling (Cloudflare)**: Use Cloudflare tunnels to bridge local scraping agents with cloud-hosted services for maximum resilience against IP blocking.

---

## 📊 Monitoring & Maintenance
- **Logs**: Backend activity is logged to standard output for easy debugging.
- **Database**: Manage monitored accounts and view raw data via the Supabase dashboard.
- **AI Quota**: Groq provides a generous free tier for high-volume analysis.

---

**TweetTrack Sentinel** - *Advanced Political Intelligence & Social Media Monitoring.*
