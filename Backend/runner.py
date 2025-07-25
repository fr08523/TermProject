"""Module to run all of the services."""

from services.loader import Loader
from services.transformer import Transformer
from services.persister import Persister

def main():
    loader = Loader()
    week_data = loader.load_current_week()
    season_data = loader.load_season()
    transformer = Transformer()
    transformed_data = transformer.transform(week_data, season_data)
    persister = Persister('sms', '127.0.0.1', 'postgres', '', 5432)
    persister.persist(transformed_data)


if __name__ == '__main__':
    main()