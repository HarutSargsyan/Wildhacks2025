from flask import current_app
from pymongo import MongoClient
from werkzeug.local import LocalProxy

def get_db():
    if 'db' not in current_app.extensions:
        client = MongoClient(current_app.config['MONGO_URI'])
        current_app.extensions['db'] = client['wildhacks2025']  # Specify database name
    return current_app.extensions['db']

db = LocalProxy(get_db)

def init_db(app):
    with app.app_context():
        get_db() 