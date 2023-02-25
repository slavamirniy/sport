from pymongo import MongoClient

client = None

def get_database():
    global client
    if client is None:
        CONNECTION_STRING = "mongodb://localhost:27017"
        client = MongoClient(CONNECTION_STRING)
    return client['sportapp']

if __name__ == "__main__":   
   get_database()