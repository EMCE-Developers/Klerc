import os
from flask_sqlalchemy import SQLAlchemy

# used th get the absolute path of this directory
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = 'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    date_created = db.Column(db.String)
    note = db.relationship('Note', backref=db.backref('Note', lazy='true'))
    task = db.relationship('Task', backref=db.backref('Task', lazy='true'))

    def __repre__(self):
        return f'<User {self.id} {self.first_name} {self.last_name}>'


class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)

    # user and task have been removed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    def __repre__(self):
        return f'<User {self.id} {self.title} {self.content}>'


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    time_period = db.Column(db.String)

    # user column was removed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note = db.relationship('Note', backref=db.backref('note', lazy='true'))

    def __repre__(self):
        return f'<User {self.id} {self.start_time} {self.time_period}>'
