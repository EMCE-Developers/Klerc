from flask import Flask, request, abort, jsonify
from flask_cors import CORS, cross_origin

from .database.models import User, Note, Task, setup_db, db_drop_and_create_all

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"*/api/*": {"origins": "*"}})

with app.app_context():
    db_drop_and_create_all()
