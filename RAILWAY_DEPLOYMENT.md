# 🚂 Railway.app Deployment Guide for StockPilot

This guide will walk you through deploying StockPilot to Railway.app for 24/7 operation.

## ✅ Prerequisites

Before you begin, make sure you have:
- [ ] A GitHub account
- [ ] Your StockPilot code ready
- [ ] Telegram bot token and chat ID configured in `config/settings.yaml`
- [ ] Tested the bot locally and it works

---

## 📋 Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

1. **Create a new repository on GitHub**
   - Go to [github.com](https://github.com) and click "New repository"
   - Name it `stockpilot` (or any name you prefer)
   - Keep it private if you want
   - Don't initialize with README (you already have one)

2. **Push your code to GitHub**
   
   Open a terminal in your stockpilot directory and run:
   
   ```bash
   cd stockpilot
   git init
   git add .
   git commit -m "Initial commit - StockPilot ready for deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/stockpilot.git
   git push -u origin main
   ```
   
   Replace `YOUR-USERNAME` with your actual GitHub username.

---

### Step 2: Sign Up for Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Login"** in the top right
3. Click **"Login with GitHub"**
4. Authorize Railway to access your GitHub account

**Note**: Railway offers $5 free credit per month, which is enough for 24/7 operation of StockPilot.

---

### Step 3: Deploy Your Project

1. **Create a new project**
   - Click **"New Project"** on the Railway dashboard
   - Select **"Deploy from GitHub repo"**
   - Choose your `stockpilot` repository from the list
   - Click on the repository to deploy it

2. **Railway will automatically:**
   - Detect that it's a Python project
   - Read your `requirements.txt`
   - Install all dependencies
   - Use the `Procfile` to know how to start your bot

3. **Wait for deployment**
   - You'll see the build logs in real-time
   - This may take 2-5 minutes
   - Look for "Build successful" message

---

### Step 4: Configure Environment (Optional)

If you want to use environment variables instead of hardcoding credentials:

1. Click on your deployed service
2. Go to **"Variables"** tab
3. Add these variables:
   - `TELEGRAM_BOT_TOKEN`: Your bot token
   - `TELEGRAM_CHAT_ID`: Your chat ID
4. Click **"Add"** for each

**Note**: If you already have credentials in `settings.yaml`, you can skip this step.

---

### Step 5: Check Deployment Status

1. **View logs**
   - Click on your service
   - Go to **"Deployments"** tab
   - Click on the latest deployment
   - View the logs to see if the bot started successfully

2. **Look for these messages in the logs:**
   ```
   ============================================================
   STOCKPILOT - Automated Stock Trading Signal Bot
   ============================================================
   Loaded X stocks in watchlist
   Telegram bot initialized successfully
   StockPilot is running...
   ```

3. **Test the bot**
   - Open Telegram
   - Send `/start` to your bot
   - You should receive a welcome message

---

### Step 6: Monitor Your Bot

1. **Check logs regularly**
   - Railway dashboard → Your service → Deployments → View logs
   - Look for any errors or warnings

2. **Monitor resource usage**
   - Go to **"Metrics"** tab
   - Check CPU and memory usage
   - Make sure you're within the free tier limits

3. **Check Telegram**
   - You should receive signals when the bot finds trading opportunities
   - Daily summaries will be sent as configured

---

## 🔧 Configuration Files Explained

Your project already has these files configured:

### `Procfile`
```
worker: python main.py
```
This tells Railway to run your bot as a background worker (not a web service).

### `runtime.txt`
```
python-3.11.0
```
This specifies which Python version to use.

### `requirements.txt`
Contains all the Python packages your bot needs.

---

## 🚨 Troubleshooting

### Bot Not Starting

**Check the logs for errors:**
1. Railway dashboard → Your service → Deployments → View logs
2. Look for error messages

**Common issues:**
- **TA-Lib installation fails**: This is normal. The bot will work without it.
- **Config file not found**: Make sure `config/settings.yaml` is in your repository
- **Telegram credentials invalid**: Double-check your bot token and chat ID

### Bot Keeps Restarting

**Possible causes:**
1. **Error in code**: Check logs for Python errors
2. **Missing dependencies**: Make sure all packages are in `requirements.txt`
3. **Memory limit exceeded**: Reduce scan frequency in settings

**To reduce memory usage:**
Edit `config/settings.yaml`:
```yaml
data:
  update_interval_minutes: 5  # Increase from 1 to 5
```

### Not Receiving Telegram Messages

1. **Verify bot token and chat ID** in `config/settings.yaml`
2. **Check if bot is running** in Railway logs
3. **Test with `/start` command** in Telegram
4. **Check Telegram settings**:
   ```yaml
   telegram:
     enabled: true
   ```

### Out of Free Credits

Railway provides $5/month free credit. If you run out:

**Option 1: Reduce usage**
- Increase scan interval in `settings.yaml`
- Reduce number of stocks in watchlist

**Option 2: Add payment method**
- Railway will charge you only for what you use beyond free tier
- Typically costs $5-10/month for 24/7 operation

**Option 3: Use multiple free services**
- Deploy to Railway for 2 weeks
- Deploy to Render.com for 2 weeks
- Alternate between services

---

## 📊 Expected Costs

| Usage | Free Tier | Paid (if exceeded) |
|-------|-----------|-------------------|
| 24/7 operation | $5 credit/month | ~$5-10/month |
| Part-time (market hours only) | Free | $0 |
| With reduced scan frequency | Free | $0 |

**Tips to stay within free tier:**
- Run only during market hours (9 AM - 4 PM)
- Increase scan interval to 5-15 minutes
- Reduce number of stocks in watchlist

---

## 🔄 Updating Your Bot

When you want to update your code:

1. **Make changes locally**
2. **Test locally** to make sure it works
3. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Updated configuration"
   git push
   ```
4. **Railway automatically redeploys** when you push to GitHub
5. **Check logs** to verify the update was successful

---

## 🛑 Stopping Your Bot

If you need to stop the bot temporarily:

1. Go to Railway dashboard
2. Click on your service
3. Go to **"Settings"** tab
4. Scroll down and click **"Remove Service"**

Or just pause it:
1. Go to **"Settings"**
2. Click **"Sleep Service"** (if available)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created and connected to GitHub
- [ ] Project deployed on Railway
- [ ] Build completed successfully
- [ ] Bot is running (check logs)
- [ ] Telegram bot responds to `/start`
- [ ] Monitoring set up
- [ ] Test signal received (if market is open)

---

## 🎯 Next Steps

After successful deployment:

1. **Monitor for 24 hours** to ensure stability
2. **Check Telegram** for signals during market hours
3. **Review logs** daily for any errors
4. **Adjust settings** based on performance
5. **Set up alerts** for bot downtime (optional)

---

## 💡 Pro Tips

1. **Keep your repository private** if it contains sensitive information
2. **Use environment variables** for credentials instead of hardcoding
3. **Enable GitHub Actions** for automated testing before deployment
4. **Set up a backup deployment** on another service (Render.com)
5. **Monitor your Railway credits** to avoid unexpected charges

---

## 📞 Getting Help

If you encounter issues:

1. **Check the logs** first - they usually tell you what's wrong
2. **Review this guide** - make sure you followed all steps
3. **Check Railway documentation** at [docs.railway.app](https://docs.railway.app)
4. **Test locally** - if it doesn't work locally, it won't work on Railway

---

## 🎉 Success!

If you see this in your logs and receive Telegram messages, you're all set:

```
============================================================
STOCKPILOT - Automated Stock Trading Signal Bot
============================================================
Loaded X stocks in watchlist
Telegram bot initialized successfully
StockPilot is running...
Scheduler started. Waiting for market hours...
```

Your bot is now running 24/7 in the cloud! 🚀

---

*Last updated: June 2026*
