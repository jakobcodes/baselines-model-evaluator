from actions import InMemoryActionsHistoryStorage, PostgresActionsHistoryStorage
from policies import InMemoryPolicyHistoryStorage, PostgresPolicyHistoryStorage
import os


def _load_db_config():
    db_name = os.getenv('DATABASE_NAME', 'postgres')
    user = os.getenv('DATABASE_USER', 'postgres')
    password = os.getenv('DATABASE_PASSWORD', 'postgres')
    host = os.getenv('DATABASE_HOST', 'postgres')
    port = os.getenv('DATABASE_PORT', 5432)
    return db_name, user, password, host, port


class StorageConfig:
    def __init__(self):
        storage_type = os.getenv('STORAGE_TYPE', 'in_memory')
        if storage_type == 'in_memory':
            self.actions_storage = InMemoryActionsHistoryStorage()
            self.policy_history_storage = InMemoryPolicyHistoryStorage()
        elif storage_type == 'postgres':
            db_name, user, password, host, port = _load_db_config()
            self.actions_storage = PostgresActionsHistoryStorage(db_name, user, password, host, port)
            self.policy_history_storage = PostgresPolicyHistoryStorage(db_name, user, password, host, port)
        else:
            raise ValueError('Unknown storage type')

