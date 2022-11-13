from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import User

# App Config
app = Flask(__name__)
moment = Moment(app)