import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# used th get the absolute path of this directory
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = f"sqlite:///{os.path.join(basedir, 'database.db')}"

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    # Adding public_id
    public_id = db.Column(db.Integer)
    date_created = db.Column(db.String)
    note = db.relationship('Note', backref=db.backref('Note', lazy=True))
    category = db.relationship(
        'Category', backref=db.backref('Category', lazy=True))
    task = db.relationship('Task', backref=db.backref('Task', lazy=True))

    def __repre__(self):
        return f'<User {self.id} {self.first_name} {self.last_name}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    # def delete(self):
    #    db.session.delete(self)
    #    db.session.commit()

    def update(self):
        db.session.commit()


class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    date_created = db.Column(db.String, default=datetime.now(), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    # task_id to be removed so task will not rely on Note
    #task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    def __repre__(self):
        return f'<User {self.id} {self.title} {self.content}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # Added user_id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note = db.relationship('Note', backref=db.backref('note', lazy=True))

    def __repre__(self):
        return f'<User {self.id} {self.title} {self.content}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    start_time = db.Column(db.String)
    # Removing the time_period and adding
    # end_time
    #time_period = db.Column(db.String)
    end_time = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repre__(self):
        return f'<User {self.id} {self.start_time} {self.time_period}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
