# Dynasty Baseball Farm System - Django Backend

A Django-based backend API for managing dynasty fantasy baseball league farm systems with real-time bidding functionality.

## Features

- **User Authentication**: JWT-based authentication with user registration
- **Team Management**: Create and manage teams with POM balances
- **Prospect Management**: Manual prospect entry with team ownership
- **Bidding System**: Real-time bidding with 24-hour auction windows
- **Automatic Stats Updates**: Nightly updates of MLB appearances from Baseball Reference
- **Eligibility Tracking**: Automatic tracking of prospect eligibility based on MLB stats
- **Admin Interface**: Comprehensive Django admin for league management
- **Real-time Updates**: WebSocket support for live bidding notifications
- **API-first Design**: RESTful API ready for web and mobile clients

## Technology Stack

- **Django 4.2.7**: Web framework
- **Django REST Framework**: API framework
- **Django Channels**: WebSocket support
- **JWT Authentication**: Secure token-based auth
- **SQLite/PostgreSQL**: Database (SQLite for development, PostgreSQL for production)
- **Redis**: Message broker for Celery and Channels
- **Celery**: Background task processing

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Installation

1. **Clone and navigate to the backend directory:**
   ```bash
   cd baseball/backend
   ```

2. **Run the setup script:**
   ```bash
   python3 setup.py
   ```
   
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Run database migrations
   - Create a superuser account
   - Set up the initial database

3. **Start the development server:**
   ```bash
   # Activate virtual environment
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Start server
   python manage.py runserver
   ```

4. **Access the application:**
   - Admin interface: http://localhost:8000/admin
   - API root: http://localhost:8000/api/

## API Endpoints

### Authentication
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/register/` - Register new user and team

### Teams
- `GET /api/teams/` - List teams (filtered by permissions)
- `GET /api/teams/my_team/` - Get current user's team
- `POST /api/teams/{id}/adjust_pom/` - Adjust team POM (admin only)

### Prospects
- `GET /api/prospects/` - List prospects (filtered by permissions)
- `GET /api/prospects/my_prospects/` - Get user's team prospects
- `GET /api/prospects/available/` - Get available prospects for bidding
- `POST /api/prospects/` - Create new prospect
- `PUT /api/prospects/{id}/` - Update prospect
- `POST /api/prospects/{id}/transfer/` - Transfer prospect (admin only)
- `POST /api/prospects/{id}/release/` - Release prospect from team
- `POST /api/prospects/{id}/tag/` - Tag prospect to extend eligibility
- `POST /api/prospects/{id}/update_stats/` - Update prospect MLB stats from external sources

### Bidding
- `GET /api/bids/` - List bids (filtered by permissions)
- `GET /api/bids/active/` - Get active bids
- `GET /api/bids/my_bids/` - Get user's nominated bids
- `GET /api/bids/my_winning/` - Get bids user is currently winning
- `POST /api/bids/` - Create new bid (nominate prospect)
- `POST /api/bids/{id}/place_bid/` - Place bid on auction
- `POST /api/bids/{id}/complete/` - Manually complete bid (admin only)
- `POST /api/bids/{id}/cancel/` - Cancel bid (admin only)
- `POST /api/bids/check_expired/` - Check and complete expired bids (admin only)

## WebSocket Endpoints

- `ws://localhost:8000/ws/bidding/` - General bidding updates
- `ws://localhost:8000/ws/team/` - Team-specific updates

## Database Models

### Team
- `name`: Team name
- `owner`: One-to-one relationship with User
- `pom_balance`: Prospect Offer Money balance
- `created_at`, `updated_at`: Timestamps

### Prospect
- `name`: Prospect name
- `position`: Baseball position (P, C, 1B, 2B, 3B, SS, OF, UTIL)
- `organization`: MLB team organization
- `age`: Prospect age
- `notes`: Optional notes
- `team`: Foreign key to Team (null if available)
- `created_by`: Team that created the prospect
- `acquired_at`: When prospect was acquired by team

### Bid
- `prospect`: Foreign key to Prospect
- `nominator`: Team that nominated the prospect
- `current_bidder`: Team currently winning the bid
- `starting_bid`: Initial bid amount
- `current_bid`: Current highest bid
- `status`: active, completed, or cancelled
- `created_at`, `last_bid_time`, `completed_at`: Timestamps

### BidHistory
- `bid`: Foreign key to Bid
- `team`: Team that placed the bid
- `amount`: Bid amount
- `bid_time`: When the bid was placed

## Admin Interface

The Django admin interface provides comprehensive management capabilities:

### Team Management
- View all teams and their POM balances
- Adjust POM balances
- View prospect counts
- Manage team owners

### Prospect Management
- View all prospects across all teams
- Transfer prospects between teams
- Edit prospect information
- Track prospect creation and acquisition

### Bid Management
- View all active and completed bids
- Manually complete or cancel bids
- View bid history
- Bulk actions for bid management
## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Shell Access
```bash
python manage.py shell
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

## Production Deployment

### Environment Variables
Create a `.env` file with:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Database
For production, use PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Static Files
```bash
python manage.py collectstatic
```

### WebSocket Support
For production WebSocket support, use Daphne or uvicorn with ASGI.

## Security Considerations

- JWT tokens expire after 24 hours
- All API endpoints require authentication
- Team owners can only manage their own data
- Admin users have full system access
- POM balances are validated before transactions
- Bid amounts must be whole numbers and higher than current bid

## API Authentication

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is open source and available under the MIT License. 