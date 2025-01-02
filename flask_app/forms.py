from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_app.models import User


class RegisterForm(FlaskForm):
    # When you define username = StringField(...) in your RegisterForm, WTForms knows that this field is named 'username', same as all the rest.
    # 在flask_wtf中，validate_<field_name> 是一个特殊的方法. Flask-WTF (through WTForms) automatically calls this method when validating the field specified in <fieldname> (e.g., username).
    username = StringField(label= "User Name", validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField(label="Email Address", validators=[DataRequired(), Email()])
    password_1 = PasswordField(label="New Password", validators=[DataRequired(), Length(min=8, max=24)])
    password_2 = PasswordField(label="Please re-confirm", validators=[
        DataRequired(), EqualTo('password_1', message="Password must match!")
    ])
    submit = SubmitField(label="create_account")


    def validate_username(self, username_to_check):
        #注意如果你这里filter_by()里面忘记.data的时候会报错，.data is the actual 'data' retrieved instead of the object.
        username = User.query.filter_by(username = username_to_check.data).first()
        if username:
            raise ValidationError("This username already used, please use another one.")

    def validate_email(self, email_to_check):
        email = User.query.filter_by(email = email_to_check.data).first()
        if email:
            raise ValidationError ("This email already exists, please use another one.")

class LoginForm(FlaskForm):
    username = StringField(label = "User Name", validators=[DataRequired()])
    password = PasswordField(label= "Enter your password", validators=[DataRequired()])
    submit = SubmitField(label="Sign in")
