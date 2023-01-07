from flask import Flask, abort, jsonify, request, make_response
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
# Using jwt tokens instead
# from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
import jwt
import uuid
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import logging
from datetime import timezone
from .database.models import Note, db, Task, Category, User, db_drop_and_create_all, setup_db


app = Flask(__name__)
setup_db(app)
app.config['SECRET_KEY'] = '$51335EMCE53315$'
bcrypt = Bcrypt(app)
CORS(app, resources={r"*/api/*": {"origins": "*"}})
# login_manager = LoginManager()
# login_manager.init_app(app)
migrate = Migrate(app, db)

logging.basicConfig(
    filename='app.log', filemode='a', format='%(levelname)s in %(module)s: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# with app.app_context():
#   db_drop_and_create_all()


# @login_manager.user_loader
# def load_user(user_id):
#     try:
#         return User.query.get(int(user_id))
#     except Exception:
#         return None

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    return parts[1]


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = get_token_auth_header()
        if 'x-access-tokens' in request.headers:
            #token = request.headers['x-access-tokens']
            token = request.args.get('token')

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except Exception:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator


@app.route('/')
@cross_origin()
def index():
    return jsonify({
        "success": True
    })


@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    '''
    Used to register a new account, expected input should come in this format \n
    {
        "email": "test005@test.com",
        "username": "Bee5",
        "password": "test5"
    }
    '''
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
            public_id=str(uuid.uuid4()),
            date_created=current_time,
        )
        if user := User.query.filter_by(username=username).first():
            return jsonify({
                "message": "Username already exist"
            })
        elif user := User.query.filter_by(email=email).first():
            return jsonify({
                "message": "Email already exist"
            })
        new_user.insert()

        return jsonify({"success": True, "message": f"{username} created"})
    except Exception:
        abort(400)


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    '''
    Used to login user, expected input should come in this the format \n
    {
    "username": "Bee5",
    "password": "test5"
    }
    '''
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
        # Public_id was used so that user's details e.g username does not appear when
        # the token is decoded.
        token = jwt.encode(
            {
                'public_id': user.public_id, 'exp': datetime.now(timezone.utc) + timedelta(minutes=45)
            }, app.config['SECRET_KEY'], "HS256"
        )
        return jsonify({'token': token})
    except Exception:
        abort(400)


# @app.route('/logout', methods=['GET', 'POST'])
# @cross_origin()
# def logout():
#    '''Function to log a user out'''
#    try:
#        logout_user()
#        return ({
#            "success": True,
#            "message": "User logged out"
#        })
#    except Exception:
#        abort(400)


# Made this endpoint to see what is stored in the database
# @app.route('/users', methods=['GET'])
# @cross_origin()
# def users():
#     try:
#         users = User.query.all()
#         formatted_users = [
#             {user.date_created: user.username, "id": user.public_id} for user in users]
#
#         return jsonify({
#             "success": True,
#             "users": formatted_users
#         })
#     except Exception:
#         abort(401)


@app.route('/categories', methods=['GET', 'POST'])
@cross_origin()
@token_required
def create_category(current_user):
    '''
    Function to add new category, expected input should come in this format, \n
    {
    "name": "Category 1"
    }
    '''
    if request.method == 'GET':
        cats = [cat.name for cat in Category.query.filter(
            Category.user_id == current_user.id).all()]
        return {
            "success": True,
            "categories": cats,
            "total": len(cats)
        }

    if request.method == 'POST':
        body = request.get_json()
        new_name = body.get('name')
        name = new_name.lower()

        cat = Category.query.filter(Category.user_id == current_user.id).all()
        count = len(cat)

        if categories := Category.query.filter(Category.user_id == current_user.id).filter_by(name=name).first():
            return jsonify({
                "success": False,
                "message": f"Category {name} already exists!"
            })
        category = Category(name=name, user_id=current_user.id, cat_id=count+1)
        category.insert()

        return jsonify({
            "success": True,
            "message": f"Category {name} added successfully!"
        })

# create new note  "methods=['POST']"


@app.route('/notes', methods=['POST'])
@cross_origin()
@token_required
def create_note(current_user):
    '''
    Function to create notes, expected input should come in this format \n
    {
    "title": "Note 1",
    "content": "Here goes your notes",
    "category_id": 1
    }
    '''
    body = request.get_json()

    notes = Note.query.filter(Note.user_id == current_user.id).all()
    count = len(notes)
    try:
        title = body.get("title")
        content = body.get("content")
        category_name = body.get("category_name")

        category = Category.query.filter(Category.user_id == current_user.id).filter(
            Category.name == category_name).one_or_none()

        if category is None:
            return ({
                "success": False,
                "message": "Wrong category name"
            })

        if title is None:
            return ({
                "success": False,
                "message": "Please enter Note title"
            })

        new_note = Note(
            title=title, content=content, user_id=current_user.id,
            note_id=count+1, category_id=category.id, date_created=current_time,
        )

        new_note.insert()

        return jsonify({
            "success": True,
            "message": f"{title} created!"
        })
    except Exception:
        abort(400)


