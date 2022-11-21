from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_login import LoginManager, login_user
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from datetime import datetime, timedelta
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
    name = body.get('name')
    categories = Category.query.filter_by(name=name).first()

    if not categories:
        category = Category(name=name)
        category.insert()

        return jsonify({
            "success": True,
            "message": f"Category {name} added successfully!"
        })

    else:
        return jsonify({
            "success": False,
            "message": f"Category {name} already exists!"
        })

# create new note  "methods=['POST']"
# changed the create_note endpoint from '/notes.
@app.route('/notes/create', methods=['POST'])
@cross_origin()
def create_note():
    body = request.get_json()

    title = body.get("title")
    content = body.get("content")
    user_id = body.get("user_id")
    category_id = body.get("category_id")

    try:
        new_note = Note(
            title=title, content=content, user_id=user_id, 
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


@app.route('/notes/<int:id>', methods=['GET'])
@cross_origin()
def get_note(id):

    try:
        # Join was done here in order to get the user's name

        query = db.session.query(Note, User).join(
            Note, User.id == Note.user_id).filter(Note.id == id).first()

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

    query = db.session.query(User, Note, Category).join(
        Note, User.id == Note.user_id).join(Category, Note.category_id == Category.id).all()

    data = [
        {
            "id": data[1].id, "title": data[1].title, "content": data[1].content, 
            "date_created": data[1].date_created, "creator": data[0].first_name, 
            "category": data[2].name
        } for data in query
    ]

    return jsonify({
        "success": True,
        "notes": data
    })


# get all notes by category
@app.route('/notes/<string:category>', methods=['GET'])
@cross_origin()
def get_notes_by_category(category):

    query = db.session.query(Note, Category, User).join(Note, Category.id == Note.category_id).join(
        User, Note.user_id == User.id).filter(Category.name.like(f"%{category}%")).all()


    results = [
        {
            "note_id": result[0].id, "title": result[0].title, 
            "content": result[0].content, "date_created": result[0].date_created, 
            "creator": result[2].first_name
        } for result in query
    ]

    return jsonify({
        "success": len(results) != 0, 
        "category": category, 
        "results": results or "Category does not exist!"
        })


# Update a note by id
@app.route('/notes/<int:note_id>/edit', methods=['PATCH'])
@cross_origin()
def edit_note(note_id):
    # body includes the json body or form data field we would like to edit.
    # As of now, I would include id, title, content, creator and category
    '''
    Query Format
    {
    "id": 8,
    "title": "The 8th note now ",
    "content": "The content of the 8th note has just being edited and the category is being tested",
    "creator": "Kashy",
    "category": "kaokao"
}
    '''
    body = request.get_json()
    categories = Category.query.all()
    # get note id from the body
    # Consider changing id to note_id as it is not a good practice to
    # use built-in variable names and it might confuse other developers
    note_id = body.get("note_id")

    try:
        result = db.session.query(Note, User, Category).join(Note, User.id == Note.user_id).join(
            Category, Note.category_id == Category.id).filter(Note.id == note_id).first()

        (note, user, category) = result
        category_name = body.get("category")

        note.title = body.get("title")
        note.content = body.get("content")
        user.first_name = body.get("creator")

        # the category should not modify except if the name already exists
        for cat in categories:
            category.name = category.name if category_name != cat.name else category_name
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Contents edited, successfully!"
        })

    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": f"Note with id {id} was not found!"
        })

@app.route('/notes/<int:note_id>/delete', methods=['DELETE'])
@cross_origin()
def delete_note(note_id):

    try:
        note = Note.query.filter(Note.id == note_id).one_or_none()

        note.delete()

        return {"success": True, "message": f"{str(note.title)} deleted successfully"}
    except Exception:
        abort(400)


@app.route('/tasks/create', methods=['GET', 'POST'])
@cross_origin()
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
            # user_id=load_user(id),
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
        abort(422)


@app.route('/tasks', methods=['GET', 'POST'])
@cross_origin()
def view_task():
    tasks = Task.query.all()
    past_tasks = []
    upcoming_tasks = []
    current_tasks = []
    
    for task in tasks:
        print(task.end_time)
        
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


@app.route('/tasks/<int:task_id>/edit', methods=['GET'])
@cross_origin()
def edit_task(task_id):

    try:
        task = Task.query.filter(Task.id == task_id).one_or_none()
        print(task)

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


@app.route('/tasks/<int:task_id>/edit', methods=['POST', 'PATCH'])
@cross_origin()
def edit_task_submission(task_id):

    body = request.get_json()

    try:
        task_to_update = Task.query.filter(Task.id == task_id).one_or_none()

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
        abort(422)


@app.route('/tasks/<int:task_id>/delete', methods=['DELETE'])
@cross_origin()
def delete_task(task_id):

    try:
        task = Task.query.filter(Task.id == task_id).one_or_none()

        task.delete()

        return {"success": True, "message": f"{str(task.title)} deleted successfully"}
    except Exception:
        abort(400)


@app.errorhandler(422)
@cross_origin()
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422

@app.errorhandler(400)
@cross_origin()
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

@app.errorhandler(404)
@cross_origin()
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404