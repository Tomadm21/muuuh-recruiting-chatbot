# Deployment Guide

This guide covers deployment options for the muuh WhatsApp Recruiting Chatbot.

## 🚂 Railway.app (Recommended)

Railway provides the simplest deployment path with automatic HTTPS and webhook support.

### Prerequisites
- GitHub account
- Railway account (free tier available)
- Twilio account configured

### Steps

1. **Prepare Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo>
   git push -u origin main
   ```

2. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway and select your repository

3. **Configure Environment Variables**
   
   In Railway dashboard, go to Variables tab and add:
   ```
   OPENAI_API_KEY=sk-...
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   DATABASE_URL=sqlite:///./muuh_chatbot.db
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   HR_EMAIL=recruiting@muuuh.de
   ```

4. **Deploy**
   - Railway will automatically detect Python and deploy
   - Note your deployment URL (e.g., `https://your-app.railway.app`)

5. **Configure Twilio Webhook**
   - Go to Twilio Console → WhatsApp Sandbox Settings
   - Set webhook URL to: `https://your-app.railway.app/webhook`
   - Method: `POST`
   - Save

6. **Test**
   - Send message to your Twilio WhatsApp number
   - Check Railway logs for incoming requests
   - Verify bot responds correctly

### Railway Configuration File

Create `railway.json` in project root:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `Procfile` (optional):
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🎨 Render.com

Alternative deployment platform with free tier.

### Steps

1. **Create Account**
   - Sign up at [render.com](https://render.com)

2. **New Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Configure:
     - **Name**: muuh-recruiting-chatbot
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   
   Add all variables from `.env.example` in Environment tab

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment
   - Note your URL (e.g., `https://muuh-recruiting-chatbot.onrender.com`)

5. **Configure Twilio**
   - Same as Railway: Set webhook to your Render URL + `/webhook`

---

## 🐳 Docker Deployment

For custom hosting or local development.

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Initialize database
RUN python scripts/setup_db.py

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - TWILIO_WHATSAPP_NUMBER=${TWILIO_WHATSAPP_NUMBER}
      - DATABASE_URL=sqlite:///./muuh_chatbot.db
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./muuh_chatbot.db:/app/muuh_chatbot.db
    restart: unless-stopped
```

### Deploy

```bash
# Build image
docker build -t muuh-chatbot .

# Run container
docker run -d -p 8000:8000 --env-file .env muuh-chatbot

# Or use docker-compose
docker-compose up -d
```

---

## 🔐 Production Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Database initialized
- [ ] Twilio webhook configured and verified
- [ ] HTTPS enabled (automatic with Railway/Render)
- [ ] Logs configured and monitored
- [ ] Error handling tested
- [ ] Rate limiting considered (future improvement)
- [ ] Backup strategy for database (if using SQLite in production)

---

## 🔄 Database Migration (SQLite → PostgreSQL)

For production at scale, migrate to PostgreSQL:

1. **Update DATABASE_URL**:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

2. **Update requirements.txt**:
   ```
   psycopg2-binary==2.9.9
   ```

3. **No code changes needed** - SQLAlchemy handles dialects

4. **Migrate data**:
   ```bash
   # Export from SQLite
   sqlite3 muuh_chatbot.db .dump > backup.sql
   
   # Import to PostgreSQL (manual cleanup may be needed)
   psql -U user -d dbname -f backup.sql
   ```

---

## 📊 Monitoring

### Railway Logs
```bash
railway logs --tail
```

### Render Logs
View in dashboard or:
```bash
render logs
```

### Health Checks
- Endpoint: `https://your-app.com/health`
- Set up external monitoring (UptimeRobot, etc.)

---

## 🆘 Troubleshooting

### Webhook not receiving messages
- Verify Twilio webhook URL is correct
- Check HTTPS (required by Twilio)
- Verify app is running: `GET /health`
- Check firewall rules

### Database errors
- Ensure database file is writable
- For PostgreSQL: verify connection string
- Check Railway/Render logs for permission errors

### OpenAI API errors
- Verify API key is valid
- Check billing/usage limits
- Review rate limits

### Twilio errors
- Verify account is active
- Check WhatsApp sandbox approval
- Review Twilio debugger logs

---

## 🔒 Security Best Practices

1. **Never commit `.env` file**
2. **Validate Twilio webhook signatures** (implemented)
3. **Use environment variables for secrets**
4. **Enable HTTPS** (automatic with Railway/Render)
5. **Implement rate limiting** (future improvement)
6. **Regular dependency updates**
7. **Monitor logs for suspicious activity**

---

## 📈 Scaling Considerations

For high traffic:

1. **Use PostgreSQL** instead of SQLite
2. **Add Redis** for conversation state (instead of in-memory)
3. **Horizontal scaling** - multiple app instances
4. **Queue system** for async processing (Celery + RabbitMQ)
5. **CDN** for static assets
6. **Load balancer** for traffic distribution

---

**Need help?** Check Railway/Render documentation or Twilio support.
