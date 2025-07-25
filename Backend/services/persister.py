"""Module to persist data into the database."""

import psycopg2

from dtos.SportRadarDTO import WeekDTO, GameDTO, SeasonDTO, WeeksDTO, WeatherDTO, VenueDTO
from services.transformer import Transformer

class Persister:
    def __init__(self, database: str, user: str, host: str, 
            password: str, port: int):
        self.database = database
        self.user = user
        self.host = host
        self.password = password
        self.port = port

    def _connect(self, database: str, user: str, host: str, password: str, port: int):
        conn = psycopg2.connect(
            database = database,
            user = user,
            host = host,
            password = password,
            port = port)
        return conn
    
    def persist(self, tuple: tuple[WeekDTO, list[GameDTO], SeasonDTO, list[WeeksDTO], list[WeatherDTO], list[VenueDTO]]):
        week_records = list(Transformer.set_week(self, tuple[0]))
        game_records = list(Transformer.set_game(self, tuple[1]))
        season_records = list(Transformer.set_season(self, tuple[2]))
        weeks_records = list(Transformer.set_weeks(self, tuple[3]))
        weather_records = list(Transformer.set_weather(self, tuple[4]))
        venue_records = list(Transformer.set_venue(self, tuple[5]))
        #TODO: Move the credentials to a config file.
        conn = self._connect('sms', 'collinbrohm', 'localhost', 'godawgs', 5432)
        cursor = conn.cursor()
        # TODO: Clean this up, very nasty. Move to seperate functions?
        try: 
            week_template = 'INSERT INTO week VALUES(%s, %s, %s, %s)'
            cursor.executemany(week_template, week_records)
            conn.commit()
            print('Successfully inserted week data!')
        except Exception as e:
            print(f'Error persisting week data because of: {e}')
        try:
            game_template = 'INSERT INTO game VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.executemany(game_template, game_records)
            conn.commit()
            print('Successfully inserted game data!')
        except Exception as e:
            print(f'Error persisting game data because of: {e}')
        try:
            season_template = 'INSERT INTO season VALUES(%s, %s, %s, %s)'
            cursor.executemany(season_template, season_records)
            conn.commit()
            print('Successfully inserted season data!')
        except Exception as e:
            print(f'Error persisting season data because of: {e}')
        try:
            weeks_template = 'INSERT INTO weeks VALUES(%s, %s, %s, %s)'
            cursor.executemany(weeks_template, weeks_records)
            conn.commit()
            print('Successfully inserted weeks data!')
        except Exception as e:
            print(f'Error persisting weeks data because of: {e}')
        try:
            weather_template = 'INSERT INTO weather VALUES(%s, %s, %s, %s, %s, %s)'
            cursor.executemany(weather_template, weather_records)
            conn.commit()
            print('Successfully inserted weather data!')
        except Exception as e:
            print(f'Error persisting weather data because of: {e}')
        try:
            venue_template = 'INSERT INTO venue VALUES(%s, %s, %s, %s, %s, %s, %s)'
            cursor.executemany(venue_template, venue_records)
            conn.commit()
            print('Successfully inserted venue data!')
        except Exception as e:
            print(f'Error persisting venue data because of: {e}')
            
           
            




        
        
        