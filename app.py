# get all dependencies
import base64
import io
from PIL import Image
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template, url_for
from flask_cors import CORS # this dependency is required to deal with the CORS issue
import numpy as np
import tensorflow as tf
from psutil import users
from tensorflow import keras
from keras import backend as K
from keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator # remove tensorflow from here if not needed.
from keras.preprocessing.image import img_to_array
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "http://127.0.0.1:5000"}}) # for security concerns, only allow the predict html page to enable CORS, for the project only.

#db configuration:
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __table_name__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable = False)
    password = db.Column(db.String(100), nullable = False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


@app.route('/')
def base_page():
    # return "This is the home page. For using the model to predict your image, please visit: 'http://127.0.0.1:5000/predict'"
    return render_template("base.html")


@app.route('/test')
def running():
    return "Flask is running!" # if you see this, them means the backend flask server is running normally.

@app.route('/register')
def register_account():
    return render_template("register.html")






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