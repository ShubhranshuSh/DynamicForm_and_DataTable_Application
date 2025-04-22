from flask import current_app as app
from backend.models import db, User, Role
from flask_security import SQLAlchemyUserDatastore, hash_password

with app.app_context():
    db.create_all()

    userdatastore: SQLAlchemyUserDatastore = app.security.datastore

    userdatastore.find_or_create_role(name='admin', description='Admin')
    userdatastore.find_or_create_role(name='user', description='User')

    if not userdatastore.find_user(email='admin@admin.com'):
        userdatastore.create_user(
            name='Admin User',
            uid='12345678900',
            phone='1234567890',
            email='admin@admin.com',
            emergency_contact='0987654321',
            password=hash_password('admin123'),
            roles=['admin'],
        )

    if not userdatastore.find_user(email='user1@user.com') and not User.query.filter_by(uid='12345678901').first():
        userdatastore.create_user(
            name='John Doe',
            uid='12345678901',
            phone='1234567890',
            email='user1@user.com',
            address='123 Main St, City, Country',
            height='180 cm',
            weight='75 kg',
            blood_group='O+',
            emergency_contact='0987654321',
            allergies='None',
            notes='No special notes',
            password=hash_password('user123'),
            roles=['user'],
        )


    db.session.commit()