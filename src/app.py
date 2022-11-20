from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_login import LoginManager, login_user
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from datetime import datetime
from .database.models import Note, db, Task, Category, User, db_drop_and_create_all, setup_db

app = Flask(__name__)
setup_db(app)
app.config['SECRET_KEY'] = '$51335EMCE53315$'
bcrypt = Bcrypt(app)
CORS(app, resources={r"*/api/*": {"origins": "*"}})
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)
now = datetime.now()

# with app.app_context():
#    db_drop_and_create_all()


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


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
            password=generate_password_hash(password, 10),
            date_created=now.strftime("%d/%m/%Y %H:%M:%S"),
        )
        print(new_user.password)
        if user := User.query.filter_by(username=username, email=email).first():
            return ({
                "message": "User already exist"
            })
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
    # Get user login details
    username = body.get("username")
    password = body.get("password")

    # User should be able to login with his username to access resources
    try:
        user = User.query.filter_by(username=username).first()

        if not user and not check_password_hash(user.password, password):
            return ({
                "success": False,
                "message": "Invalid username or password"
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
    formatted_users = [
        {user.date_created: user.username, "id": user.id} for user in users]

    return jsonify({
        "success": True,
        "users": formatted_users
    })


@app.route('/categories', methods=['POST'])
@cross_origin()
def new_category():

    body = request.get_json()

    try:
        category = Category(name=body.get('name'))
        category.insert()

        return jsonify({
            "success": True
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": e
        })

# create new note  "methods=['POST']"


@app.route('/notes', methods=['POST'])
@cross_origin()
def create_note():
    body = request.get_json()

    title = body.get("title")
    content = body.get("content")
    user_id = body.get("user_id")
    category_id = body.get("category_id")

    try:
        new_note = Note(title=title, content=content,
                        user_id=user_id, category_id=category_id, date_created=now.strftime("%d/%m/%Y %H:%M:%S"),)

        new_note.insert()

        return jsonify({
            "success": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": e
        })


@app.route('/notes/<int:id>', methods=['GET'])
@cross_origin()
def get_note(id):

    try:
        # Join was done here in order to get the user's name

        query = db.session.query(Note, User).join(
            Note, User.id == Note.user_id).filter(User.id == id).first()
        note = query[0]
        user = query[1]

        return jsonify({
            "creator": user.first_name,
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "date_created": note.date_created
        })
    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": "Note not found"
        })


# get all notes
@app.route('/notes', methods=['GET'])
@cross_origin()
def get_notes():
    query = db.session.query(Note, User).join(
        Note, User.id == Note.user_id).group_by(User.id, Note.id).all()
    data = [{"id": data[0].id, "title": data[0].title,
             "content": data[0].content, "date_creaed": data[0].date_created, "creator": data[1].first_name} for data in query]

    return jsonify({
        "success": True,
        "notes": data
    })


@app.route('/tasks/create', methods=['GET', 'POST'])
@cross_origin()
def create_task():
    body = request.get_json()

    title = body.get("title")
    content = body.get("content")
    start_time = body.get("start_time")
    time_period = body.get("time_period")

    if start_time is None:
        start_time = "To be set"
    if time_period is None:
        time_period = "To be set"
    try:
        task = Task(
            title=title,
            content=content,
            start_time=start_time,
            time_period=time_period,
            # user_id=load_user(id),
        )
        task.insert()

        return ({
            'success': True,
            "message": "Task created successfully"
        })
    except Exception:
        abort(422)


@app.route('/tasks', methods=['GET', 'POST'])
@cross_origin()
def view_task():
    tasks = Task.query.all()
    # formatted_tasks = [{
    #    tasks.title: tasks.content: tasks.start_time: tasks.time_period
    # } for task in tasks]

    return jsonify({
        "success": True,
        "tasks": tasks
    })
