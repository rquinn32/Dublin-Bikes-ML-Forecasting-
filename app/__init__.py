from flask import Flask
from config import Config
from flask_login import LoginManager
from config import DevelopmentConfig
from app.services.user_class import get_user_by_id, create_user

# Initialise Flask Login manager
login_manager = LoginManager()
login_manager.login_view = "auth.login" #Redirect here if user is not logged in


def create_app(config_class=Config):
    """Application factory function to create app instances"""
    
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)

    # initialize flask-login
    login_manager.init_app(app)

    # Register blueprints
    from .main.routes import main_bp
    from .auth.routes import auth_bp

    app.register_blueprint(main_bp) # this will be at the root directory, so I don't need the url_prefix
    app.register_blueprint(auth_bp, url_prefix="/auth")


    return app


@login_manager.user_loader
def load_user(user_id):
    """Given a user ID, return the corresponding user object"""
    return get_user_by_id(user_id)
