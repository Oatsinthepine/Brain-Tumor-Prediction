import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate #get migrate here

# initialise extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate() #create the Migrate object

# this will redirect user to login page if not login
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__, template_folder='templates',static_folder='static')

    # from config import Configuration
    # app.config.from_object(Configuration) # load configuration

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MODEL_PATH"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'model_checkpoint_epoch_177.h5')


    # initialise extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db) # Bind Flask-Migrate to the app and SQLAlchemy

    # Register blueprints
    from flask_app.routes import main
    app.register_blueprint(main)

    return app