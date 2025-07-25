"""Module containing data that are to be inserted into a database."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# TODO: Refactor at a later point with seperate tables. For now they will all go 
# into one. 
@dataclass
class WeekDTO:
    season_id: str # FK TO SEASON
    year: str
    week_id: str # PK
    week_num: str 

@dataclass
class GameDTO:
    game_id: str # PK
    season_id: str # FK TO SEASON
    week_id: str # FK TO WEEK
    status: str
    scheduled: datetime
    conference_game: bool
    venue_id: str # FK TO VENUE
    home_team_id: str # NOTE: I could seperate to different tables, but games played changes
    home_team_name: str
    home_team_abbreviation: str
    home_team_games_played: int
    away_team_id: str
    away_team_name: str
    away_team_abbreviation: str
    away_team_games_played: int
    venue_timezone: Optional[str]
    home_timezone: Optional[str]
    away_timezone: Optional[str]
    broadcast_network: Optional[str]
    home_points: Optional[int] = None
    away_points: Optional[int] = None

@dataclass
class VenueDTO:
    venue_id: str # PK TO VENUE
    venue_name: str
    venue_city: str
    venue_state: str
    venue_country: str
    surface: str
    roof_type: str
    
@dataclass
class WeatherDTO:
    game_id: str # FK TO GAME
    condition: str
    humidity: int
    temp: int
    wind_speed: int
    wind_direction: Optional[str]

@dataclass 
class WeeksDTO:
    season_id: str # FK TO SEASON
    week_id: str # PK
    sequence: int
    title: str
    
@dataclass
class SeasonDTO:
    season_id: str # PK
    year: int
    type: str
    name: str