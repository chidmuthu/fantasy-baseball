# Testing Guide for Dynasty Baseball Farm System

This guide will help you test the application with multiple teams and accelerated bidding for development.

## 🏃‍♂️ Quick Start

### 1. Set up the Backend
```bash
cd baseball/backend
python3 setup.py
```

### 2. Create Test Data with Fast Bidding
```bash
# Create test data with 5-minute bid expiration
python manage.py create_test_data --fast-bids

# Or create test data with normal 24-hour expiration
python manage.py create_test_data
```

### 3. Start the Backend Server
```bash
source venv/bin/activate
python manage.py runserver
```

### 4. Start the Frontend
```bash
cd ui  # Go to the UI directory
npm install
npm run dev
```

## 🧪 Test Accounts

The system creates 5 test accounts automatically:

| Username | Password | Team Name | POM Balance |
|----------|----------|-----------|-------------|
| test_user_1 | testpass123 | Test Team Alpha | 100 |
| test_user_2 | testpass123 | Test Team Beta | 125 |
| test_user_3 | testpass123 | Test Team Gamma | 150 |
| test_user_4 | testpass123 | Test Team Delta | 175 |
| test_user_5 | testpass123 | Test Team Echo | 200 |

## 🎯 Testing Scenarios

### Scenario 1: Basic Login and Navigation
1. Open http://localhost:3000
2. Login with `test_user_1` / `testpass123`
3. Navigate between Farm System, Bidding, and Teams pages
4. Verify your team information is displayed correctly

### Scenario 2: Multiple Teams Bidding
1. **Browser 1**: Login as `test_user_1`
2. **Browser 2**: Login as `test_user_2` (or use incognito window)
3. **Browser 3**: Login as `test_user_3` (or use different browser)

**Test Steps:**
1. User 1 nominates a prospect for 5 POM
2. User 2 bids 6 POM
3. User 3 bids 7 POM
4. User 1 bids 8 POM
5. Watch the real-time updates across all browsers

### Scenario 3: Bid Expiration Testing
With fast bidding (5-minute expiration):
1. Create a bid and wait 5 minutes
2. Run the expired bid check:
   ```bash
   python manage.py check_expired_bids
   ```
3. Verify the prospect is transferred to the winning team

### Scenario 4: POM Balance Testing
1. Login as `test_user_1` (100 POM)
2. Try to bid more than your POM balance
3. Verify the system prevents over-bidding
4. Check POM deduction when you win a bid

### Scenario 5: Admin Functions
1. Login to Django admin: http://localhost:8000/admin
2. Use your superuser credentials
3. Test admin functions:
   - Adjust team POM balances
   - Transfer prospects between teams
   - Cancel or complete bids manually

## 🔧 Development Testing Tips

### Accelerated Bidding for Development
To test bid expiration quickly, set the environment variable:
```bash
export BID_EXPIRATION_HOURS=0.083  # 5 minutes
python manage.py runserver
```

### Real-time Testing
1. Open multiple browser windows/tabs
2. Login with different accounts
3. Watch for real-time updates when bids are placed
4. Test WebSocket connections

### Database Reset
To start fresh:
```bash
python manage.py create_test_data --clear --fast-bids
```

### Manual Bid Completion
For testing bid completion without waiting:
```bash
python manage.py check_expired_bids
```

## 🐛 Common Issues and Solutions

### Issue: "Failed to load teams"
**Solution**: Make sure the Django backend is running on port 8000

### Issue: "Authentication failed"
**Solution**: Check that you're using the correct test credentials

### Issue: "Bids not updating in real-time"
**Solution**: 
1. Check WebSocket connections in browser dev tools
2. Verify Django Channels is properly configured
3. Check for CORS issues

### Issue: "Cannot place bid"
**Solution**: 
1. Verify you have sufficient POM
2. Check that the bid is still active
3. Ensure you're not trying to outbid yourself

## 📊 Testing Checklist

- [ ] User registration and login
- [ ] Team creation and management
- [ ] Prospect nomination
- [ ] Bid placement and validation
- [ ] Real-time bid updates
- [ ] POM balance management
- [ ] Bid expiration and completion
- [ ] Prospect transfers
- [ ] Admin functions
- [ ] Error handling
- [ ] Mobile responsiveness

## 🎮 Advanced Testing

### Load Testing
1. Create more test accounts
2. Simulate multiple concurrent bids
3. Test with many active auctions

### Edge Cases
1. Bid exactly at expiration time
2. Try to bid on completed auctions
3. Test with zero POM balance
4. Attempt invalid bid amounts

### Browser Compatibility
Test on:
- Chrome
- Firefox
- Safari
- Edge
- Mobile browsers

## 🔄 Continuous Testing

For ongoing development:
1. Keep the backend running with `python manage.py runserver`
2. Keep the frontend running with `npm run dev`
3. Use the test accounts for quick testing
4. Run `python manage.py check_expired_bids` periodically
5. Monitor the Django admin for data consistency

## 📝 Testing Notes

- Test data is automatically created with realistic prospect names
- Fast bidding mode uses 5-minute expiration instead of 24 hours
- All test accounts start with different POM balances for variety
- The system includes both active and completed bids for testing
- WebSocket connections provide real-time updates across browsers 