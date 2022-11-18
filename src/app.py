from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, login_user
from flask_bcrypt import Bcrypt
from datetime import datetime
from .database.models import Note, Task, User, db_drop_and_create_all, setup_db

app = Flask(__name__)
setup_db(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"*/api/*": {"origins": "*"}})

login_manager = LoginManager()

now = datetime.now()

# with app.app_context():
#     db_drop_and_create_all()


@app.route('/')
@cross_origin()
def index():
    return jsonify({
        "success": True
    })


@app.route('/register', methods=['GET', 'POST'])
@cross_origin()
def register():
    body = request.get_json()

    # # Get user info
    first_name = body.get("first_name")
    last_name = body.get("last_name")
    email = body.get("email")
    username = body.get("username")
    password = body.get("password")

    # New user's details are saved to the database
    try:
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
            date_created=now.strftime("%d/%m/%Y %H:%M:%S"),
        )
        new_user.hash_password()
        new_user.insert()

        return jsonify({
                "success": True
        })
    except Exception:
        abort(422)


@app.route('/login', methods=['GET', 'POST'])
@cross_origin()
def login():
    body = request.get_json()
    #Get user login details
    username = body.get("username")
    password = body.get("password")

    # User should be able to login with his username or email to access resources
    '''
        if user exist in database?
            if yes, check if password matches with user
                if yes give access
            else return 'wrong input'
        else return 'username does not exist'
    '''
    try:
        user = User.query.filter_by(username=username).first()
        decrypted_password = bcrypt.check_password_hash(user.password, password)
        print("This is decrypted: ", decrypted_password)
        if user is None:
            return ({
                "success": False,
                "message": "Invalid username"
            })
        if user and decrypted_password == False:
            return({
                "success": False,
                "message": "Username and Password does not match"
            })
        login_user(user)
        return ({
            "success": True,
            "message": "Login successful"
        })
    except Exception:
        abort(422)

# Made this endpoint to see what is stored in the database
@app.route('/users', methods=['GET', 'POST'])
@cross_origin()
def users():
    users = User.query.all()
    formatted_users = [{user.date_created: user.username} for user in users]

    return jsonify({
        "success": True,
        "users": formatted_users
    })


@app.route('/new_note', methods=['POST'])
@cross_origin()
def create_note():
    body = request.get_json()

    title = body.get("title")
    content = body.get("content")
    user_id = body.get("user_id")
    task_id = body.get("task_id")

    try:
        new_note = Note(title=title, content=content,
                        user_id=user_id, task_id=task_id)

        new_note.insert()

        return jsonify({
            "success": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": e
        })
