import os

class Configuration:
    SECRET_KEY = '3Dfb8MHWa3sp2F62'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'user.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = os.path.join(BASE_DIR, 'model_checkpoint_epoch_177.h5')
