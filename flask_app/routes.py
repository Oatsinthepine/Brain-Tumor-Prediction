import io
import base64
from PIL import Image
import numpy as np

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_app import db, login_manager
from flask_app.models import User
from flask_app.forms import RegisterForm, LoginForm
from flask_login import login_user, logout_user, login_required
from flask import request, jsonify


from keras.models import load_model
from keras.preprocessing.image import img_to_array


main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register_account():
    # step1: instantiate RegisterForm first
    form = RegisterForm()
    if form.validate_on_submit():
        """
        During form validation (form.validate_on_submit()), WTForms automatically checks for a method named validate_<field_name>. 
        If it finds one, it passes the field object (form.<field_name>) as the argument to the method.
        """
        user_to_create = User(
            username=form.username.data,
            email=form.email.data
        )
        user_to_create.set_password(form.password_2.data)
        try:
            db.session.add(user_to_create)
            db.session.commit()
            flash("New Account Created Successfully!", category='success')
            return redirect(url_for("main.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error occurred: {e}", category='danger')

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", category="danger")

    return render_template("register.html", form=form)

@main.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        curr_user = User.query.filter_by(username=login_form.username.data).first()
        if curr_user and curr_user.check_password_match(login_form.password.data):
            login_user(curr_user)
            flash(f"Login Successfully! login as {curr_user.username}.", category='success')
            return redirect(url_for('main.predict'))
        elif not curr_user:
            flash("Invalid username!", category='danger')
        else:
            flash("Incorrect password, please try again!", category='danger')
    return render_template('login.html', login_form=login_form)


@main.route('/logout')
def logout():
    logout_user()
    flash(f"You have logged out successfully!", category="info")
    return redirect(url_for("main.home"))


# here below is using U-Net model to predict passed files.
def get_model():
    global model
    # globals() checks the all global variables during runtime, this ensures get_modl() only execute once.
    if 'model' not in globals():
        with current_app.app_context():
            model_path = current_app.config["MODEL_PATH"]
            model = load_model(filepath=model_path) # change the path here for your local path when accessing this .h5 model file.
            print("model successfully loaded.") # when you run flask, if successful, you should see this message print in the terminal.
    return model


def preprocess_image(img, target_size = (256, 256)):
    if img.mode != "L":
        img = img.convert("L") # L means grayscale
    img = img.resize(target_size) # if user image is not in correct size, resize it here.
    img_array = img_to_array(img)

    # need to implement rescaling here, by dividing 255 to convert the Numpyfied array, to reach the result between 0 and 1.
    img_array_scaled = img_array / 255.0

    img_array = np.expand_dims(img_array_scaled, axis=0)

    return img_array



@main.route("/tumor_predict", methods = ['GET', 'POST'])
def core_predict_func(): # here is the predict function
    message = request.get_json(force=True)
    encoded = message['image'] # file passed in need to be image format
    decoded = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(decoded))
    processed_image = preprocess_image(image, target_size=(256, 256))

    # here use the model to predict the user uploaded image file.
    # invoke the model function and get the model object.
    prediction = get_model().predict(processed_image)
    # To directly access the predicted probabilities. use index slicing to get result.
    # As model.predict() returns 2D np.array which first dim contains batch_size info. we don't need this.
    predicted_probabilities = prediction[0]

    # create a dictionary to hold all returned classes probabilities.
    # here the index correspond to the classes.
    response = {
        'Prediction': {
            "glioma_tumor": f"{round(float(predicted_probabilities[0]) * 100, 2)}%",
            "meningioma_tumor": f"{round(float(predicted_probabilities[1]) * 100, 2)}%",
            "no_tumor": f"{round(float(predicted_probabilities[2]) * 100, 2)}%",
        }
    }

    return jsonify(response)

# here is the flask url for using the backend model to predict user upload image file
@main.route("/predict")
@login_required
def predict():
    # call the flask build-in method to render my predict_to_be_changed.html webpage.
    return render_template("predict.html")

