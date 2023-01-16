"""File for run the app."""

from flask import Flask
from flask_mongoengine import MongoEngine


app = Flask(__name__)
db = MongoEngine()
app.config['MONGODB_SETTINGS'] = {
    'db': 'Comparison',
    'host': 'localhost',
    'port': 27017
}
db.init_app(app)

from routes import main

app.register_blueprint(main)


if __name__ == '__main__':
    app.run()
