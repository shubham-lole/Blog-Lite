from app.extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(100))
    bio = db.Column(db.String)

class Post(db.Model):
    __tablename__ = "post"
    post_id = db.Column(db.Integer, primary_key=True)
    photo_url = db.Column(db.String)
    caption = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.String)

class Follower(db.Model):
    __tablename__ = "follower"
    follow_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))

