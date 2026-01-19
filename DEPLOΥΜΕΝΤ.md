# 🚀 Deployment Guide - ABS Stream Fucker

Complete deployment guide for different platforms.

## 📋 Prerequisites

Before deployment, you need:

1. **Telegram Bot Token**
   - Go to [@BotFather](https://t.me/BotFather)
   - Create new bot: `/newbot`
   - Save the token

2. **Telegram API Credentials**
   - Visit [my.telegram.org](https://my.telegram.org)
   - Login with your phone number
   - Go to API Development Tools
   - Create an app
   - Save API_ID and API_HASH

3. **MongoDB Database**
   - Local: Install MongoDB
   - Cloud: Use MongoDB Atlas (free tier available)

4. **Log Channel**
   - Create a private Telegram channel
   - Add your bot as admin
   - Get channel ID using [@userinfobot](https://t.me/userinfobot)

## 🖥️ Local Deployment

### Method 1: Direct Python

```bash
# Clone repository
git clone <your-repo>
cd ABS_Stream_Fucker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# Start MongoDB
mongod --dbpath ./data/db

# Run bot (Terminal 1)
python -m bot.main

# Run web server (Terminal 2)
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

### Method 2: Using start.sh

```bash
# Make script executable
chmod +x start.sh

# Run
./start.sh
```

### Method 3: Docker Compose (Recommended)

```bash
# Create .env file
cp .env.example .env
nano .env  # Edit with your credentials

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## ☁️ Cloud Platforms

### 🟣 Heroku

1. **Install Heroku CLI**
```bash
brew install heroku/brew/heroku  # macOS
# or download from heroku.com
```

2. **Login and Create App**
```bash
heroku login
heroku create abs-stream-fucker
```

3. **Add MongoDB**
```bash
heroku addons:create mongolab:sandbox
```

4. **Set Environment Variables**
```bash
heroku config:set BOT_TOKEN=your_token
heroku config:set API_ID=your_id
heroku config:set API_HASH=your_hash
heroku config:set WEB_URL=https://abs-stream-fucker.herokuapp.com
heroku config:set OWNER_ID=your_telegram_id
heroku config:set LOG_CHANNEL=-100xxxxxxxxxx
heroku config:set SECRET_KEY=random_secret_key
```

5. **Deploy**
```bash
git push heroku main
```

6. **Scale Dynos**
```bash
heroku ps:scale web=1 bot=1
```

**Important Notes for Heroku:**
- Free tier sleeps after 30 min inactivity
- Use hobby dyno ($7/mo) for 24/7 operation
- Storage is ephemeral (downloads folder clears on restart)
- Use Cloudinary or S3 for permanent file storage

### 🔷 Railway.app

1. **Create Account** at [railway.app](https://railway.app)

2. **New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Add MongoDB**
   - Click "New"
   - Select "Database"
   - Choose "MongoDB"

4. **Configure Variables**
   - Go to your service
   - Click "Variables"
   - Add all .env variables
   - Set `MONGO_URI` to Railway's MongoDB connection string

5. **Deploy**
   - Push to GitHub
   - Railway auto-deploys

**Railway Advantages:**
- $5 free credit monthly
- Better than Heroku free tier
- Easy setup
- Good for production

### 🟢 Render.com

1. **Create Account** at [render.com](https://render.com)

2. **Create Web Service**
   - New → Web Service
   - Connect repository
   - Name: abs-stream-fucker
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: See below

3. **Start Command**
```bash
uvicorn web.app:app --host 0.0.0.0 --port $PORT & python -m bot.main
```

4. **Add Environment Variables**
   - Add all variables from .env
   - Use Render's MongoDB or external

5. **Deploy**
   - Click "Create Web Service"

**Render Notes:**
- Free tier available (sleeps after inactivity)
- Paid tier: $7/mo for always-on
- Good performance

### 🔴 VPS (DigitalOcean, Linode, AWS EC2)

**Recommended for Production!**

1. **Create VPS**
   - Ubuntu 22.04 LTS
   - Minimum: 2GB RAM, 1 CPU
   - Recommended: 4GB RAM, 2 CPU

2. **Initial Setup**
```bash
# SSH into VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv nginx mongodb git

# Create user
adduser absbot
usermod -aG sudo absbot
su - absbot
```

3. **Clone & Setup**
```bash
# Clone repository
git clone <your-repo>
cd ABS_Stream_Fucker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your credentials
```

4. **Setup Systemd Services**

Create `/etc/systemd/system/abs-bot.service`:
```ini
[Unit]
Description=ABS Stream Fucker Bot
After=network.target

[Service]
Type=simple
User=absbot
WorkingDirectory=/home/absbot/ABS_Stream_Fucker
ExecStart=/home/absbot/ABS_Stream_Fucker/venv/bin/python -m bot.main
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/abs-web.service`:
```ini
[Unit]
Description=ABS Stream Fucker Web
After=network.target

[Service]
Type=simple
User=absbot
WorkingDirectory=/home/absbot/ABS_Stream_Fucker
ExecStart=/home/absbot/ABS_Stream_Fucker/venv/bin/uvicorn web.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start Services**
```bash
sudo systemctl daemon-reload
sudo systemctl enable abs-bot abs-web
sudo systemctl start abs-bot abs-web
sudo systemctl status abs-bot abs-web
```

6. **Setup Nginx Reverse Proxy**

Create `/etc/nginx/sites-available/abs-stream`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 2000M;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/abs-stream /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. **Setup SSL (Recommended)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

**VPS Advantages:**
- Full control
- Best performance
- No platform limitations
- Scalable
- Cost: $5-10/month

## 🗄️ Database Options

### Local MongoDB
```bash
# Install
sudo apt install mongodb  # Ubuntu/Debian
brew install mongodb-community  # macOS

# Start
mongod --dbpath ./data/db
```

### MongoDB Atlas (Cloud)
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster
3. Whitelist IP: 0.0.0.0/0 (allow all)
4. Create database user
5. Get connection string
6. Use in `MONGO_URI`

## 🔧 Post-Deployment

### 1. Test Bot
```bash
# Check if bot responds
/start in Telegram
```

### 2. Test Web
```bash
# Visit in browser
https://yourdomain.com
```

### 3. Test File Upload
- Upload a file to bot
- Check if links work
- Test stream and download

### 4. Monitor Logs
```bash
# Docker
docker-compose logs -f

# VPS
sudo journalctl -u abs-bot -f
sudo journalctl -u abs-web -f

# Heroku
heroku logs --tail
```

### 5. Setup Monitoring (Optional)
- Use UptimeRobot for uptime monitoring
- Setup error notifications
- Monitor resource usage

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong MongoDB password
- [ ] Enable SSL/HTTPS
- [ ] Set up firewall on VPS
- [ ] Regularly update dependencies
- [ ] Backup database regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables (never commit .env)

## 🐛 Troubleshooting

### Bot Not Starting
```bash
# Check logs
python -m bot.main

# Common issues:
# - Wrong BOT_TOKEN
# - Invalid API_ID/API_HASH
# - MongoDB not running
```

### Web Server Not Accessible
```bash
# Check if running
curl http://localhost:8000

# Check nginx
sudo nginx -t
sudo systemctl status nginx

# Check firewall
sudo ufw allow 80
sudo ufw allow 443
```

### Files Not Streaming
```bash
# Check WEB_URL in .env
# Make sure it matches your domain
# Verify SSL certificate

# Test direct API
curl https://yourdomain.com/api/stream/TOKEN
```

## 📊 Scaling

For high traffic:

1. **Use CDN** (Cloudflare)
2. **Load Balancer** (multiple instances)
3. **Redis Caching** (for session/token data)
4. **S3/Cloud Storage** (for files)
5. **MongoDB Replica Set** (for high availability)
6. **Kubernetes** (for auto-scaling)

## 💰 Cost Estimates

| Platform | Free Tier | Paid |
|----------|-----------|------|
| Heroku | ✅ (sleeps) | $7/mo |
| Railway | $5 credit/mo | $5-20/mo |
| Render | ✅ (sleeps) | $7/mo |
| VPS | ❌ | $5-20/mo |
| MongoDB Atlas | ✅ 512MB | $9/mo |

**Recommended for Production:**
- VPS (DigitalOcean): $10/mo
- MongoDB Atlas: Free tier
- **Total: $10/mo** for unlimited users!

## 🎯 Best Practices

1. **Always use HTTPS** in production
2. **Regular backups** of database
3. **Monitor resource** usage
4. **Update dependencies** regularly
5. **Use environment variables** for secrets
6. **Implement rate limiting** for API
7. **Setup error logging** (Sentry, etc.)
8. **Test before deploying** to production

## 📞 Support

Need help? Check:
- GitHub Issues
- Telegram Support Group
- Documentation

---

**Deploy with confidence! 🔥**
