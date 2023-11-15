from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_by_name
from flask_limiter import Limiter
import os
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_migrate import Migrate
from logging.config import dictConfig

# Create the SQLAlchemy database object
db = SQLAlchemy()

# Create the rate limiter object
limiter = Limiter(key_func=get_remote_address)

# load the environment variables from the .env file
load_dotenv()

# Get the OpenAI API key from the environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

def create_app():
    app = Flask(__name__)

    config_name = os.getenv('FLASK_CONFIG') or 'dev'

    # Load configuration from a configuration file
    app.config.from_object(config_by_name[config_name])

    # Initialize the database with the Flask app
    db.init_app(app)

    # Initalize the rate limiter
    limiter.init_app(app)

    # Configure logging
    configure_logging(app)

    # Initialize migrate command 
    migrate = Migrate(app, db)

    # Register the blueprints for your API routes
    from app.controllers.openai_controller import openai_api
    app.register_blueprint(openai_api)

    # Create the database (if it doesn't exist)
    with app.app_context():
        db.create_all()

    return app


def configure_logging(app):
    log_folder = os.path.join(app.root_path, 'logs')
    os.makedirs(log_folder, exist_ok=True)

    log_file_path = os.path.join(log_folder, 'app.log')
    error_log_file_path = os.path.join(log_folder, 'error.log')

    logging_config = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'info_file_handler': {
                'class': 'logging.FileHandler',
                'filename': log_file_path,
                'level': 'DEBUG',
                'formatter': 'default',
            },
            'error_file_handler': {
                'class': 'logging.FileHandler',
                'filename': error_log_file_path,
                'level': 'ERROR',
                'formatter': 'default',
            },
        },
        'loggers': {
            '': {
                'handlers': ['info_file_handler'],
                'level': 'DEBUG',
            },
            'error_logger': {
                'handlers': ['error_file_handler'],
                'level': 'ERROR',
            },
        },
    }

    dictConfig(logging_config)