import argparse
import json
import logging
from dataclasses import dataclass

import psycopg2

CREATE = 'create'
DELETE = 'delete'
OPERATION = 'operation'
TABLES = 'tables'

@dataclass
class PostgresDatabaseParams:
    """Database parameters to connect to as postgres database.

    Atrributes:
        database: Name of the database instance to connect to.
        user: Name of the user to connect to the database as.
        host: Hostname of the database.
        password: Password used to connect to the database.
        port: Port number on the host machine.
    """
    database: str
    user: str
    host: str
    password: str
    port: int

class DatabaseScript:
    def __init__(self, params: PostgresDatabaseParams):
                self._client = psycopg2.connect(
                database = params.database,
                user = params.user,
                host = params.host,
                password = params.password,
                port = params.port)
        
    def create_table(self, table_name: str, table_schema: dict[str, str]):
            """Create a table given the table schema.

            Args:
                table_schema: Dictionary of column names to column data types.
            """
            column_definitions = ', '.join(
                [f"{column} {dtype}" for column, dtype in table_schema.items() if column != "constraints"]
            )

            constraints = table_schema.get("constraints")
            if constraints : 
                constraints_definitions = ', '.join(constraints)
                column_definitions += f', {constraints_definitions}'

            query = f'CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})'
            cursor = self._client.cursor()
            cursor.execute(query)
            self._client.commit()

    def close(self):
        """Close the open connection."""
        self._client.close()


    def delete_table(self, table_name: str):
        """Deletes table from database.

        Args:
            table_name: Name of table to delete.
        """
        query = f'DROP TABLE IF EXISTS {table_name}'
        cursor = self._client.cursor()
        cursor.execute(query)
        self._client.commit()

def main():
    """Main execution function."""
    args = parse_args()

    logging.info(f'Starting the script with config file: {args.config_file} and '
        f'databases: {", ".join(args.tables)}')

    # Load the configuration.
    config = load_config(args.config_file)

    # Ensure that the 'operation' keyword is available and valid.
    try:
        operation = config[OPERATION]
    except KeyError:
        raise ValueError('The configuration file is missing the "operation" '
            'key.')

    if operation not in [CREATE, DELETE]:
        raise ValueError('Invalid operation specified. Use "create" or '
            '"delete".')

    # Validate the databases that will be operated on.
    valid_table_names = set(config['tables'])
    if not set(args.tables).issubset(valid_table_names):
        logging.error('Invalid database names specified. Only the following '
            'databases are allowed: %s', ', '.join(valid_table_names))
        return
    
    database_client = DatabaseScript(
            PostgresDatabaseParams(
            database=config['database'],
            user=config['user'],
            host=config['host'],
            port=config['port'],
            password=config['password']
        )
    )
    
    try:
        if operation == 'create':
            for table in args.tables:
                table_schema = config['tables'][table]
                database_client.create_table(table, table_schema)
        elif operation == 'delete':
            for table in args.tables:
                database_client.delete_table(table)
    except Exception as e:
        logging.error(f'An error occurred: {e} while attempting to {operation} '
                     'table(s).')
    finally:
        database_client.close()

def parse_args() -> argparse.Namespace:
    """Command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', help='Path to config file')
    parser.add_argument('--tables', nargs='+', help='Name of tables to operate on')
    parser.add_argument('--log-level', dest='log_level', default='DEBUG', 
                        help='Log level')

    return parser.parse_args()

def load_config(config_file: str):
    """Loads the configuration from a JSON file.

    Args:
        config_file: The path to the configuration file.

    Returns:
        The loaded configuration.
    """
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config

if __name__ == '__main__':
    main()