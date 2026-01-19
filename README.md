# 🔥 ABS_Stream_Fucker - Production Ready Telegram Stream Bot

A fully production-ready Telegram bot + Web application for file streaming and downloading with advanced features.

## ✨ Features

### 🤖 Bot Features
- **File Upload & Stream**: Upload files to get instant stream + download links
- **Link Leeching**: Download from Terabox, YouTube, Instagram, Hubdrive, etc.
- **Password Protection**: Secure your files with passwords
- **Force Subscribe**: Multiple channel/group support
- **User Management**: Free/Premium user tiers with limits
- **Admin Panel**: Complete control via `/boss` command
- **Smart Limits**: Daily limits for free users, unlimited for premium
- **Auto Muting**: Users who exceed limits get 24h mute instead of ban
- **Detailed Logging**: All activities logged to private channel

### 🌐 Web Features
- **Dark Theme UI**: Modern, clean interface
- **Video/Audio Streaming**: In-browser playback with seek support
- **Password Protected Access**: Secure file viewing
- **Download Support**: Direct file downloads
- **Mobile Responsive**: Works on all devices

### 🔐 Security
- **Token-based URLs**: Unique tokens for each file
- **Password Protection**: Optional password + key system
- **Expiry System**: Auto-expire links (24h for free, 1 year for premium)
- **Access Control**: Rate limiting and attempt tracking

## 📁 Project Structure

```
ABS_Stream_Fucker/
├── bot/
│   ├── handlers/        # All bot handlers
│   ├── utils/           # Utilities (database, security, etc.)
│   ├── config.py        # Configuration
│   └── main.py          # Bot entry point
├── web/
│   ├── routes/          # API routes
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS files
│   └── app.py           # FastAPI application
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
├── Procfile            # For Heroku/Railway deployment
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB
- Telegram Bot Token (from @BotFather)
- Telegram API ID & Hash (from my.telegram.org)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd ABS_Stream_Fucker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:
```env
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
MONGO_URI=mongodb://localhost:27017
DB_NAME=abs_stream_fucker
WEB_URL=https://yourdomain.com
WEB_PORT=8000
OWNER_ID=your_telegram_id
LOG_CHANNEL=-100xxxxxxxxxx
SECRET_KEY=your_random_secret
PREMIUM_USERS=123456,789012
```

4. **Run MongoDB** (if not using Docker)
```bash
mongod --dbpath /path/to/data
```

5. **Start the bot**
```bash
python -m bot.main
```

6. **Start the web server** (in another terminal)
```bash
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

## 🐳 Docker Deployment

**Using Docker Compose (Recommended)**

1. Create `.env` file with your credentials

2. Run:
```bash
docker-compose up -d
```

This will start:
- MongoDB container
- Bot + Web server container

**Manual Docker Build**

```bash
docker build -t abs_stream_fucker .
docker run -d --env-file .env -p 8000:8000 abs_stream_fucker
```

## ☁️ Cloud Deployment

### Heroku

1. Create a new Heroku app
2. Add MongoDB addon: `heroku addons:create mongolab`
3. Set environment variables:
```bash
heroku config:set BOT_TOKEN=xxx
heroku config:set API_ID=xxx
heroku config:set API_HASH=xxx
# ... set all other variables
```
4. Deploy:
```bash
git push heroku main
```

### Railway

1. Create new project on Railway
2. Add MongoDB database
3. Connect GitHub repo
4. Set environment variables in Railway dashboard
5. Deploy automatically

### Render

1. Create new Web Service
2. Connect repository
3. Set environment variables
4. Deploy

## 🎮 Bot Commands

### User Commands
- `/start` - Start the bot
- `/password <pass>` - Set password for last uploaded file

### Admin Commands
- `/boss` - Open admin panel
- `/ui <user_id>` - Get user info and manage
- `/addfsub <channel_id> <name>` - Add force subscribe channel
- `/rmfsub <channel_id>` - Remove force subscribe channel
- `/restart` - Restart the bot

## 👥 User Tiers

### Free Users
- 4 files per day
- 5 generated links per day
- 8 seconds wait time
- 24 hours link expiry
- 3 password attempts

### Premium Users
- Unlimited files
- Unlimited links
- 0 seconds wait time
- 1 year link expiry
- Extended features

## 🔧 Configuration

Edit `bot/config.py` to customize:
- User limits
- Expiry times
- Supported leech sites
- Bot personality
- And more...

## 📝 Usage Examples

### Upload File
1. Send any file to bot
2. Wait for processing
3. Get stream + download links
4. Optional: Reply `/password mypass` to protect

### Leech from URL
1. Send supported URL (YouTube, Terabox, etc.)
2. Bot downloads the file
3. Choose to receive file or just links
4. Get stream + download links

### Stream File
1. Open stream link in browser
2. Enter password if protected
3. Watch/listen in browser

### Download File
1. Open download link
2. Enter password if protected
3. File downloads to device

## 🛠️ Troubleshooting

### Bot not responding
- Check if bot token is correct
- Verify API ID and Hash
- Check MongoDB connection

### Files not streaming
- Ensure WEB_URL is set correctly
- Check if port 8000 is accessible
- Verify file hasn't expired

### Download errors
- Check file size limits
- Verify Telegram file_id is valid
- Check network connection

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## ⚠️ Disclaimer

This bot is for educational purposes. Users are responsible for:
- Respecting copyright laws
- Following Telegram ToS
- Not distributing illegal content

## 📄 License

MIT License - See LICENSE file

## 💬 Support

Need help? Contact:
- Telegram: @YOUR_USERNAME
- Issues: GitHub Issues

## 🔥 Credits

Created with savage energy by ABS Team 💪

---

**Note**: Replace `YOUR_USERNAME`, `your-repo-url`, and other placeholders with actual values before deployment.

**Enjoy streaming like a boss! 🔥**
