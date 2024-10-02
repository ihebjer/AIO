import os
import sys
sys.path.append('/home/ihebjeridi/Documents/cblite/couchbase-lite-python')

from CouchbaseLite.Database import Database, DatabaseConfiguration

DB_PATH = "/home/ihebjeridi/Documents/app - OOP/app_acquisation"
DB_NAME = "AIO_DB"

class DatabaseManager:
    def __init__(self):
        self.db = None
        if self.database_exists():
            self.db = Database(DB_NAME, DatabaseConfiguration(DB_PATH))
            print(f"Database '{DB_NAME}' already exists.")
        else:
            self.db = Database(DB_NAME, DatabaseConfiguration(DB_PATH))
            print(f"Database '{DB_NAME}' created successfully.")

    def database_exists(self) -> bool:
        db_file_path = os.path.join(DB_PATH, f"{DB_NAME}.cblite2")  
        return os.path.exists(db_file_path)