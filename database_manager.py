import os
import sys
import yaml

config_file_path = "config.yaml"
with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)
sys.path.append(config['sys']['path'])

from CouchbaseLite.Database import Database, DatabaseConfiguration
from CouchbaseLite.Collection import Collection

DB_PATH = config['db_path']
DB_NAME = config['db_name']
SCOPE_NAME = config['scope_name']
COLLECTIONS = config['collections']

class DatabaseManager:
    def __init__(self):
        self.db = None
        self.occupants_collection_name = COLLECTIONS['occupants']
        self.seats_collection_name = COLLECTIONS['seats']
        self.tests_collection_name = COLLECTIONS['tests']
        
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
                return self.get_collection(collection_name)  

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

    def get_collection(self, collection_name):
        """
        Retrieve a collection from the database by name and scope.
        :param collection_name: Name of the collection to retrieve.
        :return: The collection if found.
        """
        try:
            return Collection.get_collection(self.db, collection_name, self.scope_name)
        except Exception as e:
            raise ValueError(f"Error retrieving collection '{collection_name}': {str(e)}")

    def save_document(self, collection, doc):
        """Save a document in the specified collection."""
        try:
            return Collection.save_document(collection, doc)  
        except Exception as e:
            print(f"Failed to save document: {str(e)}")
            raise

    def get_occupant_document(self, occupant_id):
        """
        Retrieves an occupant document by occupant ID.
        :param occupant_id: ID of the occupant to retrieve.
        :return: The occupant document if found, None otherwise.
        """
        collection = self.get_collection(self.occupants_collection_name)
        occupant_doc_id = f"Occupant_{occupant_id}"  # Adjust based on your saving logic
        return Collection.get_document(collection, occupant_doc_id)

    def get_seat_document(self, seat_id):
        """
        Retrieves a seat document by seat ID.
        :param seat_id: ID of the seat to retrieve.
        :return: The seat document if found, None otherwise.
        """
        collection = self.get_collection(self.seats_collection_name)
        seat_doc_id = f"Seat_{seat_id}"  # Adjust based on your saving logic
        return Collection.get_document(collection, seat_doc_id)
