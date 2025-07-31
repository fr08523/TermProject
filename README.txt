# Sports Management System - Setup and Usage Guide

## 🏈 Quick Start Guide for Graders

This Sports Management System is a full-stack application with Flask backend and React frontend, connected to a publicly accessible PostgreSQL database via ngrok tunneling.

### 📋 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend) 
- **Git** (to clone repository)
- **curl** (for API testing)
- **jq** (for JSON parsing in curl examples)

### 🚀 Getting Started

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd TermProject
```

#### 2. Start the Backend (Terminal 1)
```bash
cd Backend
```

Activate virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the Flask server:
```bash
python run.py
```

The backend will start on http://127.0.0.1:5000

#### 3. Start the Frontend (Terminal 2)
```bash
cd Frontend
npm install
npm start
```

The frontend will start on http://localhost:3000

#### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:5000

**Login Credentials:**
- Username: `admin`
- Password: `admin123`

---

## 🗄️ Database Connection

The system is configured to connect to a remote PostgreSQL database (sportsdb2) via ngrok tunneling. The database is already populated with sample data and publicly accessible for grading purposes. No additional database setup is required.

---

## 📊 Adding Data to Database via API

### Authentication Setup

First, open a terminal, navigate to the Backend directory, ensure your virtual environment is active, and get an authentication token:

```bash
cd Backend
source venv/bin/activate
export TOKEN=$(curl -s -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r .access_token)
```

### Adding New Teams

Add teams that are not already in the database:

```bash
# Add Los Angeles Rams (NFL)
curl -X POST http://127.0.0.1:5000/api/teams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Los Angeles Rams",
    "home_city": "Los Angeles",
    "league_id": 1,
    "head_coach": "Sean McVay",
    "stadium": "SoFi Stadium"
  }'

# Add Kansas City Chiefs (NFL)
curl -X POST http://127.0.0.1:5000/api/teams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Kansas City Chiefs",
    "home_city": "Kansas City",
    "league_id": 1,
    "head_coach": "Andy Reid",
    "stadium": "Arrowhead Stadium"
  }'

# Add Georgia Bulldogs (NCAA)
curl -X POST http://127.0.0.1:5000/api/teams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Georgia Bulldogs",
    "home_city": "Athens",
    "league_id": 2,
    "head_coach": "Kirby Smart",
    "stadium": "Sanford Stadium"
  }'

# Add Ohio State Buckeyes (NCAA)
curl -X POST http://127.0.0.1:5000/api/teams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Ohio State Buckeyes",
    "home_city": "Columbus",
    "league_id": 2,
    "head_coach": "Ryan Day",
    "stadium": "Ohio Stadium"
  }'
```

### Adding New Players

Add players that are not already in the database:

```bash
# Add Patrick Mahomes (Kansas City Chiefs - team_id will be 4 after adding above teams)
curl -X POST http://127.0.0.1:5000/api/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Patrick Mahomes",
    "position": "QB",
    "team_id": 4,
    "career_passing_yards": 28500,
    "career_rushing_yards": 1200,
    "career_touchdowns": 230
  }'

# Add Cooper Kupp (Los Angeles Rams - team_id will be 3)
curl -X POST http://127.0.0.1:5000/api/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Cooper Kupp",
    "position": "WR",
    "team_id": 3,
    "career_receiving_yards": 6800,
    "career_touchdowns": 52
  }'

# Add Aaron Donald (Los Angeles Rams)
curl -X POST http://127.0.0.1:5000/api/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Aaron Donald",
    "position": "DT",
    "team_id": 3,
    "career_sacks": 111,
    "career_tackles": 580
  }'

# Add Stetson Bennett (Georgia Bulldogs - team_id will be 5)
curl -X POST http://127.0.0.1:5000/api/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Stetson Bennett",
    "position": "QB",
    "team_id": 5,
    "career_passing_yards": 8800,
    "career_rushing_yards": 850,
    "career_touchdowns": 85
  }'

# Add C.J. Stroud (Ohio State Buckeyes - team_id will be 6)
curl -X POST http://127.0.0.1:5000/api/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "C.J. Stroud",
    "position": "QB",
    "team_id": 6,
    "career_passing_yards": 8100,
    "career_rushing_yards": 400,
    "career_touchdowns": 85
  }'

# Add Marvin Harrison Jr. (Ohio State Buckeyes)
curl -X POST http://127.0.0.1:5000/api/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Marvin Harrison Jr.",
    "position": "WR",
    "team_id": 6,
    "career_receiving_yards": 2900,
    "career_touchdowns": 31
  }'
