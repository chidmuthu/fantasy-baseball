# Celery Setup Guide for Baseball Farm System

## What We've Added

### 1. **Automated Bid Expiration**
- ✅ Checks for expired bids every minute
- ✅ Automatically completes expired bids
- ✅ Transfers prospects to winning teams
- ✅ Deducts POM from winning teams

### 2. **Real-time Notifications**
- ✅ WebSocket notifications when bids are placed
- ✅ WebSocket notifications when bids are completed
- ✅ Team-specific notifications for prospect acquisitions

### 3. **Background Task Processing**
- ✅ Celery worker for processing tasks
- ✅ Celery beat scheduler for periodic tasks
- ✅ In-memory message broker and result backend

## Setup Instructions

### Step 1: Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
# No additional system dependencies needed
```

**Windows:**
```bash
# No additional system dependencies needed
```

### Step 2: Start Celery Services

**Option A: Use the helper script (Recommended for development)**
```bash
cd baseball/backend
python start_celery.py
```

**Option B: Start manually (Two terminal windows needed)**

Terminal 1 - Start Celery Worker:
```bash
cd baseball/backend
celery -A farm_system worker --loglevel=info
```

Terminal 2 - Start Celery Beat Scheduler:
```bash
cd baseball/backend
celery -A farm_system beat --loglevel=info
```

### Step 3: Test the Setup

1. **Start your Django server:**
```bash
python manage.py runserver
```

3. **Watch the logs:**
You should see in the Celery worker logs:
```
✅ Automatically completed bid for [Prospect Name] - [Team Name] wins for 10 POM
📢 Sent WebSocket notifications for completed bid: [Prospect Name]
```

## How It Works

### 1. **Scheduled Task: `check_expired_bids`**
- Runs every 30 seconds
- Finds all expired bids (`is_expired=True`)
- Calls `bid.complete_bid()` for each expired bid
- Triggers WebSocket notifications

### 2. **Real-time Notifications**
- **New bids**: Triggered when `place_bid()` is called
- **Completed bids**: Triggered when `check_expired_bids` completes a bid
- **Team updates**: Sent to team-specific WebSocket channels

### 3. **WebSocket Channels**
- `bidding_updates`: General bidding notifications
- `bid_{id}`: Specific bid updates
- `team_{id}`: Team-specific updates

## Configuration Options

### Environment Variables
```bash
# .env file
BID_EXPIRATION_HOURS=24  # or shorter for testing
```

### Development vs Production

**Development:**
- Uses in-memory channel layer for WebSockets
- Uses in-memory broker for Celery
- Short bid expiration for testing

**Production:**
- Uses in-memory channel layer for WebSockets
- Uses in-memory broker for Celery
- Longer bid expiration (24 hours)
- Single server deployment (can scale to multiple servers with Redis later)

## Monitoring

### Check Celery Status
```bash
celery -A farm_system inspect active
celery -A farm_system inspect stats
```

### View Scheduled Tasks
```bash
celery -A farm_system inspect scheduled
```

### Manual Task Execution
```bash
# Check expired bids manually
celery -A farm_system call bidding.tasks.check_expired_bids

# Clean up old bids
celery -A farm_system call bidding.tasks.cleanup_old_bids
```

## Troubleshooting

### Common Issues

1. **Celery Worker Not Starting:**
```bash
# Check if all dependencies are installed
pip install -r requirements.txt

# Check if Django settings are correct
python manage.py check
```

3. **Tasks Not Running:**
```bash
# Check Celery beat scheduler
celery -A farm_system inspect scheduled

# Check worker status
celery -A farm_system inspect active
```

### Logs
- **Celery Worker**: Shows task execution and results
- **Celery Beat**: Shows scheduled task triggers
- **Django**: Shows WebSocket notifications and errors

## Production Deployment

### Using Supervisor (Recommended)
```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A farm_system worker --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A farm_system beat --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

### Using Systemd
Create service files for both worker and beat scheduler.

## Next Steps

1. **Test the setup** with short expiration times
2. **Monitor the logs** to ensure everything works
3. **Adjust bid expiration** for production use
4. **Set up monitoring** for production deployment
5. **Consider Redis** if you need to scale to multiple servers

## Files Created/Modified

- ✅ `farm_system/celery.py` - Celery configuration
- ✅ `farm_system/__init__.py` - Celery app import
- ✅ `bidding/tasks.py` - Background tasks
- ✅ `bidding/models.py` - Added notification triggers
- ✅ `farm_system/settings.py` - Updated channel layers (in-memory)
- ✅ `start_celery.py` - Development helper script
- ✅ `CELERY_SETUP.md` - This guide 