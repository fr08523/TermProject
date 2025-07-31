# Sports Management System - Grader Instructions

## 🏈 Quick Start Guide

This Sports Management System demonstrates a full-stack application with Flask backend and React frontend, showcasing database operations, complex queries, and transactions.

### 📋 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend) 
- **Git** (to clone repository)

### 🚀 Getting Started

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd TermProject
```

#### 2. Start the Backend (Terminal 1)
```bash
cd Backend
./start_backend.sh
```

The script will:
- Create a Python virtual environment
- Install dependencies from requirements.txt  
- Create SQLite database with sample data
- Start Flask server on http://127.0.0.1:5000

#### 3. Start the Frontend (Terminal 2)
```bash
cd Frontend
./start_frontend.sh
```

The script will:
- Install Node.js dependencies
- Create environment configuration
- Start React server on http://localhost:3000

#### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:5000

**Login Credentials:**
- Username: `admin`
- Password: `password123`

---

## 🎯 Key Features to Demonstrate

### 1. 📊 Database Analytics & Complex Queries
Navigate to **Analytics** page to see:
- League statistics with aggregated data
- Team performance rankings
- Player statistics with JOIN operations
- Complex SQL queries with GROUP BY and HAVING clauses

### 2. 🏥 Injury Management (NEW)
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

## 📊 Database Schema Overview

The system includes these main entities:
- **Users**: Authentication system
- **Leagues**: Organization levels (NFL, NCAA, etc.)
- **Teams**: Sports teams with stadiums and coaches
- **Players**: Individual athletes with career statistics
- **Games**: Match records with scores and attendance
- **PlayerGameStats**: Individual performance per game
- **Injuries**: Injury tracking with severity levels (NEW FEATURE)
- **PlayerSalary**: Salary and compensation data

---

## 🧪 Testing Database Operations

### Complex Query Testing
1. Go to Analytics → View team performance (demonstrates complex aggregations)
2. Filter by league or season (demonstrates parameterized queries)
3. View player statistics (demonstrates multi-table JOINs)

### Transaction Testing  
1. Go to Data Management → Bulk Game Stats
2. Add multiple player statistics for a game
3. System ensures all succeed or all fail (ACID compliance)

### Injury Analytics Testing (NEW)
1. Go to Analytics → Injury Report  
2. View injuries sorted by severity
3. Filter by team or active status
4. See injury duration calculations

---

## 🗂️ Sample Data Included

The database initializes with:
- 2 Leagues (NFL, NCAA)
- 3 Teams (Dallas Cowboys, New York Giants, Alabama)
- 5+ Players with career statistics
- 2+ Games with scores and attendance
- Player game statistics
- Salary information
- Sample injury records with different severity levels

---

## 🛠️ Technology Stack

**Backend:**
- Flask (Python web framework)
- SQLAlchemy (ORM for database operations)
- SQLite (Database - easily portable)
- Flask-JWT-Extended (Authentication)
- Flask-CORS (Cross-origin requests)

**Frontend:**
- React 18 (UI framework)
- React Router (Navigation)
- Axios (HTTP client)
- CSS3 (Styling)

---

## 🔧 Manual Setup (Alternative)

If the scripts don't work, follow these manual steps:

### Backend Manual Setup:
```bash
cd Backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py  # Initialize database
python run.py      # Start server
```

### Frontend Manual Setup:
```bash
cd Frontend
npm install
echo "REACT_APP_API_URL=http://127.0.0.1:5000" > .env
npm start
```

---

## 📈 Grading Checklist

- ✅ **Easy Backend Start**: `./start_backend.sh` 
- ✅ **Easy Frontend Start**: `./start_frontend.sh`
- ✅ **Database Queries**: Complex analytics with JOINs and aggregations
- ✅ **Database Transactions**: Bulk operations with proper rollback
- ✅ **Database Updates**: CRUD operations throughout the application
- ✅ **Injury Display**: NEW injury report with severity-based sorting
- ✅ **Enhanced Analytics**: Multiple database insights and reports
- ✅ **Clear Instructions**: This comprehensive guide

---

## ❓ Troubleshooting

**Backend Issues:**
- Ensure Python 3.8+ is installed
- Check if port 5000 is available
- Verify database file permissions

**Frontend Issues:**
- Ensure Node.js 16+ is installed
- Check if port 3000 is available  
- Clear browser cache if needed

**Database Issues:**
- Delete `Backend/instance/sports_management.db` and restart backend to reinitialize
- Check Backend/.env file exists with proper DATABASE_URI

---

## 👨‍💻 Contact

For any issues with setup or demonstration, please check the console output for detailed error messages.