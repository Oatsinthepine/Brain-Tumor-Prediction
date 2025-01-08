# Brain Tumor Prediction app
This is a Flask web application allows users to upload medical images and predict whether a brain tumor is present and the potential class of tumor. 
The backend model was trained on medical imaging datasets obatined from kaggle website and leverages convolutional neural networks (CNN) to classify brain tumors.

### `Notion`: This is an improved version of the Project 4: Brain Tumor classification and detection using deep-learning models. 
### To view the original group project, please visit the pinned `Project4` repository in my github :)

## Improvements made:
I made several improvement after the completion of this group project. 
* Beyond simply showing users a plain, unstructured flask. I restructured the whole flask_app into several directories. Made the project structure neet and tidy.
* Polished HTML/CSS were applied to the corresponding file, which enhance the visual appeal for better aesthetics.
* The user registration, login, logout function implemented. This improves the user interaction and add one layer of security for better privacy.

### Project structure:
```plaintext
.
├── config.py            # Configuration settings for Flask app, not in repo
├── flask_app            # main Flask app folder
│   ├── __init__.py      # Initializes Flask app and extensions
│   ├── models.py        # Database models for the app
│   ├── routes.py        # Defines app routes
│   ├── static           # Static files like images, CSS, JS
│   └── templates        # HTML templates for rendering views
├── instance             # database file location
│   └── user.db          # database for user info
├── model_checkpoint_epoch_177.h5  # Pre-trained model for brain tumor detection
├── Procfile             # Specifies the command to run the app on Heroku
├── requirements.txt     # Python dependencies for the app
├── run.py               # Entry point for running the app locally
└── README.md            # Project documentation (this file)

```
## User guide:
use pip install -r requirement.txt to get dependencies.

