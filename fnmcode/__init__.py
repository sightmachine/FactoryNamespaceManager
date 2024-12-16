import os
import sys
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_simple_captcha import CAPTCHA

current_file_path = os.path.abspath(__file__)
project_dir = os.path.dirname(current_file_path)
env_file = os.path.join(project_dir, "vars.env")
templates_dir = os.path.join(project_dir, "templates")

if project_dir not in sys.path:
    sys.path.append(project_dir)

# Read the environment variables from the file
with open(env_file, "r") as f:
    for line in f:
        key, value = line.strip().split("=")
        os.environ[key] = value

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
SIMPLE_CAPTCHA = CAPTCHA({
        'SECRET_CAPTCHA_KEY': 'LONG_KEY',
        'CAPTCHA_LENGTH': 6,
        'CAPTCHA_DIGITS': False,
        'EXPIRE_SECONDS': 600,
    })  # Define it globally to be accessible within create_app



def create_app(app):
    global SIMPLE_CAPTCHA
    db.init_app(app)

    app = SIMPLE_CAPTCHA.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Initialize SocketIO

    from fnmcode.models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from fnmcode.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from fnmcode.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app