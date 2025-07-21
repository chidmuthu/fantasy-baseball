# ⚾ Dynasty Baseball Farm System

A full-stack web application for managing a dynasty fantasy baseball league's farm system with real-time bidding on prospects.

## 🏗️ Project Structure

```
baseball/
├── backend/           # Django Python backend
│   ├── requirements.txt
│   ├── manage.py
│   ├── setup.py
│   ├── farm_system/   # Django project settings
│   ├── teams/         # Teams app
│   ├── prospects/     # Prospects app
│   └── bidding/       # Bidding app
├── ui/               # React frontend
│   ├── package.json
│   ├── src/
│   ├── index.html
│   └── vite.config.js
└── TESTING_GUIDE.md  # Testing instructions
```

## 🚀 Quick Start

### 1. Set up the Backend
```bash
cd backend
python3 setup.py
```

### 2. Create Test Data
```bash
cd backend
python manage.py create_test_data --fast-bids
```

### 3. Start the Backend Server
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### 4. Start the Frontend
```bash
cd ui
npm install
npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin

## 🧪 Test Accounts

| Username | Password | Team Name | POM Balance |
|----------|----------|-----------|-------------|
| test_user_1 | testpass123 | Test Team Alpha | 100 |
| test_user_2 | testpass123 | Test Team Beta | 125 |
| test_user_3 | testpass123 | Test Team Gamma | 150 |
| test_user_4 | testpass123 | Test Team Delta | 175 |
| test_user_5 | testpass123 | Test Team Echo | 200 |

## 🎯 Features

- **Team Management**: Create and manage dynasty league teams
- **Prospect Database**: Manual entry of minor league prospects
- **Real-time Bidding**: Live auction system for prospects
- **POM Currency**: Prospect Offer Money system for bidding
- **Automatic Stats Updates**: Nightly updates of MLB appearances from Baseball Reference
- **Eligibility Tracking**: Automatic tracking of prospect eligibility based on MLB stats
- **Admin Interface**: Django admin for league management
- **WebSocket Support**: Real-time updates across browsers

## 🔧 Development

- **Backend**: Django 4.2+ with Django REST Framework
- **Frontend**: React 18+ with Vite
- **Database**: SQLite (development) / PostgreSQL (production)
- **Real-time**: Django Channels with WebSocket support
- **Authentication**: JWT tokens

## 📚 Documentation

- [Testing Guide](TESTING_GUIDE.md) - Comprehensive testing instructions
- [Backend README](backend/README.md) - Backend API documentation
- [UI README](ui/README.md) - Frontend documentation

## 🎮 Testing

For detailed testing instructions, see [TESTING_GUIDE.md](TESTING_GUIDE.md).

## 📝 License

This project is for educational and personal use. 