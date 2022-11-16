from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from datetime import datetime

from .database.models import Note, Task, User, db_drop_and_create_all, setup_db

app = Flask(__name__)
setup_db(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"*/api/*": {"origins": "*"}})

login_manager = LoginManager()

now = datetime.now()

with app.app_context():
    db_drop_and_create_all()

@app.route('/register', methods=['GET', 'POST'])
@cross_origin()
def register():
    body = request.get_json()

    #Get user info
    first_name = body.get("firstname")
    last_name = body.get("lastname")
    email = body.get("email")
    username = body.get("username")
    password = bcrypt.generate_password_hash(body.get("password"))


    try:
        new_user = User(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = username,
            password = password,
            date_created = now.strftime("%d/%m/%Y %H:%M:%S"), 
        )
        new_user.insert()

        return jsonify(
            {
                "success": True
            }
        )
    except Exception:
        abort(422)

