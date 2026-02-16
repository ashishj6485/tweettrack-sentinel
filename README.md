# 🐦 TweetTrack Sentinel

**TweetTrack Sentinel** is a professional-grade, live monitoring and analysis platform designed to track specific Twitter (X) profiles, analyze their content using state-of-the-art AI, and deliver real-time alerts via WhatsApp.

---

## 🏗️ Architecture & Design

The system follows a modern decoupled architecture designed for high availability and near-zero latency in AI processing.

### 🎨 Frontend (React + Vite)
- **Design Aesthetic**: Formal, business-tier user interface with a clean light theme and high-contrast slate typography.
- **Dynamic Dashboard**: Real-time monitoring feed with account-based filtering.
- **AI Insights**: Integrated summary cards and risk analysis data for every tweet.
- **Tech**: React 18, Vite, Vanilla CSS for maximum flexibility.

### ⚙️ Backend (FastAPI + Python)
- **High Performance**: Asynchronous API endpoints serving the dashboard and search functionality.
- **Robust Scraper**: Multi-account polling system with persistent session management to avoid rate limits.
- **Task Queue**: Background task processing for AI analysis and alerts, ensuring the main scraper remains fast and responsive.

### 🧠 AI Engine (Groq + Llama 3.1)
- **Lightning Fast**: Powered by Groq's LPUs, delivering AI summaries and political risk analysis in under 500ms.
- **Intelligent Summarization**: Automatically condenses long tweets into single, punchy sentences.
- **Political Risk Analysis**: Classifies tweets (ATTACK, GRIEVANCE, SUPPORT, NEUTRAL) and assigns urgency scores (1-5) and sentiment mapping.

### 🗄️ Database & Infrastructure
- **Supabase (PostgreSQL)**: Cloud-native database hosting tweet history, monitored accounts, and search logs.
- **Twilio WhatsApp API**: Real-time notification layer for delivering critical alerts to mobile devices.
- **Dual Deployment Support**: Can run fully in the cloud (Render/Vercel) or in a "Split Architecture" (Scraper locally, API/Frontend in the cloud) to bypass platform-specific blocking.

---

## 🚀 Key Features

- **Live Monitoring**: Track multiple high-profile accounts simultaneously.
- **AI Insights**: Instant summaries and deep political analysis for every post.
- **Real-Time Alerts**: High-urgency tweets are delivered directly to WhatsApp recipients.
- **Historical Analysis**: View and search through 24-hour archives of monitored data.
- **Cloud-Native**: Fully prepared for deployment on Vercel, Render, and Supabase.

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

### **Backend (Render)**
1. Connect GitHub repository and select the `backend` directory as root (or top-level with custom build/start commands).
2. Set `pip install -r requirements.txt` as Build Command.
3. Set `python main.py` as Start Command.
4. Set `RUN_MODE=api` if you wish to run only the API on Render (recommended if Twitter blocks Render IPs).

### **Frontend (Vercel)**
1. Connect GitHub repository.
2. Set Root Directory to `frontend`.
3. Set Build Command to `npm run build`.
4. Set `VITE_API_URL` to your Render backend URL.

---

## 📊 Monitoring & Maintenance
- **Logs**: Backend activity is logged to standard output.
- **Database**: Use the Supabase dashboard to manage monitored accounts and view raw data.
- **AI Quota**: Groq provides a generous free tier (Llama 3.1 8B) for high-volume analysis.

---

**TweetTrack Sentinel** - *Advanced Political Intelligence & Social Media Monitoring.*
