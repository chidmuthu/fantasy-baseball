#!/bin/bash
# Check Django logs script
# Usage: ./check_logs.sh [lines]

LINES=${1:-50}

echo "📋 Checking Django logs (last $LINES lines):"
echo "=============================================="

# Check Django service logs
echo "🔧 Django Service Logs:"
sudo journalctl -u baseball-django --no-pager -n $LINES

echo ""
echo "📄 Django File Logs:"
if [ -f "/var/log/baseball/django.log" ]; then
    tail -n $LINES /var/log/baseball/django.log
else
    echo "No Django log file found at /var/log/baseball/django.log"
fi

echo ""
echo "🌐 Nginx Access Logs:"
sudo tail -n $LINES /var/log/nginx/access.log

echo ""
echo "❌ Nginx Error Logs:"
sudo tail -n $LINES /var/log/nginx/error.log 