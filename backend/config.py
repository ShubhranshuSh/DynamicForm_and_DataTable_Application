class Config():
    DEBUG = False
    SQL_ALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SECURITY_PASSWORD_SALT = 'thisshouldbekeptsecret'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECRET_KEY = "shouldbekepthidden"
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'