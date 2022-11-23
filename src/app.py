from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.exceptions import MethodNotAllowed, NotFound, BadRequest, Unauthorized, UnprocessableEntity
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

#with app.app_context():
#   db_drop_and_create_all()


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


@app.route('/')
@cross_origin()
def index():
    return jsonify({
        "success": True
    })


@app.route('/register', methods=['POST'])
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
        if user := User.query.filter_by(username=username).first():
            return ({
                "message": "Username already exist"
            })
        elif user := User.query.filter_by(email=email).first():
            return ({
                "message": "Email already exist"
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


@app.route('/logout', methods=['GET', 'POST'])
@cross_origin()
@login_required
def logout():
    logout_user()
    return({
        "success": True,
        "message": "User logged out"
    })


# Made this endpoint to see what is stored in the database
@app.route('/users', methods=['GET'])
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
@login_required
def new_category():

    body = request.get_json()
    name = body.get('name')
    if categories := Category.query.filter_by(name=name).first():
        return jsonify({
            "success": False,
            "message": f"Category {name} already exists!"
        })
    category = Category(name=name, user_id=current_user.id)
    category.insert()

    return jsonify({
        "success": True,
        "message": f"Category {name} added successfully!"
    })

# create new note  "methods=['POST']"
@app.route('/notes', methods=['POST'])
@cross_origin()
@login_required
def create_note():
    body = request.get_json()

    title = body.get("title")
    content = body.get("content")
    # The user_id is being removed as current_user.id==user_id
    #user_id = body.get("user_id")
    category_id = body.get("category_id")

    try:
        new_note = Note(
            title=title, content=content, user_id=current_user.id, 
            category_id=category_id, date_created=current_time,
        )

        new_note.insert()

        return jsonify({
            "success": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": e
        })


@app.route('/notes/<int:note_id>', methods=['GET'])
@cross_origin()
@login_required
def get_note(note_id):

    try:
        if note := Note.query.join(User).filter(User.id==current_user.id).join(
            Category).filter(Category.id==Note.category_id).filter(Note.id==note_id).one_or_none():
            return jsonify({
                "title": note.title,
                "content": note.content,
                "date_created": note.date_created,
                "id": note.id,
                "category_id": note.category_id
            })
        else:
            abort(404)
    except Exception as e:
        abort(400)


# get all notes
@app.route('/notes', methods=['GET'])
@cross_origin()
@login_required
def get_notes():
    # modified the notes endpoint
    note_data = []
    try:
        # Query to get notes with user_id = current_user
        notes = Note.query.join(User).filter(User.id==current_user.id).join(
            Category).filter(Note.category_id==Category.id).all()
        # Properties to add to note to be returned
        note_data.extend(
            {
                "title": note.title, "content": note.content, 
                "date_created": note.date_created, "id": note.id,
                "category_id": note.category_id
            } for note in notes)

        result = {"notes_data" : note_data}
        return jsonify({
            "success": True,
            "notes": result
        })
    except Exception:
        abort(404)


# get all notes by category
@app.route('/notes/<string:category>', methods=['GET'])
@cross_origin()
@login_required
def get_notes_by_category(category):

    note_data = []
    # Get notes filtered by category name for current user
    try:
        # notes with category names having given characters willbe returned
        notes = Note.query.join(User).filter(User.id==current_user.id).join(Category).filter(
        Category.id==Note.category_id).filter(Category.name.like(f"%{category}%")).all()
    
        note_data.extend(
            {
                "title": note.title, "content": note.content, 
                "date_created": note.date_created, "id": note.id,
                "category": note.category_id
            } for note in notes)

        result = {"notes_data" : note_data}
        return jsonify({
            "success": True,
            "notes": result
        })
    except Exception:
        abort(400)

# Update a note by id
@app.route('/notes/<int:note_id>', methods=['PUT', 'PATCH'])
@cross_origin()
@login_required
def edit_note(note_id):
    # body includes the json body or form data field we would like to edit.
    body = request.get_json()
    try:
        note_to_update = Note.query.join(User).filter(User.id==current_user.id).join(Category).filter(
            Category.id==Note.category_id).filter(Note.id==note_id).one_or_none()

        note_to_update.title = body.get("title")
        note_to_update.content = body.get("content")
        note_to_update.category_id = body.get("category_id")

        note_to_update.update()
        return ({
            "success": True,
            "message": "Note updated successfully"
        })
    except Exception:
        abort(400)


@app.route('/notes/<int:note_id>', methods=['DELETE'])
@cross_origin()
@login_required
def delete_note(note_id):

    try:
        note= Note.query.join(User).filter(User.id==current_user.id).filter(
            Note.id == note_id).one_or_none()
        if note is None:
            abort(404)
        else:
            note.delete()
            return {"success": True, "message": f"{str(note.title)} deleted successfully"}
    except Exception:
        abort(400)


@app.route('/tasks', methods=['POST'])
@cross_origin()
@login_required
def create_task():
    body = request.get_json()
    # Note that time period has been dropped and end_time added
    title = body.get("title")
    content = body.get("description")
    start_time = body.get("start_time")
    end_time = body.get("end_time")

    try:
        task = Task(
            title=title,
            content=content,
            start_time=start_time,
            end_time=end_time,
            user_id=current_user.id,
        )

        if title is None:
            return ({
                "success": False,
                "message": "Please enter Task title"
            })

        if start_time is None and end_time is None:
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
        abort(400)


@app.route('/tasks', methods=['GET'])
@cross_origin()
@login_required
def get_tasks():
    tasks = Task.query.join(User).filter(User.id==int(current_user.id)).all()
    past_tasks = []
    upcoming_tasks = []
    current_tasks = []
    
    try:
        for task in tasks:

            match [task.start_time <= current_time, task.end_time >= current_time]:
                case [True, False]:
                    past_tasks.append({
                        "id": task.id,
                        "title": task.title,
                        "description": task.content,
                        "start_time": task.start_time,
                        "end_time": task.end_time
                    })
                case [True, True]:
                    current_tasks.append({
                        "id": task.id,
                        "title": task.title,
                        "description": task.content,
                        "start_time": task.start_time,
                        "end_time": task.end_time
                    })
                case [False, True]:
                    upcoming_tasks.append({
                        "id": task.id,
                        "title": task.title,
                        "description": task.content,
                        "start_time": task.start_time,
                        "end_time": task.end_time
                    })

        task_data = {
            "current_tasks": current_tasks,
            "upcoming_tasks": upcoming_tasks,
            "past_tasks": past_tasks
        }
        return jsonify({
            "success": True,
            "tasks": task_data
        })
    except Exception:
        abort(400)


@app.route('/tasks/<int:task_id>', methods=['GET'])
@cross_origin()
@login_required
def get_task(task_id):

    try:
        task = Task.query.join(User).filter(User.id==current_user.id).filter(Task.id == task_id).one_or_none()

        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.content,
            "start_time": task.start_time,
            "end_time": task.end_time
        }
        return ({
            "success": True,
            "task": task_data
        })
    except Exception:
        abort(400)


@app.route('/tasks/<int:task_id>', methods=['PUT', 'PATCH'])
@cross_origin()
@login_required
def edit_task(task_id):

    body = request.get_json()

    try:
        task_to_update = Task.query.join(User).filter(User.id==current_user.id).filter(Task.id == task_id).one_or_none()

        task_to_update.title = body.get("title")
        task_to_update.content = body.get("description")
        task_to_update.start_time = body.get("start_time")
        task_to_update.end_time = body.get("end_time")

        task_to_update.update()

        return ({
            'success': True,
            "message": "Task updated successfully"
        })
    except Exception:
        abort(400)


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@cross_origin()
@login_required
def delete_task(task_id):

    try:
        task = Task.query.join(User).filter(User.id==current_user.id).filter(Task.id == task_id).one_or_none()
        if task is None:
            abort(404)
        else:
            task.delete()
            return {"success": True, "message": f"{str(task.title)} deleted successfully"}
    except Exception:
        abort(400)


@app.errorhandler(400)
@cross_origin()
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

@app.errorhandler(401)
@cross_origin()
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(404)
@cross_origin()
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

@app.errorhandler(405)
@cross_origin()
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405

@app.errorhandler(422)
@cross_origin()
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422