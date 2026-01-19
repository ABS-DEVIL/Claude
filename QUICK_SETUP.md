# ⚡ Quick Setup Guide - ABS Stream Fucker

Get up and running in 5 minutes! 🔥

## 🎯 What You Need

1. Telegram Bot Token (from @BotFather)
2. Telegram API ID & Hash (from my.telegram.org)
3. Python 3.11+ installed
4. MongoDB (local or Atlas)

## 🚀 Setup Steps

### Step 1: Get Bot Token

```
1. Open Telegram
2. Search for @BotFather
3. Send: /newbot
4. Follow instructions
5. Copy the bot token
```

### Step 2: Get API Credentials

```
1. Visit: https://my.telegram.org
2. Login with phone number
3. Go to: API Development Tools
4. Create new application
5. Copy API_ID and API_HASH
```

### Step 3: Create Log Channel

```
1. Create a new private channel in Telegram
2. Add your bot as admin
3. Forward any message from channel to @userinfobot
4. Copy the channel ID (starts with -100)
```

### Step 4: Install & Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd ABS_Stream_Fucker

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### Step 5: Edit .env File

Open `.env` and fill in:

```env
# Required - Get from @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Required - Get from my.telegram.org
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890

# Required - Your Telegram user ID
OWNER_ID=123456789

# Required - Private channel ID (starts with -100)
LOG_CHANNEL=-1001234567890

# MongoDB (use default for local)
MONGO_URI=mongodb://localhost:27017
DB_NAME=abs_stream_fucker

# Your domain (for deployment)
WEB_URL=http://localhost:8000
WEB_PORT=8000

# Random secret key (generate any random string)
SECRET_KEY=your_random_secret_key_here_make_it_long

# Premium users (comma separated IDs)
PREMIUM_USERS=123456789,987654321

# Storage
STORAGE_PATH=./downloads
```

### Step 6: Start MongoDB

**Option A: Local MongoDB**
```bash
# Install MongoDB first, then:
mongod --dbpath ./data/db
```

**Option B: MongoDB Atlas (Cloud)**
```
1. Go to: https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create free cluster
4. Add database user
5. Whitelist IP: 0.0.0.0/0
6. Get connection string
7. Use in MONGO_URI
```

### Step 7: Run the Bot

**Terminal 1 - Bot:**
```bash
python -m bot.main
```

**Terminal 2 - Web Server:**
```bash
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

**Or use start.sh (Linux/Mac):**
```bash
chmod +x start.sh
./start.sh
```

## ✅ Test It

1. **Open Telegram**
2. **Search for your bot** (the username you gave @BotFather)
3. **Send:** `/start`
4. **Upload a file** or **send a YouTube link**
5. **Get your stream links!** 🎉

## 🌐 Access Web UI

Open browser:
```
http://localhost:8000
```

## 🐳 Quick Docker Setup

**Easiest Method!**

```bash
# 1. Create .env file (as above)
cp .env.example .env
nano .env

# 2. Start everything with Docker
docker-compose up -d

# 3. Check logs
docker-compose logs -f

# Done! 🎉
```

## 🔧 Common Issues

### "Bot not responding"
- ✅ Check BOT_TOKEN is correct
- ✅ Check API_ID and API_HASH
- ✅ Make sure MongoDB is running

### "MongoDB connection error"
- ✅ Start MongoDB: `mongod --dbpath ./data/db`
- ✅ Or use MongoDB Atlas connection string

### "Port already in use"
- ✅ Change WEB_PORT in .env
- ✅ Or kill process: `kill $(lsof -t -i:8000)`

### "File not found"
- ✅ Create downloads folder: `mkdir downloads`
- ✅ Check STORAGE_PATH in .env

## 📱 Admin Commands

Once bot is running:

```
/start - Welcome message
/boss - Admin panel (owner only)
/ui 123456789 - User info (owner only)
/password mypass123 - Set password for last file
```

## 🎮 User Features

- **Upload any file** → Get stream + download links
- **Send YouTube/Insta link** → Auto download + stream
- **Password protect** files
- **Free limits:** 4 files, 5 links per day
- **Premium:** Unlimited everything

## 💎 Add Premium Users

1. Get user's Telegram ID (forward their message to @userinfobot)
2. Add to .env: `PREMIUM_USERS=123456789,987654321`
3. Restart bot

Or use `/ui` command:
```
/ui 123456789
[Click "Add Premium" button]
```

## 🚀 Deploy to Cloud

After local testing, deploy:

### Heroku (Free)
```bash
heroku create
heroku addons:create mongolab
heroku config:set BOT_TOKEN=xxx API_ID=xxx ...
git push heroku main
```

### Railway (Better than Heroku)
```
1. Push to GitHub
2. Import to Railway
3. Add MongoDB database
4. Set environment variables
5. Deploy!
```

See `DEPLOYMENT.md` for detailed cloud deployment.

## 📊 Monitoring

Check if everything is working:

```bash
# Bot logs
tail -f bot.log

# Web logs  
tail -f web.log

# Docker logs
docker-compose logs -f
```

## 🎯 Next Steps

1. ✅ Test file upload
2. ✅ Test link leeching
3. ✅ Set up force subscribe channels
4. ✅ Configure premium users
5. ✅ Deploy to cloud
6. ✅ Add custom domain
7. ✅ Setup SSL certificate

## 💬 Need Help?

- 📖 Full docs: README.md
- 🚀 Deployment: DEPLOYMENT.md
- 🐛 Issues: GitHub Issues
- 💬 Support: Telegram

---

**That's it! You're ready to stream like a boss! 🔥**

---

## 🎁 Bonus Tips

### Custom Bot Name
Change in `bot/config.py`:
```python
BOT_NAME = "Your_Custom_Name"
```

### Change Limits
Edit `bot/config.py`:
```python
FREE_FILE_LIMIT = 10  # Change from 4
FREE_LINK_LIMIT = 20  # Change from 5
```

### Add More Leech Sites
Add to `LEECH_SITES` in `bot/config.py`

### Custom Messages
Edit handlers in `bot/handlers/` folder

---

**Enjoy! 🔥💪**
