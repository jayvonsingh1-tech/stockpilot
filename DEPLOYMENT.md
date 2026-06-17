# StockPilot - Cloud Deployment Guide

## 🌐 Free Cloud Hosting Options

This guide shows you how to deploy StockPilot to run 24/7 on free cloud hosting.

---

## Option 1: PythonAnywhere (Easiest - Recommended)

**Best for beginners. Free tier includes 24/7 operation.**

### Step 1: Sign Up
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Click "Start running Python online in less than a minute!"
3. Create a free "Beginner" account

### Step 2: Upload Your Code
1. Click on "Files" tab
2. Click "Upload a file"
3. Upload your entire `stockpilot` folder as a zip file
4. Or use Git: Click "Consoles" → "Bash" and run:
   ```bash
   git clone <your-repo-url>
   cd stockpilot
   ```

### Step 3: Install Dependencies
1. Click "Consoles" → "Bash"
2. Run:
   ```bash
   cd stockpilot
   pip3.10 install --user -r requirements.txt
   ```

**Note**: TA-Lib is tricky on PythonAnywhere. If it fails:
```bash
# Remove ta-lib from requirements.txt
# The bot will still work, just without some advanced indicators
```

### Step 4: Configure Settings
1. Click "Files" → navigate to `stockpilot/config/settings.yaml`
2. Edit your Telegram credentials
3. Save the file

### Step 5: Create Always-On Task
1. Click "Tasks" tab
2. Create a new scheduled task:
   - **Command**: `python3.10 /home/yourusername/stockpilot/main.py`
   - **Hour**: Leave blank (runs continuously)
   - **Minute**: Leave blank
3. Click "Create"

### Step 6: Start the Bot
1. Click "Consoles" → "Bash"
2. Run:
   ```bash
   cd stockpilot
   python3.10 main.py
   ```

**Limitations**:
- Free tier has CPU limits (may need to reduce scan frequency)
- Limited to 100 seconds of CPU time per day
- May need to upgrade to paid plan ($5/month) for full 24/7 operation

---

## Option 2: Render.com (Better for 24/7)

**Free tier with 750 hours/month (enough for 24/7 operation).**

### Step 1: Prepare Your Code
1. Create a `Procfile` in your stockpilot folder:
   ```
   worker: python main.py
   ```

2. Create `runtime.txt`:
   ```
   python-3.11.0
   ```

3. Update `requirements.txt` - remove `ta-lib` if it causes issues

### Step 2: Push to GitHub
```bash
cd stockpilot
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 3: Deploy on Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Background Worker"
4. Connect your GitHub repository
5. Configure:
   - **Name**: stockpilot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
6. Add environment variables (if needed):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
7. Click "Create Background Worker"

### Step 4: Monitor
- Check logs in Render dashboard
- Bot will restart automatically if it crashes

**Limitations**:
- Free tier spins down after 15 minutes of inactivity
- Need to upgrade to paid ($7/month) for true 24/7

---

## Option 3: Railway.app (Most Generous Free Tier)

**$5 free credit per month (enough for 24/7 operation).**

### Step 1: Prepare Your Code
Same as Render - create `Procfile` and `runtime.txt`

### Step 2: Deploy
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your stockpilot repository
5. Railway auto-detects Python and installs dependencies
6. Add environment variables in Settings

### Step 3: Configure
1. Go to Settings
2. Set start command: `python main.py`
3. Bot starts automatically

**Limitations**:
- $5 credit = ~500 hours of runtime per month
- Need to add credit card for more (but won't charge unless you exceed free tier)

---

## Option 4: Google Cloud (Free Tier)

**Always free tier with limitations.**

### Step 1: Create VM Instance
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project
3. Go to Compute Engine → VM Instances
4. Create instance:
   - **Machine type**: e2-micro (free tier)
   - **Boot disk**: Ubuntu 22.04 LTS
   - **Firewall**: Allow HTTPS traffic

### Step 2: Connect via SSH
1. Click "SSH" button in VM instances
2. Install Python and dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip git -y
   git clone <your-repo-url>
   cd stockpilot
   pip3 install -r requirements.txt
   ```

### Step 3: Run Bot as Service
1. Create systemd service:
   ```bash
   sudo nano /etc/systemd/system/stockpilot.service
   ```

2. Add:
   ```ini
   [Unit]
   Description=StockPilot Trading Bot
   After=network.target

   [Service]
   Type=simple
   User=yourusername
   WorkingDirectory=/home/yourusername/stockpilot
   ExecStart=/usr/bin/python3 /home/yourusername/stockpilot/main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl enable stockpilot
   sudo systemctl start stockpilot
   sudo systemctl status stockpilot
   ```

**Limitations**:
- Free tier: 1 e2-micro instance per month
- Limited to US regions
- Requires credit card (but won't charge for free tier usage)

---

## Option 5: Oracle Cloud (Most Generous)

**Always free tier with 2 VMs and 200GB storage.**

### Similar to Google Cloud
1. Sign up at [cloud.oracle.com](https://cloud.oracle.com)
2. Create free tier VM (Ampere A1 or AMD)
3. Follow same steps as Google Cloud

**Benefits**:
- More generous free tier than Google
- 2 VMs instead of 1
- Better for long-term free hosting

---

## 🎯 Recommended Setup

### For Beginners:
**Railway.app** - Easiest setup, generous free tier

### For 24/7 Operation:
**Oracle Cloud** - Most generous always-free tier

### Quick Test:
**PythonAnywhere** - Fastest to get started

---

## 📝 Configuration Tips

### Environment Variables
Instead of hardcoding credentials in `settings.yaml`, use environment variables:

```python
# In your code
import os

telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', 'default-value')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', 'default-value')
```

### Reduce Scan Frequency for Free Tiers
If hitting CPU limits, edit `src/scheduler.py`:
```python
# Change from every 15 minutes to every 30 minutes
CronTrigger(hour='9-15', minute='0,30', day_of_week='mon-fri')
```

### Monitor Resource Usage
Add logging to track CPU/memory:
```python
import psutil
logger.info(f"CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%")
```

---

## 🔧 Troubleshooting

### TA-Lib Installation Fails
Remove from `requirements.txt` - the bot will work without it (just fewer indicators)

### Bot Keeps Crashing
- Check logs for errors
- Reduce scan frequency
- Ensure enough memory (upgrade to paid tier if needed)

### Telegram Not Working
- Verify bot token and chat ID
- Check firewall rules
- Test with `/start` command in Telegram

### Out of Free Credits
- Reduce scan frequency
- Use multiple free tier accounts
- Upgrade to paid tier ($5-7/month)

---

## 💰 Cost Comparison

| Provider | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| PythonAnywhere | Limited CPU | $5/month | Beginners |
| Render | 750 hrs/month | $7/month | Simple deployment |
| Railway | $5 credit/month | Pay as you go | Flexible usage |
| Google Cloud | 1 e2-micro VM | Pay as you go | Long-term free |
| Oracle Cloud | 2 VMs always free | Pay as you go | Best free tier |

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Telegram credentials configured
- [ ] Dependencies installed
- [ ] Bot tested locally
- [ ] Cloud service account created
- [ ] Bot deployed and running
- [ ] Logs checked for errors
- [ ] Test signal received on Telegram
- [ ] Monitoring set up

---

## 🚀 Next Steps

After deployment:
1. Monitor logs for first 24 hours
2. Verify scheduled scans are working
3. Check Telegram receives signals
4. Set up alerts for bot downtime
5. Consider backup deployment on second provider

---

*For more help, check the logs or reach out with specific error messages.*
