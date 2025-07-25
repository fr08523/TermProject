"""Module for transforming data into its DTO"""
from datetime import datetime

from dtos.SportRadarDTO import WeekDTO, GameDTO, SeasonDTO, WeatherDTO, WeeksDTO, VenueDTO
from models.models import Week, BigSeason
from schemas.schema import WeekSchema

# week_entry = tuple[str, str, str]
# game_entry = tuple[str, str, str, datetime, bool, str,
#                        str, str, str, str, str, str, str, str,
#                        str, int, str, str, str, int, int, int]
class Transformer:
    def __init__(self):
        pass

    def transform(self, week_input: Week, season_input: BigSeason) -> tuple[WeekDTO, list[GameDTO], SeasonDTO, list[WeeksDTO], list[WeatherDTO], list[VenueDTO]]:
        """Function to add the incoming data into a WeekDTO which is
        to be inserted. 
        
        Args:
            week_data: The data for the current week of NFL.
            
        Returns:
            request_objects: A datastructure of type WeekDTO containing the values
            to be inserted into PostGres.
        """
        #TODO: list of games inside of week. 
        week_data = WeekDTO(
                season_id=season_input.season.season_id,
                year=week_input.year,
                week_id=week_input.week_id,
                week_num=week_input.week.week_num
                )
        game_data = []
        season_id = season_input.season.season_id
        for game in week_input.week.games:
            if game.scoring is None:
                away_points = 0
                home_points = 0
            else :
                away_points = game.scoring.away_points
                home_points = game.scoring.home_points
            game_dto = GameDTO(
                game_id=game.game_id,
                season_id=season_id,
                week_id=week_data.week_id, 
                status=game.status,
                scheduled=game.scheduled,
                conference_game=game.conference_game,
                venue_id=game.venue.venue_id,
                home_team_id=game.home.home_team_id,
                home_team_name=game.home.home_team_name,
                home_team_abbreviation=game.home.home_team_abbreviation,
                home_team_games_played=game.home.home_team_games_played,
                away_team_id=game.away.away_team_id,
                away_team_name=game.away.away_team_name,
                away_team_abbreviation=game.away.away_team_abbreviation,
                away_team_games_played=game.away.away_team_games_played,
                home_points=home_points,
                away_points=away_points,
                venue_timezone=game.timezone.venue,
                home_timezone=game.timezone.home,
                away_timezone=game.timezone.away,
                broadcast_network=game.broadcast.network
            )
            game_data.append(game_dto)
        season_data = SeasonDTO(
            season_input.season.season_id, season_input.season.year,season_input.season.type, season_input.season.name
        )
        weeks_data = []
        weather_data = []
        venue_data = []
        for week in season_input.weeks:
            week_id = week.week_id
            sequence = week.sequence
            title = week.title
            weeks_dto = WeeksDTO(
                season_id, week_id, sequence, title
            )
            weeks_data.append(weeks_dto)
            for game in week.games:
                game_id = game.game_id
                if game.broadcast is None:
                    broadcast_network = 'Unavailable'
                else:
                    broadcast_network = game.broadcast.network
                game_dto2 = GameDTO(
                    game_id=game.game_id,
                    season_id=season_id,
                    week_id=week_data.week_id, 
                    status=game.status,
                    scheduled=game.scheduled,
                    conference_game=game.conference_game,
                    venue_id=game.venue.venue_id,
                    home_team_id=game.home.home_team_id,
                    home_team_name=game.home.home_team_name,
                    home_team_abbreviation=game.home.home_team_abbreviation,
                    home_team_games_played=game.home.home_team_games_played,
                    away_team_id=game.away.away_team_id,
                    away_team_name=game.away.away_team_name,
                    away_team_abbreviation=game.away.away_team_abbreviation,
                    away_team_games_played=game.away.away_team_games_played,
                    home_points=home_points,
                    away_points=away_points,
                    venue_timezone=game.timezone.venue,
                    home_timezone=game.timezone.home,
                    away_timezone=game.timezone.away,
                    broadcast_network=broadcast_network
                    )
                game_data.append(game_dto2)
                if game.weather:
                    condition = game.weather.condition
                    humidity = game.weather.humidity
                    temp = game.weather.temp
                    wind_speed = game.weather.wind.speed
                    wind_direction = game.weather.wind.direction
                    weather_dto = WeatherDTO(game_id, condition, humidity, temp, 
                                            wind_speed, wind_direction 
                    )
                venue_id = game.venue.venue_id
                venue_name = game.venue.name
                venue_city = game.venue.city
                venue_state = game.venue.state
                venue_country = game.venue.country
                surface = game.venue.surface
                roof_type = game.venue.roof_type
                venue_dto = VenueDTO(venue_id, venue_name, venue_city, venue_state, venue_country, surface, roof_type)
                weather_data.append(weather_dto)
                venue_data.append(venue_dto)
        print('Sucessfully transformed data!')
        
        return week_data, game_data, season_data, weeks_data, weather_data, venue_data
        
    
    def set_week(self, week: WeekDTO):
        records: set[tuple] = set()
        records.add(
                (
                    week.season_id,
                    week.year,
                    week.week_id,
                    week.week_num,
                ))
        return records
    
    def set_game(self, games: list[GameDTO]) -> set[tuple]:
        records: set[tuple] = set()
        for game in games: 
            records.add(
                (
                    game.game_id,
                    game.season_id,
                    game.week_id,
                    game.status,
                    game.scheduled,
                    game.conference_game,
                    game.venue_id,
                    game.home_team_id,
                    game.home_team_name,
                    game.home_team_abbreviation,
                    game.home_team_games_played,
                    game.away_team_id,
                    game.away_team_name,
                    game.away_team_abbreviation,
                    game.away_team_games_played,
                    game.venue_timezone,
                    game.home_timezone,
                    game.away_timezone,
                    game.broadcast_network,
                    game.home_points,
                    game.away_points
                    )
                )

        return records
        

    def set_season(self, season: SeasonDTO) -> set[tuple]:
        records: set[tuple] = set()
        records.add((season.season_id, season.year, season.type, season.name))

        return records
    
    def set_weeks(self, weeks: list[WeeksDTO]) -> set[tuple]:
        records: set[tuple] = set()
        for week in weeks:
            records.add((week.season_id, week.week_id, week.sequence, week.title))

        return records
    
    def set_weather(self, weathers: list[WeatherDTO]) -> set[tuple]:
        records: set[tuple] = set()
        for weather in weathers:
            records.add((weather.game_id, weather.condition, weather.humidity, weather.temp,
                      weather.wind_speed, weather.wind_direction))
            
        return records

    def set_venue(self, venues: list[VenueDTO]) -> set[tuple]:
        records: set[tuple] = set()
        for venue in venues:
            records.add((venue.venue_id, venue.venue_name, venue.venue_city, 
                        venue.venue_state, venue.venue_country, 
                        venue.surface, venue.roof_type))
            
        return records
    