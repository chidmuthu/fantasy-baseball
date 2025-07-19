# Dynasty Baseball Farm System

A modern web application for managing dynasty fantasy baseball league farm systems with a bidding system for prospects.

## Features

- **Farm System Management**: View all teams and their prospects in an organized interface
- **Bidding System**: Nominate prospects and bid on them with POM (Prospect Offer Money)
- **Team Management**: Add teams and manage their POM balances
- **Real-time Updates**: Automatic bid completion after 24 hours of inactivity
- **Responsive Design**: Works on desktop and mobile devices
- **Local Storage**: Data persists between sessions

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
   ```bash
   cd baseball
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3000`

## Usage

### Farm System Overview
- View all teams and their current prospects
- See POM balances for each team
- Browse prospect details including position, organization, and age

### Bidding System
1. **Select Your Team**: Choose your team from the dropdown menu
2. **Nominate Prospects**: Click "Nominate New Prospect" to create a new bidding auction
   - Minimum starting bid: 5 POM
   - Fill in prospect details (name, position, organization, age, notes)
3. **Place Bids**: On active auctions, enter your bid amount and click "Place Bid"
   - Bids must be whole number increments
   - You cannot bid more than your available POM
   - You cannot outbid yourself
4. **Win Prospects**: If no one tops your bid for 24 hours, you win the prospect

### Team Management
- Add new teams to the league
- Edit POM balances for existing teams
- View team statistics and recent prospects

## Game Rules

- **POM (Prospect Offer Money)**: Each team starts with 100 POM
- **Minimum Bid**: All prospects must start at minimum 5 POM
- **Bidding Increments**: Bids must be whole numbers
- **Auction Duration**: 24 hours from the last bid
- **Winning**: Highest bidder after 24 hours wins the prospect
- **POM Deduction**: Winning bid amount is deducted from team's POM balance

## Technical Details

- **Frontend**: React 18 with Vite
- **State Management**: React Context with useReducer
- **Styling**: Custom CSS with modern design
- **Data Persistence**: Browser localStorage
- **Routing**: React Router v6

## Project Structure

```
src/
├── components/
│   ├── FarmSystem.jsx    # Main farm system overview
│   ├── Bidding.jsx       # Bidding interface
│   └── Teams.jsx         # Team management
├── context/
│   └── FarmContext.jsx   # State management
├── App.jsx               # Main application component
├── main.jsx             # Application entry point
└── index.css            # Global styles
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Customization

### Adding More Teams
Teams can be added through the Teams page or by modifying the initial state in `FarmContext.jsx`.

### Changing POM Rules
Modify the minimum bid amount and starting POM values in the context file.

### Styling
The application uses custom CSS in `src/index.css`. Colors, fonts, and layout can be customized there.

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License. 