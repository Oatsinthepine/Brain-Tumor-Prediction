from flask_app import db, bcrypt
from flask_login import UserMixin



class User(db.Model, UserMixin):
    """
    By inheriting from UserMixin, the following properties are automatically added to User class:
	•	is_authenticated: Returns True if the user is logged in.
	•	is_active: Returns True by default unless overridden.
	•	is_anonymous: Returns False for logged-in users.
	•	get_id(): Used to retrieve the user ID, which is required for session management.
    """
    __table_name__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable = False)
    password = db.Column(db.String(100), nullable = False)

    #here for security reason, let's implement a hashed password via the flask_bcrypt module
    def set_password(self, plain_password):
        self.password = bcrypt.generate_password_hash(plain_password).decode('utf-8') # hey why decode here? aren't we encoding password?

    def check_password_match(self, user_entered_password):
        return bcrypt.check_password_hash(self.password, user_entered_password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
