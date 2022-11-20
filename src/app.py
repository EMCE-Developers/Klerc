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
current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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
            date_created=current_time,
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
                        user_id=user_id, category_id=category_id, date_created=current_time,)

        new_note.insert()

        return jsonify({
            "success": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": e
        })


@app.route('/tasks/create', methods=['GET', 'POST'])
@cross_origin()
def create_task():
    body = request.get_json()

    title = body.get("title")
    content = body.get("description")
    start_time = body.get("start_time")
    time_period = body.get("time_period")

    
    try:
        task = Task(
            title=title,
            content=content,
            start_time=start_time,
            time_period=time_period,
            # user_id=load_user(id),
        )

        if title is None:
            return ({
                "success": False,
                "message": "Please enter Task title"
            })

        if start_time is None and time_period is None:
            return ({
                "success": False,
                "message": "Please enter valid start time and time period for task"
            })
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
    past_tasks = []
    upcoming_tasks = []
    for task in tasks:
        # When we implement current task, it should look like,
        # match [task.end_time < current_time, task.end_time > current_time]
        #       case [True, Flase]: for current task
        match [task.start_time < current_time]:
            case [True]:
                past_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.content,
                    "start_time": task.start_time,
                    "time_period": task.time_period
                 })
            case [False]:
                upcoming_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.content,
                    "start_time": task.start_time,
                    "time_period": task.time_period
                })
    
    task_data ={
        "upcoming_tasks": upcoming_tasks,
        "past_tasks": past_tasks
    }
    

    return jsonify({
        "success": True,
        "tasks": task_data
    })

@app.route('/tasks/<int:id>/edit', methods=['GET'])
@cross_origin()
def edit_task(id):

    task = Task.query.get(id)

    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.content,
        "start_time": task.start_time,
        "time_period": task.time_period
    }

    return ({
        "success": True,
        "task": task_data
    })

@app.route('/tasks/<int:task_id>/edit', methods=['POST','PATCH'])
@cross_origin()
def edit_task_submission(task_id):

    body = request.get_json()

    try:
        task_to_update = Task.query.filter(Task.id == task_id).one_or_none()

        if task_to_update is None:
            abort(404)

        task_to_update.title = body.get("title")
        task_to_update.content = body.get("description")
        task_to_update.start_time = body.get("start_time")
        task_to_update.time_period = body.get("time_period")

        task_to_update.update()

        return ({
            'success': True,
            "message": "Task updated successfully"
        })
    except Exception:
        abort(422)