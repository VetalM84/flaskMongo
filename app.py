"""File for run the app."""

from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("localhost", 27017)
db = client.get_database("Comparison")
phone = db.get_collection("phone")
factory = db.get_collection("factory")
transaction = db.get_collection("transaction")

from routes import main

app.register_blueprint(main)


if __name__ == "__main__":
    app.run()