@app.route('/notes/<int:note_id>', methods=['GET'])
@cross_origin()
@token_required
def get_note(current_user, note_id):
    '''
        Function to get a specific note using the id
        expected response will look similar to this \n
        {
            "category_id": 3,
            "content": "Here goes your notes",
            "date_created": "25/11/2022 09:52:52",
            "id": 15,
            "title": "Tasks and Notes"
        }
    '''
    try:
        if note := Note.query.join(User).filter(User.id == current_user.id).join(
            Category, Category.id == Note.category_id).filter(
                Note.note_id == note_id).one_or_none():

            return jsonify({
                "title": note.title,
                "content": note.content,
                "date_created": note.date_created,
                "id": note.note_id,
                "category_id": note.category_id
            })
        else:
            abort(404)
    except Exception:
        abort(400)


# get all notes
@ app.route('/notes', methods=['GET'])
@ cross_origin()
@token_required
def get_notes(current_user):
    '''Function to view notes, expected response should return notes authorized by user eg \n
        {
            "notes": [
                {
                    "category_id": 2,
                    "content": "An edited note for all!",
                    "date_created": "25/11/2022 09:52:13",
                    "id": 11,
                    "title": "This has been edited"
                },
                {
                    "category_id": 3,
                    "content": "Here goes your notes",
                    "date_created": "25/11/2022 09:52:52",
                    "id": 15,
                    "title": "Tasks and Notes by Larawwaaaaaa"
                },
            ]
        }
    '''
    note_data = []
    try:
        notes = Note.query.join(User).filter(User.id == current_user.id).join(
            Category, Category.id == Note.category_id).all()
        for i in notes:
            note_data.extend(
                {
                    "title": note.title, "content": note.content,
                    "date_created": note.date_created, "id": note.note_id,
                    "category_id": note.category_id
                } for note in notes)

        result = note_data
        return jsonify({
            "success": True,
            "notes": result
        })
    except Exception:
        abort(404)


# get all notes by category
@ app.route('/notes/category/<string:category>', methods=['GET'])
@ cross_origin()
@token_required
def get_notes_by_category(current_user, category):
    '''
        Function to get notes by category name, searches with given \n
        characters to return notes with category names having those characters. 
        Example of expected response \n
        {
            "notes": [
                {
                    "category_id": 1,
                    "content": "Here goes your notes",
                    "date_created": "25/11/2022 09:52:13",
                    "id": 10,
                    "title": "Tasks and Notes Kasumu"
                },
                {
                    "category_id": 2,
                    "content": "An edited note for all!",
                    "date_created": "25/11/2022 09:52:13",
                    "id": 11,
                    "title": "This has been edited"
                },
            ]
        }
    '''
    note_data = []
    try:
        # Get notes filtered by category name for current user
        # notes with category names having given characters will be returned
        notes = Note.query.join(User).filter(User.id == current_user.id).join(Category).filter(
            Category.id == Note.category_id).filter(Category.name.like(f"%{category}%")).all()

        note_data.extend(
            {
                "title": note.title, "content": note.content,
                "date_created": note.date_created, "id": note.note_id,
                "category": note.category_id
            } for note in notes)

        result = note_data
        return jsonify({
            "success": True,
            "notes": result
        })
    except Exception:
        abort(400)

# Update a note by id


@app.route('/notes/<int:note_id>', methods=['PUT', 'PATCH'])
@cross_origin()
@token_required
def edit_note(current_user, note_id):
    '''
        Function to edit existing note, example of expected input; \n
        {
            "title": "This has been edit",
            "content": "An edited note for all!",
            "category_id": 3
        }
    '''
    # body includes the json body or form data field we would like to edit.
    body = request.get_json()
    try:
        note_to_update = Note.query.join(User).filter(User.id == current_user.id).join(
            Category, Category.id == Note.category_id).filter(
                Note.note_id == note_id).one_or_none()

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
@token_required
def delete_note(current_user, note_id):
    '''
        Function to delete note
    '''
    try:
        note = Note.query.join(User).filter(User.id == current_user.id).filter(
            Note.note_id == note_id).one_or_none()
        if note is None:
            abort(404)
        else:
            note.delete()
            return {"success": True, "message": f"{str(note.title)} deleted successfully"}
    except Exception:
        abort(400)


