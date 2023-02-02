"""File for run the app."""
import os

from dotenv import load_dotenv
from flask import Flask
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

from validation_schema import (
    factory_validation_schema,
    phone_validation_schema,
    transaction_validation_schema,
)

load_dotenv()

app = Flask(__name__)
connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(connection_string)
db = client.get_database("Comparison")


def create_db_collection(collection_name: str, validator: dict = None):
    try:
        db.create_collection(collection_name, validator=validator)
    except CollectionInvalid as e:
        print(e)


create_db_collection(collection_name="phone", validator=phone_validation_schema)
create_db_collection(collection_name="factory", validator=factory_validation_schema)
create_db_collection(
    collection_name="transaction", validator=transaction_validation_schema
)

phone = db.get_collection("phone")
factory = db.get_collection("factory")
transaction = db.get_collection("transaction")

from routes import main

app.register_blueprint(main)

if __name__ == "__main__":
    app.run()
