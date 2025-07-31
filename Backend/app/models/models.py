from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# ---------- auth ----------
class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _pw_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, pw):  # hash on save
        self._pw_hash = generate_password_hash(pw)

    def check_password(self, pw):  # verify on login
        return check_password_hash(self._pw_hash, pw)

    # for /auth/me etc.
    def to_dict(self):
        return {"id": self.id, "username": self.username}

# ---------- core ----------
class League(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    name   = db.Column(db.String(120), unique=True, nullable=False)
    level  = db.Column(db.String(50))    # was sport_type
    teams  = db.relationship("Team", backref="league", lazy=True)

class Team(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    league_id   = db.Column(db.Integer, db.ForeignKey("league.id"), nullable=False)
    home_city   = db.Column(db.String(120))
    head_coach  = db.Column(db.String(120))
    stadium     = db.Column(db.String(120))
    players     = db.relationship("Player", backref="current_team", lazy=True)

class Player(db.Model):
    id                     = db.Column(db.Integer, primary_key=True)
    name                   = db.Column(db.String(120), nullable=False)
    position               = db.Column(db.String(50))
    team_id                = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    career_passing_yards   = db.Column(db.Integer, default=0)
    career_rushing_yards   = db.Column(db.Integer, default=0)
    career_receiving_yards = db.Column(db.Integer, default=0)
    career_tackles         = db.Column(db.Integer, default=0)
    career_sacks           = db.Column(db.Integer, default=0)
    career_interceptions   = db.Column(db.Integer, default=0)
    career_touchdowns      = db.Column(db.Integer, default=0)
    salaries               = db.relationship("PlayerSalary", backref="player", cascade="all, delete-orphan")
    injuries               = db.relationship("Injury", backref="player", cascade="all, delete-orphan")
    stats                  = db.relationship("PlayerGameStats", backref="player", cascade="all, delete-orphan")

class Game(db.Model):   # renamed from Match to match your FD
    id           = db.Column(db.Integer, primary_key=True)
    league_id    = db.Column(db.Integer, db.ForeignKey("league.id"), nullable=False)
    season_year  = db.Column(db.Integer, nullable=False)
    week         = db.Column(db.Integer, nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    venue        = db.Column(db.String(120))
    game_date    = db.Column(db.DateTime, default=datetime.utcnow)
    home_score   = db.Column(db.Integer)
    away_score   = db.Column(db.Integer)
    attendance   = db.Column(db.Integer)
    stats        = db.relationship("PlayerGameStats", backref="game", cascade="all, delete-orphan")

class PlayerGameStats(db.Model):
    player_id         = db.Column(db.Integer, db.ForeignKey("player.id"),   primary_key=True)
    game_id           = db.Column(db.Integer, db.ForeignKey("game.id"),     primary_key=True)
    passing_yards     = db.Column(db.Integer, default=0)
    rushing_yards     = db.Column(db.Integer, default=0)
    receiving_yards   = db.Column(db.Integer, default=0)
    tackles           = db.Column(db.Integer, default=0)
    sacks             = db.Column(db.Integer, default=0)
    interceptions     = db.Column(db.Integer, default=0)
    touchdowns        = db.Column(db.Integer, default=0)
    field_goals_made  = db.Column(db.Integer, default=0)
    extra_points_made = db.Column(db.Integer, default=0)

class Injury(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    player_id   = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    start_date  = db.Column(db.Date)
    end_date    = db.Column(db.Date)
    description = db.Column(db.Text)
    severity    = db.Column(db.String(50))   # added to match your FD

class PlayerSalary(db.Model):
    player_id      = db.Column(db.Integer, db.ForeignKey("player.id"), primary_key=True)
    season_year    = db.Column(db.Integer, primary_key=True)
    base_salary    = db.Column(db.Numeric)
    bonuses        = db.Column(db.Numeric)
    cap_hit        = db.Column(db.Numeric)
    total_comp     = db.Column(db.Numeric)

# ---------- NFL Historical Data Models ----------
class NFLPlayer(db.Model):
    """Enhanced model for NFL players with comprehensive historical data"""
    id                    = db.Column(db.Integer, primary_key=True)
    pfr_id               = db.Column(db.String(50), unique=True)  # Pro Football Reference ID
    name                 = db.Column(db.String(120), nullable=False)
    position             = db.Column(db.String(10))
    current_team         = db.Column(db.String(50))
    birth_date           = db.Column(db.Date)
    college              = db.Column(db.String(100))
    height_inches        = db.Column(db.Integer)
    weight_lbs           = db.Column(db.Integer)
    draft_year           = db.Column(db.Integer)
    draft_round          = db.Column(db.Integer)
    draft_pick           = db.Column(db.Integer)
    career_start         = db.Column(db.Integer)
    career_end           = db.Column(db.Integer)
    active               = db.Column(db.Boolean, default=True)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    season_stats         = db.relationship("NFLPlayerSeasonStats", backref="nfl_player", cascade="all, delete-orphan")
    career_stats         = db.relationship("NFLPlayerCareerStats", backref="nfl_player", cascade="all, delete-orphan")

class NFLPlayerSeasonStats(db.Model):
    """Season-by-season statistics for NFL players"""
    id                    = db.Column(db.Integer, primary_key=True)
    player_id            = db.Column(db.Integer, db.ForeignKey("nfl_player.id"), nullable=False)
    season_year          = db.Column(db.Integer, nullable=False)
    team                 = db.Column(db.String(50))
    position             = db.Column(db.String(10))
    age                  = db.Column(db.Integer)
    games_played         = db.Column(db.Integer, default=0)
    games_started        = db.Column(db.Integer, default=0)
    
    # Passing Stats
    pass_completions     = db.Column(db.Integer, default=0)
    pass_attempts        = db.Column(db.Integer, default=0)
    pass_yards           = db.Column(db.Integer, default=0)
    pass_touchdowns      = db.Column(db.Integer, default=0)
    interceptions        = db.Column(db.Integer, default=0)
    qb_rating            = db.Column(db.Float, default=0.0)
    
    # Rushing Stats
    rush_attempts        = db.Column(db.Integer, default=0)
    rush_yards           = db.Column(db.Integer, default=0)
    rush_touchdowns      = db.Column(db.Integer, default=0)
    rush_long            = db.Column(db.Integer, default=0)
    
    # Receiving Stats
    receptions           = db.Column(db.Integer, default=0)
    receiving_yards      = db.Column(db.Integer, default=0)
    receiving_touchdowns = db.Column(db.Integer, default=0)
    receiving_long       = db.Column(db.Integer, default=0)
    targets              = db.Column(db.Integer, default=0)
    
    # Defensive Stats
    tackles_total        = db.Column(db.Integer, default=0)
    tackles_solo         = db.Column(db.Integer, default=0)
    tackles_assists      = db.Column(db.Integer, default=0)
    sacks                = db.Column(db.Float, default=0.0)
    def_interceptions    = db.Column(db.Integer, default=0)
    forced_fumbles       = db.Column(db.Integer, default=0)
    fumble_recoveries    = db.Column(db.Integer, default=0)
    
    # Special Teams
    field_goals_made     = db.Column(db.Integer, default=0)
    field_goals_attempted = db.Column(db.Integer, default=0)
    extra_points_made    = db.Column(db.Integer, default=0)
    extra_points_attempted = db.Column(db.Integer, default=0)
    
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('player_id', 'season_year', name='unique_player_season'),)

class NFLPlayerCareerStats(db.Model):
    """Career summary statistics for NFL players"""
    player_id            = db.Column(db.Integer, db.ForeignKey("nfl_player.id"), primary_key=True)
    total_seasons        = db.Column(db.Integer, default=0)
    total_games          = db.Column(db.Integer, default=0)
    
    # Career Totals
    career_pass_yards    = db.Column(db.Integer, default=0)
    career_pass_tds      = db.Column(db.Integer, default=0)
    career_rush_yards    = db.Column(db.Integer, default=0)
    career_rush_tds      = db.Column(db.Integer, default=0)
    career_rec_yards     = db.Column(db.Integer, default=0)
    career_rec_tds       = db.Column(db.Integer, default=0)
    career_tackles       = db.Column(db.Integer, default=0)
    career_sacks         = db.Column(db.Float, default=0.0)
    career_interceptions = db.Column(db.Integer, default=0)
    
    # Averages
    avg_yards_per_game   = db.Column(db.Float, default=0.0)
    avg_touchdowns_per_season = db.Column(db.Float, default=0.0)
    
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NFLTeam(db.Model):
    """NFL Team information"""
    id                   = db.Column(db.Integer, primary_key=True)
    name                 = db.Column(db.String(50), unique=True, nullable=False)
    abbreviation         = db.Column(db.String(5), unique=True)
    city                 = db.Column(db.String(50))
    conference           = db.Column(db.String(10))  # AFC/NFC
    division             = db.Column(db.String(20))  # North/South/East/West
    founded_year         = db.Column(db.Integer)
    stadium              = db.Column(db.String(100))
    head_coach           = db.Column(db.String(100))
    colors               = db.Column(db.String(100))
    logo_url             = db.Column(db.String(255))
    
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
