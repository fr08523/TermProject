"""Module to load data into a datastore."""
import requests

from schemas.schema import WeekSchema, BigSeasonSchema
from models.models import Week, BigSeason

OK = 200

class Loader:
    def __init__(self):
        self.week_url = 'https://api.sportradar.com/nfl/official/trial/v7/en/games/current_week/schedule.json?api_key='
        self.season_url = 'https://api.sportradar.com/nfl/official/trial/v7/en/games/current_season/schedule.json?api_key='
        self.api_key = 'u1eEkxdkg5O4xNdtBsfGAg2ihO9fBFm0cY9FnmKQ'
                
    def load_current_week(self) -> Week:
        schema = WeekSchema()
        headers = {"accept": "application/json"}
        url = f'{self.week_url}{self.api_key}'
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        data = response.text
        # TODO: Implement Retry logic
        if status_code == OK:
            data = schema.load(response.json(), partial=True)
            print('Sucessfully loaded week data!')
        else:
            print(f'Failed to load data from {url} with status code: {status_code}')
       
        return data
    
    def load_season(self) -> BigSeason:
        schema = BigSeasonSchema()
        headers = {"accept": "application/json"}
        url = f'{self.season_url}{self.api_key}'
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        if status_code == OK:
            data = schema.load(response.json(), partial=True)
            print('Sucessfully loaded season data!')
        else:
            print(f'Failed to load data from {url} with status code: {status_code}')

        return data
            
        
    