import os
import sys
from CouchbaseLite.Database import Database, DatabaseConfiguration
from CouchbaseLite.Collection import Collection

sys.path.append('/home/ihebjeridi/Documents/cbliteFinal/couchbase-lite-python')

DB_PATH = "/home/ihebjeridi/Documents/app - OOP/app_acquisation"
DB_NAME = "AIO_DB"

class DatabaseManager:
    def __init__(self):
        self.db = None
        self.occupants_collection_name = "Occupants"
        self.seats_collection_name = "Seats"
        self.tests_collection_name = "Tests"
        
        if self.database_exists():
            self.db = Database(DB_NAME, DatabaseConfiguration(DB_PATH))
            print(f"Database '{DB_NAME}' already exists.")
        else:
            self.db = Database(DB_NAME, DatabaseConfiguration(DB_PATH))
            print(f"Database '{DB_NAME}' created successfully.")
        
        self.print_scopes()  
        self.scope_name = "_default"
        
        self.occupants_collection = self.create_collection(self.occupants_collection_name)
        self.seats_collection = self.create_collection(self.seats_collection_name)
        self.tests_collection = self.create_collection(self.tests_collection_name)

    def database_exists(self) -> bool:
        db_file_path = os.path.join(DB_PATH, f"{DB_NAME}.cblite2")
        return os.path.exists(db_file_path)
    
    def create_collection(self, collection_name):
        """Create a collection in the database if it does not exist."""
        try:
            collection_names = self.get_collection_names(self.scope_name)
            if collection_name in collection_names:
                print(f"Collection '{collection_name}' already exists.")
                return Collection.get_collection(self.db, collection_name, self.scope_name)  # Return existing collection

            collection = Collection.create_collection(self.db, collection_name, self.scope_name)
            print(f"Collection '{collection_name}' created successfully.")
            return collection
        except Exception as e:
            print(f"Failed to create collection '{collection_name}': {str(e)}")
            return None
        
    def print_scopes(self):
        """Retrieve and print all available scopes in the database."""
        try:
            scope_names = Collection.get_scope_names(self.db)
            print("Scopes in the database:")
            for scope in scope_names:
                print(f" - {scope}")
        except Exception as e:
            print(f"Failed to retrieve scopes: {str(e)}")

    def get_collection_names(self, scope_name) -> list:
        """Retrieve and return all collection names inside the given scope."""
        try:
            return Collection.get_collection_names(self.db, scope_name)
        except Exception as e:
            print(f"Failed to retrieve collection names: {str(e)}")
            return []
        
    def save_document(self, collection, doc):
        """Save a document in the specified collection."""
        try:
            return Collection.save_document(collection, doc)  
        except Exception as e:
            print(f"Failed to save document: {str(e)}")
            raise
