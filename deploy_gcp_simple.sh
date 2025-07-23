#!/bin/bash
# Simple GCP Deployment Script
# Usage: ./deploy_gcp_simple.sh

set -e

echo "🚀 Starting simple GCP deployment..."

APP_DIR=$(pwd)

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)
echo "📡 Server IP: $SERVER_IP"

# Backend setup
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "📦 Virtual environment already exists"
fi

source venv/bin/activate

# Install dependencies
echo "📦 Installing/updating Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

ENV_FILE="/home/$(whoami)/farm.env"
# Generate secret key and create .env
if [ ! -f "$ENV_FILE" ]; then
    SECRET_KEY=$(python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))")
    
    cat > $ENV_FILE <<EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$SERVER_IP,localhost,127.0.0.1
BID_EXPIRATION_MINUTES=1440
EOF
    echo "✅ Created $ENV_FILE"
else
    echo "✅ Environment file already exists, skipping creation"
fi

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Frontend setup
echo "⚛️ Setting up frontend..."
cd ../ui

# Install dependencies
echo "📦 Installing/updating Node.js dependencies..."
npm install

# Build for production
echo "🔨 Building frontend..."
npm run build

# Create systemd service files
echo "🔧 Creating/updating systemd services..."

# Django service
sudo tee /etc/systemd/system/baseball-django.service > /dev/null <<EOF
[Unit]
Description=Baseball Django Application
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
ExecStart=$APP_DIR/backend/venv/bin/daphne -b 127.0.0.1 -p 8000 farm_system.asgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Celery worker service
sudo tee /etc/systemd/system/baseball-celery-worker.service > /dev/null <<EOF
[Unit]
Description=Baseball Celery Worker
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
ExecStart=$APP_DIR/backend/venv/bin/celery -A farm_system worker --loglevel=info
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Celery beat service
sudo tee /etc/systemd/system/baseball-celery-beat.service > /dev/null <<EOF
[Unit]
Description=Baseball Celery Beat
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
ExecStart=$APP_DIR/backend/venv/bin/celery -A farm_system beat --loglevel=info
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
echo "🌐 Setting up/updating Nginx configuration..."
sudo tee /etc/nginx/sites-available/baseball > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_IP;
    
    # Frontend static files
    location / {
        root $APP_DIR/ui/dist;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Django admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/baseball /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
sudo nginx -t

# Reload systemd and start services
echo "🔄 Starting/restarting services..."
sudo systemctl daemon-reload

# Enable services (idempotent)
sudo systemctl enable baseball-django
sudo systemctl enable baseball-celery-worker
sudo systemctl enable baseball-celery-beat

# Restart services (will start if not running, restart if running)
sudo systemctl restart baseball-django
sudo systemctl restart baseball-celery-worker
sudo systemctl restart baseball-celery-beat

sudo systemctl reload nginx

echo "✅ Deployment completed!"
echo "📝 Your application is available at:"
echo "   Frontend: http://$SERVER_IP"
echo "   API: http://$SERVER_IP/api/"
echo "   Admin: http://$SERVER_IP/admin/"
echo ""
echo "🔧 Service status:"
echo "   Django: $(sudo systemctl is-active baseball-django)"
echo "   Celery Worker: $(sudo systemctl is-active baseball-celery-worker)"
echo "   Celery Beat: $(sudo systemctl is-active baseball-celery-beat)"
echo "   Nginx: $(sudo systemctl is-active nginx)"
echo ""
echo "💡 You can run this script again anytime to update your deployment!" 