```

### Adding New Games

```bash
# Add a game between new teams
curl -X POST http://127.0.0.1:5000/api/games \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "league_id": 1,
    "season_year": 2024,
    "week": 3,
    "home_team_id": 3,
    "away_team_id": 4,
    "venue": "SoFi Stadium",
    "game_date": "2024-09-22T16:00:00",
    "home_score": 24,
    "away_score": 31,
    "attendance": 70000
  }'
```

### Adding Player Game Statistics

```bash
# Add game stats for Patrick Mahomes (assuming game_id 3 from above)
curl -X POST http://127.0.0.1:5000/api/player-game-stats \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "player_id": 6,
    "game_id": 3,
    "passing_yards": 355,
    "touchdowns": 4,
    "interceptions": 0,
    "rushing_yards": 45
  }'
```

### Viewing Data

You can verify the added data using GET requests:

```bash
# List all teams
curl -X GET http://127.0.0.1:5000/api/teams

# List all players
curl -X GET http://127.0.0.1:5000/api/players

# List all games
curl -X GET http://127.0.0.1:5000/api/games

# Get analytics data
curl -X GET http://127.0.0.1:5000/analytics/overview
```

---

## 🎯 Key Features to Demonstrate

### 1. 📊 Database Analytics & Complex Queries
Navigate to **Analytics** page to see:
- League statistics with aggregated data
- Team performance rankings
- Player statistics with JOIN operations
- Complex SQL queries with GROUP BY and HAVING clauses

### 2. 🏥 Injury Management
Navigate to **Injury Report** page to see:
- Complete injury database with severity levels
- Sortable table from highest to lowest severity
- Active vs. recovered injury tracking
- Player and team association

### 3. 🔄 Database Transactions & Updates
Use the **Data Management** page to:
- Bulk insert player game statistics (demonstrates transactions)
- Add new players, teams, games
- Update existing records
- All operations use proper transaction handling with rollback on errors

---

## 📊 Database Schema Overview

The system includes these main entities:
- **Users**: Authentication system
- **Leagues**: Organization levels (NFL, NCAA, etc.)
- **Teams**: Sports teams with stadiums and coaches
- **Players**: Individual athletes with career statistics
- **Games**: Match records with scores and attendance
- **PlayerGameStats**: Individual performance per game
- **Injuries**: Injury tracking with severity levels
- **PlayerSalary**: Salary and compensation data

---

## 🗂️ Existing Sample Data

The database is pre-populated with:
- 2 Leagues (NFL, NCAA)
- 3 Teams (Dallas Cowboys, New York Giants, Alabama Crimson Tide)
- 5 Players with career statistics
- 2 Games with scores and attendance
- Player game statistics
- Sample injury records with different severity levels

---

## 🛠️ Technology Stack

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (ORM for database operations)
- PostgreSQL (Remote database via ngrok)
- Flask-JWT-Extended (Authentication)
- Flask-CORS (Cross-origin requests)

**Frontend:**
- React 18 (UI framework)
- React Router (Navigation)
- Axios (HTTP client)
- CSS3 (Styling)

---

## 🔧 Troubleshooting

**Backend Issues:**
- Ensure Python 3.8+ is installed
- Check if port 5000 is available
- Ensure virtual environment is activated
- Verify .env file exists with correct DATABASE_URI

**Frontend Issues:**
- Ensure Node.js 16+ is installed
- Check if port 3000 is available  
- Clear browser cache if needed
- Verify .env file in Frontend directory

**API Issues:**
- Ensure backend is running before making curl requests
- Check that TOKEN environment variable is set correctly
- Verify Content-Type header is set to application/json

**Database Issues:**
- The database is remotely hosted and should be accessible
- If connection fails, check that ngrok tunnel is active
- Contact system administrator if database is unreachable

---

## 📈 API Endpoints Reference

### Authentication
- `POST /auth/login` - Login and get access token
- `POST /auth/register` - Register new user

### Teams
- `GET /api/teams` - List all teams
- `POST /api/teams` - Create new team (requires auth)

### Players  
- `GET /api/players` - List all players
- `POST /api/players` - Create new player (requires auth)

### Games
- `GET /api/games` - List all games  
- `POST /api/games` - Create new game (requires auth)

### Player Game Stats
- `GET /api/player-game-stats` - List player game statistics
- `POST /api/player-game-stats` - Add player game stats (requires auth)

### Analytics
- `GET /analytics/overview` - Get system overview statistics
- `GET /analytics/teams` - Get team performance analytics
- `GET /analytics/players` - Get player performance analytics