@app.route('/tasks', methods=['POST'])
@cross_origin()
@token_required
def create_task(current_user):
    '''
        Function to create task, expected input; \n
        {
            "title": "Tasks and Notes crud",
            "description": "Just another Lorem",
            "start_time": "24/11/2022 8:30:00",
            "end_time": "24/11/2022 9:40:00"
        }
    '''
    body = request.get_json()
    # Note that time period has been dropped and end_time added
    title = body.get("title")
    content = body.get("description")
    start_time = body.get("start_time")
    end_time = body.get("end_time")

    tasks = Task.query.filter(Task.user_id == current_user.id).all()
    count = len(tasks)
    try:
        task = Task(
            title=title,
            content=content,
            start_time=start_time,
            end_time=end_time,
            task_id=int(count+1),
            user_id=current_user.id,
        )
        if title is None:
            return jsonify({
                "success": False,
                "message": "Please enter Task title"
            })
        if start_time is None and end_time is None:
            return jsonify({
                "success": False,
                "message": "Please enter valid start time and time period for task"
            })
        start = datetime.strptime(start_time, '%d/%m/%Y %H:%M:%S')
        finish = datetime.strptime(end_time, '%d/%m/%Y %H:%M:%S')
        if start >= finish:
            return jsonify({
                "success": False,
                "message": "Time to complete task should be greater than start time"
            })
        if start < datetime.now():
            return jsonify({
                "success": False,
                "message": "Task start time should be greater than current time"
            })
        task.insert()
        return ({
            'success': True,
            "message": f"{title} created successfully"
        })
    except Exception:
        abort(400)


@app.route('/tasks', methods=['GET'])
@cross_origin()
@token_required
def view_task(current_user):
    '''
        Function to return tasks already created, expected response \n
        {
            "success": true,
            "tasks": {
                "current_tasks": [],
                "past_tasks": [],
                "upcoming_tasks": [
                    {
                        "description": "Just another Lorem, This is to test current_user can be added to user id",
                        "end_time": "24/12/2022 9:40:00",
                        "id": 128,
                        "start_time": "24/12/2022 8:30:00",
                        "title": "Tasks & Notes crud"
                    },
                ]
    '''
    tasks = Task.query.join(User).filter(User.id == int(current_user.id)).all()
    past_tasks = []
    upcoming_tasks = []
    current_tasks = []

    try:
        for task in tasks:
            start_time = datetime.strptime(
                str(task.start_time), '%d/%m/%Y %H:%M:%S')
            end_time = datetime.strptime(
                str(task.end_time), '%d/%m/%Y %H:%M:%S')
            now = datetime.now()
            match [start_time <= now, end_time >= now]:
                case [True, False]:
                    past_tasks.append({
                        "id": task.task_id,
                        "title": task.title,
                        "description": task.content,
                        "start_time": task.start_time,
                        "end_time": task.end_time
                    })
                case [True, True]:
                    current_tasks.append({
                        "id": task.task_id,
                        "title": task.title,
                        "description": task.content,
                        "start_time": task.start_time,
                        "end_time": task.end_time
                    })
                case [False, True]:
                    upcoming_tasks.append({
                        "id": task.task_id,
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
@token_required
def get_task(current_user, task_id):
    '''
        Function to get a specific task using it's id, example of returned task \n
        {
            "success": true,
            "task": {
                "description": "Just another Lorem, This is to test current_user can be added to user id",
                "end_time": "24/11/2022 9:40:00",
                "id": 129,
                "start_time": "24/11/2022 8:30:00",
                "title": "Tasks crud"
            }
        }
    '''
    try:
        task = Task.query.join(User).filter(User.id == current_user.id).filter(
            Task.task_id == task_id).one_or_none()

        task_data = {
            "id": task.task_id,
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
@token_required
def edit_task(current_user, task_id):
    '''
        Function to edit already existing task, example of input \n
        {
            "title": "To be updated tawwwwa",
            "description": "Just another Lorem, This is to test current_user can be added to user id",
            "start_time": "24/11/2022 8:30:00",
            "end_time": "24/11/2022 9:40:00"
        }
    '''
    body = request.get_json()

    try:
        task_to_update = Task.query.join(User).filter(
            User.id == current_user.id).filter(Task.task_id == task_id).one_or_none()

        task_to_update.title = body.get("title")
        task_to_update.content = body.get("description")
        task_to_update.start_time = body.get("start_time")
        task_to_update.end_time = body.get("end_time")

        if task_to_update.start_time >= task_to_update.end_time:
            return jsonify({
                "success": False,
                "message": "Task finish time should be greater than start time"
            })

        task_to_update.update()

        return ({
            'success': True,
            "message": "Task updated successfully"
        })
    except Exception:
        abort(400)


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_task(current_user, task_id):
    '''Function to delete task using it's id'''
    try:
        task = Task.query.join(User).filter(User.id == current_user.id).filter(
            Task.task_id == task_id).one_or_none()
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


# @app.errorhandler(401)
# @cross_origin()
# def unprocessable(error):
#    return jsonify({
#        "success": False,
#        "error": 401,
#        "message": "Unauthorized"
#    }), 401

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

# @app.errorhandler(500)
# @cross_origin()
# def special_exception_handler(error):
#     return jsonify({
#         "success": False,
#         "error": 500,
#         "message": 'Database connection failed'
#     }), 500


@app.errorhandler(AuthError)
@cross_origin()
def authentication_error(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), auth_error.status_code
