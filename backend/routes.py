from datetime import datetime
from functools import wraps
import os
import traceback
import uuid
from flask import current_app as app, jsonify, request, render_template , abort, send_file, send_from_directory
from flask_security import auth_required, verify_password, hash_password, login_required, current_user, logout_user, login_user
from backend.models import  db, User, Role 
from werkzeug.utils import secure_filename


datastore = app.security.datastore


# Role-based access control
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.has_role('admin'):
            return jsonify({'message': 'Access Denied: Admin only'}), 403
        return func(*args, **kwargs)
    return wrapper


def user_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.has_role('user'):
            return jsonify({'message': 'Access Denied: Must be valid user'}), 403
        return func(*args, **kwargs)
    return wrapper




# Home route
@app.route("/")
def home():
    return "Welcome to the Home Page!"


@app.route('/protected')
@auth_required('token')
def protected():
    return "This is an authenticated user."

from flask import request, jsonify
from flask_security import current_user
from backend.models import db, User
from flask_security.utils import verify_password

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Ensure the email and password fields are provided
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400
    
    # Find the user by email
    user = User.query.filter_by(email=email).first()  # Make sure you're querying the right database
    if not user:
        return jsonify({"message": "Invalid email"}), 404  # Changed to match the provided logic

    # Check if the password matches
    if verify_password(password, user.password):  # Ensure verify_password checks against hashed password
        # Generate token (this assumes you have a `get_auth_token` method for JWT generation)
        token = user.get_auth_token()

        # Serialize roles as a list of role names
        role_names = [role.name for role in user.roles]
        
        return jsonify({
            'token': token,
            'email': user.email,
            'role': role_names,  # List of role names instead of a single role
            'id': user.id
        }), 200  # Successfully logged in
        
    else:
        return jsonify({"message": "Invalid password"}), 401  # Incorrect password
    


UPLOAD_FOLDER = 'uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Function to check if the file is an allowed image type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    uid = data.get('uid')
    phone = data.get('phone')
    address = data.get('address')
    height = data.get('height')
    weight = data.get('weight')
    blood_group = data.get('blood_group')
    emergency_contact = data.get('emergency_contact')
    allergies = data.get('allergies')
    notes = data.get('notes')

    profile_picture = request.files.get('profile_picture')
    if profile_picture and allowed_file(profile_picture.filename):
        picture_filename = secure_filename(profile_picture.filename)
        picture_path = os.path.join(UPLOAD_FOLDER, picture_filename)
        profile_picture.save(picture_path)
    else:
        picture_path = None

    # Basic field check
    if not all([name, email, password, uid, phone, emergency_contact]):
        return jsonify({"message": "Required fields: name, email, password, uid, phone, emergency_contact."}), 400

    # Validation logic
    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"message": "Phone number must be exactly 10 digits."}), 400
    if not uid.isdigit() or len(uid) != 11:
        return jsonify({"message": "UID must be exactly 11 digits."}), 400
    if not emergency_contact.isdigit() or len(emergency_contact) != 10:
        return jsonify({"message": "Emergency contact must be exactly 10 digits."}), 400
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Invalid email format."}), 400

    # Check duplicates
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User with this email already exists."}), 409
    if User.query.filter_by(uid=uid).first():
        return jsonify({"message": "User with this UID already exists."}), 409

    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        return jsonify({"message": "User role not found. Contact administrator."}), 500

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        uid=uid,
        phone=phone,
        address=address,
        height=height,
        weight=weight,
        blood_group=blood_group,
        emergency_contact=emergency_contact,
        allergies=allergies,
        notes=notes,
        fs_uniquifier=str(uuid.uuid4()),
        roles=[user_role],
        profile_picture=picture_path
    )

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error registering user: {str(e)}"}), 500

    return jsonify({"message": "User registered successfully."}), 201

@app.route('/user/<int:user_id>/dashboard', methods=['GET'])
@auth_required('token')
@user_required
def user_dashboard(user_id):
    # Ensure current user can only access their own dashboard
    if current_user.id != user_id:
        return jsonify({"message": "Unauthorized access."}), 403

    user_data = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "uid": current_user.uid,
        "phone": current_user.phone,
        "address": current_user.address,
        "height": current_user.height,
        "weight": current_user.weight,
        "blood_group": current_user.blood_group,
        "emergency_contact": current_user.emergency_contact,
        "allergies": current_user.allergies,
        "notes": current_user.notes,
        "profile_picture": current_user.profile_picture,
        "roles": [role.name for role in current_user.roles]
    }

    return jsonify({"message": "Dashboard data fetched successfully.", "user": user_data}), 200