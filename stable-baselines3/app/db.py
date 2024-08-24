import psycopg2
from psycopg2 import sql
import os


class StorageConfig:
    def __init__(self):
        storage_type = os.getenv('STORAGE_TYPE', 'in_memory')
        if storage_type == 'in_memory':
            self.actions_storage = InMemoryActionsHistoryStorage()
        elif storage_type == 'postgres':
            self.actions_storage = PostgresActionsHistoryStorage()
        else:
            raise ValueError('Unknown storage type')


class InMemoryActionsHistoryStorage:
    def __init__(self):
        self.storage = []

    def save(self, result):
        self.storage.append(result)

    def load(self):
        return self.storage


class PostgresActionsHistoryStorage:
    def __init__(self):
        db_name = os.getenv('DATABASE_NAME', 'postgres')
        user = os.getenv('DATABASE_USER', 'postgres')
        password = os.getenv('DATABASE_PASSWORD', 'postgres')
        host = os.getenv('DATABASE_HOST', 'postgres')
        port = os.getenv('DATABASE_PORT', 5432)

        self.connection = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.create_table()

    def create_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS actions_history (
                    id SERIAL PRIMARY KEY,
                    status VARCHAR(256) NOT NULL,
                    obs FLOAT[] NOT NULL,
                    action INTEGER NOT NULL,
                    datetime VARCHAR(256) NOT NULL
                );
                '''
            )
            self.connection.commit()

    def save(self, result):
        with self.connection.cursor() as cursor:
            cursor.execute(
                sql.SQL('INSERT INTO actions_history (status, obs, action, datetime) VALUES (%s, %s, %s, %s);'),
                (result['status'], result['obs'], result['action'], result['datetime'])
            )
            self.connection.commit()

    def load(self):
        results = []
        with self.connection.cursor() as cursor:
            cursor.execute(
                sql.SQL('SELECT status, obs, action, datetime FROM actions_history;')
            )
            for row in cursor:
                results.append({
                    'status': row[0],
                    'obs': row[1],
                    'action': row[2],
                    'datetime': row[3]
                })
        return results

    def close(self):
        self.connection.close()

