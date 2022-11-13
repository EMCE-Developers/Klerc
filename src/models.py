from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    date_created = db.Column(db.String)
    is_active = db.Column(db.String)
    note = db.relationship('Note', backref=db.backref('Note', lazy='true'))
    task = db.relationship('Task', backref=db.backref('Task', lazy='true'))