from flask_app import create_app
from flask_app.models import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Databases initialised successfully")