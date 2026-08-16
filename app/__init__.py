from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Login manager settings
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints (we'll use direct routes for simplicity)
    from app import routes
    app.register_blueprint(routes.routes)
    
    return app

# Import models at the end to avoid circular imports
from app import models