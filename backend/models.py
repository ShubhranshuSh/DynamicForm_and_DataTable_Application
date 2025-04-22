from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    uid = db.Column(db.String(11), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255))
    height = db.Column(db.String(10))
    weight = db.Column(db.String(10))
    profile_picture = db.Column(db.String(255))  # Store image filename or URL
    blood_group = db.Column(db.String(3))
    emergency_contact = db.Column(db.String(15), nullable=False)
    allergies = db.Column(db.Text)
    notes = db.Column(db.Text)
    # Required fields for Flask-Security
    fs_uniquifier = db.Column(db.String(255), unique=True)
    roles = db.relationship('Role', backref='bearers', secondary='user_roles')
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return f'<User {self.name} | UID: {self.uid}>'

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
