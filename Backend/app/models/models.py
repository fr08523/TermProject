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
