from flask import Flask
from flasgger import Swagger
from dotenv import load_dotenv
import os

from app.config import Config, DevelopmentConfig, ProductionConfig

from .auth.routes import auth_bp
from .cows.routes import cow_bp
from .admin.routes import admin_bp
from .user_profile.routes import user_bp
from .mLmodel.routes import predict_bp
from .home.routes import home_bp
from .disease_prediction.routes import pred_bp
from .cronjob.scheduler import start_sensor_scheduler
from .utils.logger import setup_logger
from .firebase_config import *


def create_app():
    load_dotenv()
    app = Flask(__name__)

    
    env = os.getenv('FLASK_ENV', 'production')
    if env == 'development':
            app.config.from_object(DevelopmentConfig)
    else:
            app.config.from_object(ProductionConfig)


    Swagger(app)

    setup_logger()
    start_sensor_scheduler()


    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cow_bp ,url_prefix='/cows')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(predict_bp, url_prefix='/predict')
    app.register_blueprint(home_bp, url_prefix='/home')
    app.register_blueprint(pred_bp, url_prefix='/predict')

    @app.route('/')
    def index():
        return "Welcome to Cowly"

    return app
