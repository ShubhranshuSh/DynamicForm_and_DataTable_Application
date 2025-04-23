from datetime import datetime
from functools import wraps
import os
import traceback
import uuid
from flask import current_app as app, jsonify, request, render_template, abort, send_file, send_from_directory
from flask_security import auth_required, verify_password, hash_password, login_required, current_user, logout_user, login_user
from backend.models import db, User, Role
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

@app.route("/")
def home():
    return "Welcome to the Home Page!"

@app.route('/protected')
@auth_required('token')
def protected():
    return "This is an authenticated user."

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Invalid email"}), 404

    if verify_password(password, user.password):
        token = user.get_auth_token()
        role_names = [role.name for role in user.roles]
        return jsonify({
            'token': token,
            'email': user.email,
            'role': role_names,
            'id': user.id
        }), 200
    else:
        return jsonify({"message": "Invalid password"}), 401

UPLOAD_FOLDER = os.path.join('uploads', 'profile_pics')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        save_path = os.path.join(UPLOAD_FOLDER, picture_filename)
        profile_picture.save(save_path)
        picture_path = os.path.normpath(f"profile_pics/{picture_filename}").replace("\\", "/")
    else:
        picture_path = None

    if not all([name, email, password, uid, phone, emergency_contact]):
        return jsonify({"message": "Required fields: name, email, password, uid, phone, emergency_contact."}), 400

    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"message": "Phone number must be exactly 10 digits."}), 400
    if not uid.isdigit() or len(uid) != 11:
        return jsonify({"message": "UID must be exactly 11 digits."}), 400
    if not emergency_contact.isdigit() or len(emergency_contact) != 10:
        return jsonify({"message": "Emergency contact must be exactly 10 digits."}), 400
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Invalid email format."}), 400

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

@app.route('/uploads/profile_pics/<filename>')
def serve_profile_pic(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"message": "Profile picture not found."}), 404

@app.route('/user/<int:user_id>/dashboard', methods=['GET'])
@auth_required('token')
@user_required
def get_user_dashboard(user_id):
    user = User.query.get_or_404(user_id)
    profile_picture_url = None
    if user.profile_picture:
        normalized_path = user.profile_picture.replace("\\", "/")
        if normalized_path.startswith("uploads/"):
            profile_picture_url = f"{request.host_url}{normalized_path}"
        else:
            profile_picture_url = f"{request.host_url}uploads/{normalized_path}"

    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'uid': user.uid,
            'phone': user.phone,
            'address': user.address,
            'height': user.height,
            'weight': user.weight,
            'blood_group': user.blood_group,
            'emergency_contact': user.emergency_contact,
            'allergies': user.allergies,
            'notes': user.notes,
            'profile_picture': profile_picture_url,
            'roles': [role.name for role in user.roles],
        }
    })


@app.route('/user/<int:user_id>/dashboard/edit', methods=['POST'])
@auth_required('token')
@user_required
def edit_user_profile(user_id):
    if current_user.id != user_id:
        return jsonify({"message": "Unauthorized access."}), 403

    data = request.form
    name = data.get('name')
    email = data.get('email')
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
        save_path = os.path.join(UPLOAD_FOLDER, picture_filename)
        profile_picture.save(save_path)
        picture_path = os.path.normpath(f"profile_pics/{picture_filename}").replace("\\", "/")
    else:
        picture_path = current_user.profile_picture

    if not all([name, email, uid, phone, emergency_contact]):
        return jsonify({"message": "Required fields cannot be empty."}), 400

    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"message": "Phone number must be exactly 10 digits."}), 400
    if not uid.isdigit() or len(uid) != 11:
        return jsonify({"message": "UID must be exactly 11 digits."}), 400
    if not emergency_contact.isdigit() or len(emergency_contact) != 10:
        return jsonify({"message": "Emergency contact must be exactly 10 digits."}), 400
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Invalid email format."}), 400

    existing_email = User.query.filter(User.email == email, User.id != user_id).first()
    if existing_email:
        return jsonify({"message": "Email already in use by another user."}), 409

    existing_uid = User.query.filter(User.uid == uid, User.id != user_id).first()
    if existing_uid:
        return jsonify({"message": "UID already in use by another user."}), 409

    current_user.name = name
    current_user.email = email
    current_user.uid = uid
    current_user.phone = phone
    current_user.address = address
    current_user.height = height
    current_user.weight = weight
    current_user.blood_group = blood_group
    current_user.emergency_contact = emergency_contact
    current_user.allergies = allergies
    current_user.notes = notes
    current_user.profile_picture = picture_path

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating profile: {str(e)}"}), 500
