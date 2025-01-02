from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


# initialise extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
# this will redirect user to login page if not login
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__, template_folder='templates',static_folder='static')
    app.config.from_object('config.Configuration') # load configuration

    # initialise extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from flask_app.routes import main
    app.register_blueprint(main)

    return app