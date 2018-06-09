from flask_sqlalchemy import SQLAlchemy
from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    uuid = db.Column(db.String(120), unique=True)
    account_created = db.Column(db.Boolean(), unique=False, default=False)

    def __repr__(self):
        return "<User %r>" % self.username
