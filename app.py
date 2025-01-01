# get all dependencies
import base64
import io
from PIL import Image
from flask import Flask
from flask import jsonify, render_template, url_for, request, redirect, flash, get_flashed_messages
from flask_cors import CORS # this dependency is required to deal with the CORS issue
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import img_to_array

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError



app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "http://127.0.0.1:5000"}}) # for security concerns, only allow the predict html page to enable CORS, for the project only.

#db configuration:
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = "3Dfb8MHWa3sp2F62"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __table_name__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable = False)
    password = db.Column(db.String(100), nullable = False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class RegisterForm(FlaskForm):
    # When you define username = StringField(...) in your RegisterForm, WTForms knows that this field is named 'username', same as all the rest.
    username = StringField(label= "User Name", validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField(label="Email Address", validators=[DataRequired(), Email()])
    password_1 = StringField(label="New Password", validators=[DataRequired(), Length(min=8, max=24)])
    password_2 = StringField(label="Please re-confirm", validators=[
        DataRequired(), EqualTo('password_1', message="Password must match!")
    ])
    submit = SubmitField(label="create_account")


#在flask_wtf中，validate_<field_name> 是一个特殊的方法. Flask-WTF (through WTForms) automatically calls this method when validating the field specified in <fieldname> (e.g., username).

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
    password = StringField(label= "Enter your password", validators=[DataRequired()])
    submit = SubmitField(label="Sign in")



@app.route('/')
def base_page():
    return render_template("base.html")


@app.route('/register', methods=["GET", "POST"])
def register_account():
    # step1: instantiate RegisterForm first
    form = RegisterForm()
    if form.validate_on_submit():
        """
        During form validation (form.validate_on_submit()), WTForms automatically checks for a method named validate_<field_name>. 
        If it finds one, it passes the field object (form.<field_name>) as the argument to the method.
        """
        user_to_create = User(username = form.username.data,
                              email = form.email.data,
                              password = form.password_2.data)
        try:
            db.session.add(user_to_create)
            db.session.commit()
            flash("New Account Created Successfully!", category = 'success')
            return redirect(url_for("predict"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error occurred: {e}", category='danger')

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", category="danger")

    return render_template("register.html", form=form)


@app.route('/login')
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        curr_user = User.query.filter_by(username=login_form.username.data).first()
        if curr_user and curr_user.check_password_match(login_form.password.data):
            pass


def get_model():
    global model
    model = load_model("model_checkpoint_epoch_177.h5") # change the path here for your local path when accessing this .h5 model file.
    print("model successfully loaded.") # when you run flask, if successful, you should see this message print in the terminal.

def preprocess_image(img, traget_size = (256, 256)):
    if img.mode != "L":
        img = img.convert("L") # L means grayscale
    img = img.resize(traget_size) # if user image is not in correct size, resize it here.
    img_array = img_to_array(img)

    # need to implement rescaling here, by dividing 255 to convert the numpyfied array, to reach the result between 0 and 1.
    img_array_scaled = img_array / 255.0

    img_array = np.expand_dims(img_array_scaled, axis=0)

    return img_array

print("==========>> Loading keras model...")

# invoke the model function and get the model object.
get_model()


@app.route("/tumor_predict", methods = ['GET', 'POST'])
def core_func(): # here is the predict function for user
    message = request.get_json(force=True)
    encoded = message['image'] # file passed in need to be image format
    decoded = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(decoded))
    processed_image = preprocess_image(image, traget_size=(256, 256))

    # here use the model to predict the user uploaded image file
    prediction = model.predict(processed_image)
    # here, to directly access the predicted probabilities. use index slicing to reterive the result.
    # As model.predict() returns 2D np.array which first dim contains batch_size info. we don't need this.
    predicted_probabilities = prediction[0]

    # create a dictionary to hold all returned classes probabilities.
    # here the index co-respond to the classes.
    response = {
        'Prediction': {
            "glioma_tumor": f"{round(float(predicted_probabilities[0]) * 100, 2)}%",
            "meningioma_tumor": f"{round(float(predicted_probabilities[1]) * 100, 2)}%",
            "no_tumor": f"{round(float(predicted_probabilities[2]) * 100, 2)}%",
            # "pituitary_tumor": f"{round(float(predicted_probabilities[3]) * 100,2)}%" # U-Net model did not trained on this class, so comment it out
        }
    }

    return jsonify(response)

# here is the flask url for using the backend model to predict user uplaoded image file
@app.route("/predict")
def predict():
    # call the flask build-in method to render my predict_to_be_changed.html webpage.
    return render_template("predict.html")



# use app.run to start flask server
if __name__ == "__main__":
    app.run(debug=True)