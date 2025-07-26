"""Module containing models for incoming data from SportRadar."""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }


@dataclass(frozen=True)
class Scoring:
    home_points: Optional[int] = None
    away_points: Optional[int] = None

@dataclass(frozen=True)
class Away:
    away_team_id: str
    away_team_name: str
    away_team_abbreviation: str
    away_team_games_played: int

@dataclass(frozen=True)
class Home:
    home_team_id: str
    home_team_name: str
    home_team_abbreviation: str
    home_team_games_played: int

@dataclass(frozen=True)
class Venue:
    venue_id: str
    name: str
    city: str
    country: str
    surface: str
    roof_type: str
    state: Optional[str] = None

@dataclass(frozen=True)
class Wind:
    speed: int
    direction: Optional[str] = None

@dataclass(frozen=True)
class Weather:
    humidity: int
    temp: int
    wind: Optional[Wind]
    condition: Optional[str] = None

@dataclass(frozen=True)
class Timezone:
    venue: Optional[str]
    home: Optional[str]
    away: Optional[str]

@dataclass(frozen=True)
class Broadcast:
    network: str

@dataclass(frozen=True)
class Games:
    """Main dataclass."""
    game_id: str
    status: str
    scheduled: datetime
    conference_game: bool
    venue: Venue
    home: Home
    away: Away
    broadcast: Optional[Broadcast] = None
    timezone: Optional[Timezone] = None
    weather: Optional[Weather] = None
    scoring: Optional[Scoring] = None

@dataclass(frozen=True)
class InnerWeek:
    week_num: str  # inside week title
    games: list[Games]

@dataclass(frozen=True)
class Week:
    week_id: str
    year: str
    week: InnerWeek

@dataclass(frozen=True)
class Weeks:
    week_id: str
    sequence: int
    title: str
    games: list[Games]

@dataclass(frozen=True)
class Season:
    season_id: str
    year: int
    type: str
    name: str 


@dataclass
class BigSeason:
    season: Season
    weeks: list[Weeks]