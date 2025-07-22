# Production Deployment Guide

## **Cheapest Options (Ranked by Cost)**

### **Option 1: Single VPS - $5-10/month (Recommended)**

**Providers**: DigitalOcean, Linode, Vultr
**Server**: 1GB RAM, 1 CPU, 25GB SSD

#### **What You Need to Run:**

1. **PostgreSQL** - Database (better than SQLite for production)
2. **Django Backend** - API and WebSocket server (with Daphne)
3. **Celery Worker** - Background tasks (bid expiration, stats updates)
4. **Celery Beat** - Scheduled tasks
5. **Nginx** - Reverse proxy and static files
6. **React Frontend** - Built static files served by Nginx

#### **Deployment Steps:**

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# 2. Set up PostgreSQL
sudo -u postgres createuser --interactive
sudo -u postgres createdb baseball_farm

# 3. Clone your code
git clone <your-repo>
cd baseball

# 4. Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with production settings

# 6. Run migrations
python manage.py migrate
python manage.py collectstatic

# 7. Set up process management with Supervisor
sudo apt install supervisor
```

#### **Supervisor Configuration:**

Create `/etc/supervisor/conf.d/baseball.conf`:

```ini
[program:baseball_django]
command=/path/to/baseball/backend/venv/bin/daphne -b 127.0.0.1 -p 8000 farm_system.asgi:application
directory=/path/to/baseball/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/baseball/django.log

[program:baseball_celery_worker]
command=/path/to/baseball/backend/venv/bin/celery -A farm_system worker --loglevel=info
directory=/path/to/baseball/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/baseball/celery_worker.log

[program:baseball_celery_beat]
command=/path/to/baseball/backend/venv/bin/celery -A farm_system beat --loglevel=info
directory=/path/to/baseball/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/baseball/celery_beat.log
```

#### **Nginx Configuration:**

Create `/etc/nginx/sites-available/baseball`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    location / {
        root /path/to/baseball/ui/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Django admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Option 2: Railway/Render - $7-15/month (Easiest)**

**Railway** or **Render** can handle most deployment automatically.

#### **Railway Deployment:**

1. Connect your GitHub repo to Railway
2. Railway will auto-detect Django and deploy
3. Add PostgreSQL service
4. Set environment variables (no Redis needed)

#### **Environment Variables:**

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app
DATABASE_URL=postgresql://user:pass@host:port/db
```

### **Option 3: Heroku - $25-50/month (Most Expensive but Easiest)**

1. Create Heroku app
2. Add PostgreSQL add-on
3. Deploy from Git (no Redis add-on needed)

## **Environment Configuration**

### **Production .env file:**

```bash
# Django
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/baseball_farm

# Production settings
BID_EXPIRATION_MINUTES=1440  # 24 hours
```

## **Frontend Deployment**

### **Build for Production:**

```bash
cd baseball/ui
npm run build
```

### **Deploy Options:**

1. **Same server as backend** - Serve via Nginx
2. **Netlify/Vercel** - Free hosting for static sites
3. **GitHub Pages** - Free hosting

## **Database Migration**

### **SQLite to PostgreSQL:**

```bash
# 1. Install psycopg2
pip install psycopg2-binary

# 2. Update settings.py for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'baseball_farm',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 3. Run migrations
python manage.py migrate
```

## **SSL/HTTPS Setup**

### **Let's Encrypt (Free):**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## **Monitoring and Maintenance**

### **Log Monitoring:**

```bash
# Check Django logs
tail -f /var/log/baseball/django.log

# Check Celery logs
tail -f /var/log/baseball/celery_worker.log
tail -f /var/log/baseball/celery_beat.log

# Check Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **Backup Strategy:**

```bash
# Database backup
pg_dump baseball_farm > backup_$(date +%Y%m%d).sql

# Media files backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz /path/to/media/
```

## **Performance Optimization**

### **For Small Scale (Recommended):**

1. **Use in-memory broker** (already configured):
   ```bash
   # No additional configuration needed
   ```

2. **Reduce Celery workers**:
   ```bash
   celery -A farm_system worker --loglevel=info --concurrency=1
   ```

3. **Use SQLite** if PostgreSQL is too complex (not recommended for production but works for small scale)

### **For Larger Scale:**

1. **Add Redis** for multi-server deployment
2. **Multiple Celery workers**
3. **Load balancing**
4. **CDN for static files**

## **Cost Breakdown**

### **Option 1 (VPS):**
- **Server**: $5-10/month
- **Domain**: $10-15/year
- **Total**: ~$6-11/month

### **Option 2 (Railway/Render):**
- **Platform**: $7-15/month
- **Domain**: $10-15/year
- **Total**: ~$8-16/month

### **Option 3 (Heroku):**
- **Platform**: $25-50/month
- **Domain**: $10-15/year
- **Total**: ~$26-51/month

## **Recommendation**

**For your use case (single server, small scale):**

1. **Start with Option 1 (VPS)** - $5-10/month
2. **Use in-memory broker** (already configured)
3. **Use SQLite** initially (upgrade to PostgreSQL later if needed)
4. **Deploy frontend to Netlify** (free)

**Total cost: ~$5-10/month**

This gives you full control, lowest cost, and room to scale up as needed. 