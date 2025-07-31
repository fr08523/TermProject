# Sports Management System - Final Submission

This Sports Management System is a full-stack application with a Flask backend and React frontend, demonstrating comprehensive database operations, complex queries, and transactions.

## 🌐 Option 1: Using Neon Database (Recommended for Graders)

The application is configured to use a hosted PostgreSQL database on Neon for easy grader access.

### Quick Start with Neon Database

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TermProject
   ```

2. **Start the Backend (Terminal 1)**
   ```bash
   cd Backend
   ./start_backend.sh
   ```
   The backend will automatically connect to the Neon-hosted database.

3. **Start the Frontend (Terminal 2)**
   ```bash
   cd Frontend
   ./start_frontend.sh
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://127.0.0.1:5000

5. **Login Credentials**
   - Username: `admin`
   - Password: `password123`

### How Neon Integration Works

The `.env` file in the `Backend/` directory contains:
```
SECRET_KEY=Password
DATABASE_URI=postgresql://neondb_owner:npg_g56YLHZFoWXn@ep-wild-violet-aevhv2hk-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

When you run `python run.py`, Flask reads this `.env` file and connects directly to the Neon-hosted PostgreSQL database. All API endpoints (`/api/players`, `/api/teams`, `/analytics/...`) fetch data live from Neon.

---

## 💻 Option 2: Local Database Setup

For development or if you prefer to run locally with sample data:

### Prerequisites
- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)

### Setup Instructions

1. **Configure for Local Database**
   
   Edit `Backend/.env` and comment out the Neon DATABASE_URI, then uncomment the local SQLite line:
   ```
   SECRET_KEY=Password
   # DATABASE_URI=postgresql://neondb_owner:npg_g56YLHZFoWXn@ep-wild-violet-aevhv2hk-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   DATABASE_URI=sqlite:///instance/sports_management.db
   ```

2. **Start the Backend**
   ```bash
   cd Backend
   ./start_backend.sh
   ```
   The script will create a local SQLite database with sample data.

3. **Start the Frontend**
   ```bash
   cd Frontend
   ./start_frontend.sh
   ```

### Adding Data to Local Database

#### Authentication Process

1. **Create a user account** (first-time setup):
   ```bash
   curl -X POST http://127.0.0.1:5000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpass123"}'
   ```

2. **Get authentication token**:
   ```bash
   curl -X POST http://127.0.0.1:5000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password123"}'
   ```
   
   This returns a JWT token like:
   ```json
   {"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
   ```

3. **Use the token for authenticated requests**:
   Replace `YOUR_TOKEN_HERE` with the actual token from step 2.

#### Adding Sample Teams

**Team 1: Kansas City Chiefs**
```bash
curl -X POST http://127.0.0.1:5000/api/teams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Kansas City Chiefs",
    "home_city": "Kansas City",
    "league_id": 1,
    "head_coach": "Andy Reid",
    "stadium": "Arrowhead Stadium"
  }'
```

**Team 2: San Francisco 49ers**
```bash
curl -X POST http://127.0.0.1:5000/api/teams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "San Francisco 49ers",
    "home_city": "San Francisco",
    "league_id": 1,
    "head_coach": "Kyle Shanahan",
    "stadium": "Levi's Stadium"
  }'
```

#### Adding Sample Players

**Player 1: Patrick Mahomes (for Chiefs - assuming team_id 4)**
```bash
curl -X POST http://127.0.0.1:5000/api/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Patrick Mahomes",
    "position": "QB",
    "team_id": 4,
    "career_passing_yards": 28424,
    "career_rushing_yards": 1478,
    "career_touchdowns": 219
  }'
```

**Player 2: Brock Purdy (for 49ers - assuming team_id 5)**
```bash
curl -X POST http://127.0.0.1:5000/api/players \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Brock Purdy",
    "position": "QB",
    "team_id": 5,
    "career_passing_yards": 4280,
    "career_rushing_yards": 144,
    "career_touchdowns": 31
  }'
```

#### Viewing Data

**Get all teams:**
```bash
curl -X GET http://127.0.0.1:5000/api/teams \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Get all players:**
```bash
curl -X GET http://127.0.0.1:5000/api/players \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🎯 Key Features Demonstrated

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

### 4. 🔍 Advanced Database Queries
The system demonstrates:
- **Complex JOINs**: Player stats with team and league data
- **Aggregations**: Win/loss ratios, average statistics
- **Subqueries**: Team performance calculations
- **SQL Injection Prevention**: Parameterized queries throughout

---

## 🗂️ Database Schema

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

## 🛠️ Technology Stack

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (ORM for database operations)
- PostgreSQL/SQLite (Database)
- Flask-JWT-Extended (Authentication)
- Flask-CORS (Cross-origin requests)

**Frontend:**
- React 18 (UI framework)
- React Router (Navigation)
- Axios (HTTP client)
- CSS3 (Styling)

---

## 📈 Grading Checklist

- ✅ **Neon Database Setup**: Automatic connection via .env file
- ✅ **Easy Backend Start**: `./start_backend.sh`
- ✅ **Easy Frontend Start**: `./start_frontend.sh`
- ✅ **Database Queries**: Complex analytics with JOINs and aggregations
- ✅ **Database Transactions**: Bulk operations with proper rollback
- ✅ **Database Updates**: CRUD operations throughout the application
- ✅ **Injury Display**: Injury report with severity-based sorting
- ✅ **Enhanced Analytics**: Multiple database insights and reports
- ✅ **Authentication**: JWT-based API security
- ✅ **Comprehensive Documentation**: This README with both setups

---

## ❓ Troubleshooting

**Backend Issues:**
- Ensure Python 3.8+ is installed
- Check if port 5000 is available
- For local setup: Verify `Backend/.env` file exists with proper DATABASE_URI

**Frontend Issues:**
- Ensure Node.js 16+ is installed
- Check if port 3000 is available
- Clear browser cache if needed

**Database Issues:**
- **Neon**: Connection issues may be due to network - this is expected in restricted environments
- **Local**: Delete `Backend/instance/sports_management.db` and restart backend to reinitialize

**Authentication Issues:**
- Ensure you're using the correct token in the Authorization header
- Tokens expire after some time - get a new token if requests fail

---

## 🚀 Quick Commands Summary

**Neon Database (Recommended):**
```bash
cd Backend && ./start_backend.sh
cd Frontend && ./start_frontend.sh
# Access: http://localhost:3000
```

**Local Database:**
```bash
# Edit Backend/.env to use SQLite
cd Backend && ./start_backend.sh
cd Frontend && ./start_frontend.sh
# Access: http://localhost:3000
```

**API Testing:**
```bash
# Get token
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}' | jq -r '.access_token')

# Test API
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/teams
```