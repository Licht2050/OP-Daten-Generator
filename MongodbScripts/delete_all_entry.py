import pymongo

# Verbindung zur MongoDB-Datenbank herstellen
client = pymongo.MongoClient("mongodb://localhost:27017/")
database_name = "Patientenakte"
collection_name = "Holiday-Record"
db = client[database_name]
collection = db[collection_name]

def delete_all_documents():
    # Lösche alle Dokumente in der Sammlung
    result = collection.delete_many({})
    print(f"{result.deleted_count} Dokumente wurden gelöscht.")

if __name__ == "__main__":
    delete_all_documents()
