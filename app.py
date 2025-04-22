from flask import Flask
from flask_cors import CORS
from backend.config import LocalDevelopmentConfig
from flask_security import auth_required
from backend.models import db , User , Role
from flask_security import Security, SQLAlchemyUserDatastore 


def createApp():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)


    datastore = SQLAlchemyUserDatastore(db, User , Role)
    app.security = Security(app, datastore=datastore , register_blueprint=False)
    app.app_context().push()
    return app

app = createApp()

import backend.create_init_data
import backend.routes

if (__name__ == "__main__"):
    app.run(debug=True)