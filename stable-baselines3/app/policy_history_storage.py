import psycopg2
from psycopg2 import sql
import datetime as dt


class InMemoryPolicyHistoryStorage:
    def __init__(self):
        self.storage = []

    def save(self, policy_name):
        self.storage.append({
            'policy_name': policy_name,
            'datetime': dt.datetime.now().isoformat()
        })

    def load(self):
        return self.storage


class PostgresPolicyHistoryStorage:
    def __init__(self, db_name, user, password, host, port):
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
                CREATE TABLE IF NOT EXISTS policy_history (
                    id SERIAL PRIMARY KEY,
                    policy_name VARCHAR(256) NOT NULL,
                    datetime VARCHAR(256) NOT NULL
                );
                '''
            )
            self.connection.commit()

    def save(self, policy_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                sql.SQL('INSERT INTO policy_history (policy_name, datetime) VALUES (%s, %s);'),
                (policy_name, dt.datetime.now().isoformat())
            )
            self.connection.commit()

    def load(self):
        results = []
        with self.connection.cursor() as cursor:
            cursor.execute(
                sql.SQL('SELECT policy_name, datetime FROM policy_history;')
            )
            for row in cursor:
                results.append({
                    'policy_name': row[0],
                    'datetime': row[1]
                })
        return results

    def close(self):
        self.connection.close()