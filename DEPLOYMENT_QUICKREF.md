# 🚀 Quick Deployment Reference Card

## 📋 Pre-Deployment Checklist

- [ ] GitHub account created
- [ ] Vercel account created (https://vercel.com)
- [ ] Render account created (https://render.com)
- [ ] Supabase account created (https://supabase.com)
- [ ] All API keys ready (Twitter, Gemini, Twilio)

---

## 🗄️ Database Setup (Supabase)

1. Create project: `tweettrack-db`
2. Copy connection string from Settings → Database
3. Run SQL schema (see CLOUD_DEPLOYMENT.md Step 1.3)
4. Save connection string for later

**Connection String Format:**
```
postgresql://postgres:YOUR_PASSWORD@db.xxx.supabase.co:5432/postgres
```

---

## 🐙 GitHub Push

```bash
git init
git add .
git commit -m "Production ready deployment"
git remote add origin https://github.com/YOUR-USERNAME/tweettrack-sentinel.git
git branch -M main
git push -u origin main
```

---

## 🔧 Backend Deployment (Render)

1. New Web Service → Connect GitHub repo
2. Settings:
   - **Name**: `tweettrack-backend`
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `python main.py`
   - **Instance**: Free

3. Environment Variables (Add all):
   ```
   DATABASE_URL=postgresql://postgres:...
   TWITTER_USERNAME=your_username
   TWITTER_PASSWORD=your_password
   TWITTER_EMAIL=your_email
   GEMINI_API_KEY=your_key
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   WHATSAPP_TO_NUMBERS=+919876543210,+919876543211
   POLL_INTERVAL_SECONDS=600
   MONITORED_ACCOUNTS=account1,account2,account3
   PORT=8000
   ```

4. Deploy & copy URL: `https://tweettrack-backend.onrender.com`

---

## 🎨 Frontend Deployment (Vercel)

### Option 1: Via Vercel Dashboard
1. Import Git Repository
2. Framework: **Vite**
3. Root Directory: **frontend**
4. Build Command: **npm run build**
5. Output Directory: **dist**
6. Environment Variable:
   ```
   VITE_API_URL=https://tweettrack-backend.onrender.com
   ```
7. Deploy!

### Option 2: Via CLI
```bash
npm install -g vercel
cd frontend
vercel --prod
```

---

## ✅ Verification Steps

1. **Backend Health**: Visit `https://your-backend.onrender.com/health`
   - Should return: `{"status":"healthy",...}`

2. **Frontend**: Visit your Vercel URL
   - Dashboard should load
   - Check browser console for errors

3. **Database**: Supabase → Table Editor
   - Check `monitored_accounts` table has entries

4. **WhatsApp**: Wait 10 minutes for first scrape
   - Should receive alert for new tweets

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Render logs, verify all env vars set |
| Frontend blank | Check API URL in env vars, verify backend is running |
| No tweets | Check backend logs, verify Twitter credentials |
| No WhatsApp | Check Twilio credentials, verify phone number format |
| Database errors | Verify Supabase connection string, check password |

---

## 📊 Monitoring

- **Backend Logs**: Render Dashboard → Your Service → Logs
- **Frontend Logs**: Browser Console (F12)
- **Database**: Supabase Dashboard → Logs
- **Metrics**: Render Dashboard → Metrics

---

## 🔄 Future Updates

```bash
# Make changes
git add .
git commit -m "Update description"
git push

# Both Vercel and Render auto-deploy!
```

---

## 💰 Free Tier Limits

- **Supabase**: 500MB database, 2GB bandwidth/month
- **Render**: 750 hours/month (enough for 24/7)
- **Vercel**: Unlimited deployments, 100GB bandwidth/month

**All free tiers are more than enough for this project!**

---

## 🔗 Important URLs

After deployment, save these:
- Frontend: `https://your-project.vercel.app`
- Backend: `https://your-backend.onrender.com`
- Database: Supabase Dashboard
- GitHub: `https://github.com/YOUR-USERNAME/tweettrack-sentinel`

---

## 📞 Support

If stuck, check:
1. `CLOUD_DEPLOYMENT.md` - Detailed guide
2. `PRODUCTION_CLEANUP.md` - What was changed
3. `README.md` - General documentation
4. Service logs (Render/Vercel/Supabase)

---

**Deployment Time: ~30 minutes**
**Cost: $0/month**
**Uptime: 24/7**

🎉 **Happy Deploying!**
