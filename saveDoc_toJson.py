# check.py

import sys
sys.path.append('/home/ihebjeridi/Documents/cbliteFinal/couchbase-lite-python')
import json
from CouchbaseLite.Document import MutableDocument
from CouchbaseLite.Database import Database, DatabaseConfiguration


db_path = "/home/ihebjeridi/Documents/app_OOP/app_acquisation"
db_name = "AIO_DB"

def read_document(doc_id):
    config = DatabaseConfiguration(db_path)
    db = Database(db_name, config)
    read_doc = db.getDocument(doc_id)
    
    if read_doc:
        props = read_doc.properties
        print("Document ID:", doc_id)
        for key, value in props.items():
            print(f"{key}: {value}")
        
        json_file_path = f"/home/ihebjeridi/Documents/app - OOP/app_acquisation/data/{doc_id}.json"
        with open(json_file_path, 'w') as json_file:
            json.dump(props, json_file, indent=4)
        print(f"Document data saved to '{json_file_path}'.")
    else:
        print(f"Document with ID {doc_id} not found.")

def main(doc_id):
    read_document(doc_id)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check.py <document_id>")
    else:
        doc_id = sys.argv[1]  
        main(doc_id)