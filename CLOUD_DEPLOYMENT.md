# 🚀 Cloud Deployment Guide - Vercel + Render + Supabase

This guide will help you deploy TweetTrack Sentinel to the cloud in **under 30 minutes**.

## 📋 Prerequisites

Before starting, create accounts on:
1. **Vercel** - https://vercel.com (for Frontend)
2. **Render** - https://render.com (for Backend + Scraper)
3. **Supabase** - https://supabase.com (for Database)
4. **GitHub** - https://github.com (to push your code)

---

## 🗄️ Step 1: Setup Supabase Database (5 minutes)

### 1.1 Create a New Project
1. Go to https://supabase.com/dashboard
2. Click **"New Project"**
3. Fill in:
   - **Name**: `tweettrack-db`
   - **Database Password**: (create a strong password - save it!)
   - **Region**: Choose closest to you
4. Click **"Create new project"** (takes 2-3 minutes)

### 1.2 Get Database URL
1. Once created, go to **Settings** → **Database**
2. Scroll to **Connection String** → **URI**
3. Copy the connection string (looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
4. **Replace `[YOUR-PASSWORD]`** with your actual password
5. Save this URL - you'll need it later!

### 1.3 Initialize Database Schema
1. In Supabase dashboard, go to **SQL Editor**
2. Click **"New Query"**
3. Run this SQL to create tables:

```sql
-- Create monitored_accounts table
CREATE TABLE monitored_accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    last_checked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tweets table
CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) UNIQUE NOT NULL,
    account_username VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    summary TEXT,
    link VARCHAR(500),
    posted_at TIMESTAMP NOT NULL,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_data TEXT,
    is_alert_sent BOOLEAN DEFAULT false,
    FOREIGN KEY (account_username) REFERENCES monitored_accounts(username)
);

-- Create indexes for performance
CREATE INDEX idx_tweets_posted_at ON tweets(posted_at DESC);
CREATE INDEX idx_tweets_account ON tweets(account_username);
CREATE INDEX idx_tweets_scraped_at ON tweets(scraped_at DESC);
```

4. Click **"Run"**
5. You should see: `Success. No rows returned`

---

## 🐙 Step 2: Push Code to GitHub (3 minutes)

### 2.1 Create GitHub Repository
1. Go to https://github.com/new
2. **Repository name**: `tweettrack-sentinel`
3. **Visibility**: Private (recommended)
4. Click **"Create repository"**

### 2.2 Push Your Code
Open terminal in your project folder and run:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Production ready"

# Add remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/tweettrack-sentinel.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🔧 Step 3: Deploy Backend to Render (10 minutes)

### 3.1 Create New Web Service
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"** → Select your GitHub repo
4. Fill in:
   - **Name**: `tweettrack-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`

### 3.2 Add Environment Variables
Scroll down to **"Environment Variables"** and add these (click **"Add Environment Variable"** for each):

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Supabase connection string from Step 1.2 |
| `TWITTER_USERNAME` | Your Twitter username |
| `TWITTER_PASSWORD` | Your Twitter password |
| `TWITTER_EMAIL` | Your Twitter email |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_WHATSAPP_NUMBER` | Your Twilio WhatsApp number (e.g., whatsapp:+14155238886) |
| `WHATSAPP_TO_NUMBERS` | Comma-separated numbers (e.g., +919876543210,+919876543211) |
| `POLL_INTERVAL_SECONDS` | `600` |
| `MONITORED_ACCOUNTS` | Comma-separated Twitter usernames (e.g., ArvindKejriwal,AtishiAAP) |
| `PORT` | `8000` |

### 3.3 Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Once deployed, you'll see a URL like: `https://tweettrack-backend.onrender.com`
4. **Save this URL!**
5. Test it by visiting: `https://tweettrack-backend.onrender.com/health`
   - You should see: `{"status":"healthy","timestamp":"..."}`

---

## 🎨 Step 4: Deploy Frontend to Vercel (5 minutes)

### 4.1 Update Frontend API URL
1. Open `frontend/src/services/api.js`
2. Find the line with `const API_BASE_URL`
3. Replace it with your Render backend URL:
   ```javascript
   const API_BASE_URL = 'https://tweettrack-backend.onrender.com';
   ```
4. Save the file
5. Commit and push:
   ```bash
   git add .
   git commit -m "Update API URL for production"
   git push
   ```

### 4.2 Deploy to Vercel
1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select your `tweettrack-sentinel` repository
4. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Click **"Deploy"**
6. Wait 2-3 minutes
7. You'll get a URL like: `https://tweettrack-sentinel.vercel.app`

---

## ✅ Step 5: Verify Everything Works

### 5.1 Check Backend
1. Visit: `https://tweettrack-backend.onrender.com/health`
2. Should see: `{"status":"healthy",...}`

### 5.2 Check Frontend
1. Visit your Vercel URL: `https://tweettrack-sentinel.vercel.app`
2. You should see the dashboard loading
3. Check if tweets appear (may take 10 minutes for first scrape)

### 5.3 Check Database
1. Go to Supabase → **Table Editor**
2. Select `monitored_accounts` table
3. You should see your accounts listed

### 5.4 Check WhatsApp Alerts
1. Wait for a new tweet to be posted by monitored accounts
2. You should receive a WhatsApp message within 10 minutes

---

## 🎉 You're Live!

Your TweetTrack Sentinel is now running 24/7 in the cloud!

### 📱 Access Your Dashboard
- **Production URL**: Your Vercel URL
- **Backend API**: Your Render URL

### 🔄 Future Updates
To update your deployment:
```bash
# Make changes to your code
git add .
git commit -m "Your update message"
git push
```

Both Vercel and Render will automatically redeploy!

---

## 🆘 Troubleshooting

### Backend not starting?
1. Check Render logs: Dashboard → Your Service → Logs
2. Verify all environment variables are set correctly
3. Make sure DATABASE_URL has the correct password

### Frontend not loading data?
1. Check browser console for errors (F12)
2. Verify API_BASE_URL in `frontend/src/services/api.js`
3. Make sure backend is running (check /health endpoint)

### No WhatsApp alerts?
1. Check Render logs for errors
2. Verify Twilio credentials in environment variables
3. Make sure phone numbers are in correct format (+country code)

### Database connection errors?
1. Verify Supabase connection string
2. Make sure you replaced `[YOUR-PASSWORD]` with actual password
3. Check if Supabase project is active

---

## 💰 Cost Breakdown

- **Supabase**: Free (up to 500MB database)
- **Render**: Free (750 hours/month)
- **Vercel**: Free (unlimited for personal projects)
- **Total**: **$0/month** 🎉

---

## 📊 Monitoring

### Render Dashboard
- View logs: https://dashboard.render.com → Your Service → Logs
- Check metrics: CPU, Memory usage
- View deployment history

### Supabase Dashboard
- Monitor database size
- View query performance
- Check connection count

### Vercel Dashboard
- View deployment history
- Check analytics
- Monitor bandwidth usage

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** (already in .gitignore)
2. **Use environment variables** for all secrets
3. **Keep dependencies updated**: Run `pip list --outdated` monthly
4. **Monitor logs** for suspicious activity
5. **Rotate API keys** every 3-6 months

---

## 🚀 Next Steps

1. **Custom Domain**: Add your own domain in Vercel settings
2. **Email Alerts**: Add email notifications alongside WhatsApp
3. **Analytics**: Track tweet sentiment trends over time
4. **Backup**: Setup automated database backups in Supabase

---

**Need help?** Check the logs first:
- **Backend**: Render Dashboard → Logs
- **Frontend**: Browser Console (F12)
- **Database**: Supabase Dashboard → Logs

Happy monitoring! 🎯
