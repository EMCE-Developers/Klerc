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

@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    body = request.get_json()

    #Get user info
    first_name = body.get("first_name")
    last_name = body.get("last_name")
    email = body.get("email")
    username = body.get("username")
    password = request.json.get("password")

    username_list = query.User

    try:
        new_user = User(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = username,
            password = password,
            date_created = now.strftime("%d/%m/%Y %H:%M:%S"), 
        )
        if new_user.username in
        new_user.hash_password()
        new_user.insert()

        return jsonify(
            {
                "success": True
            }
        )
    except Exception:
        abort(422)

'''
# Made this endpoint to see what is stored in the database
@app.route('/users', methods=['GET', 'POST'])
@cross_origin()
def users():
    users = User.query.all()
    formatted_users = {user.date_created: user.username for user in users }
    print(formatted_users)

    return jsonify({
        "success": True,
        "users": formatted_users
    })
'''