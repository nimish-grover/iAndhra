import os
import traceback
from dotenv import load_dotenv
from flask import Flask, request, session, url_for,render_template
from flask_migrate import Migrate
from flask_login import LoginManager
from app.models.users import User
from app.db import db
from app.routes.auth import blp as authBlueprint
from app.routes.desktop import blp as desktopBlueprint
from app.routes.mobile import blp as mobileBlueprint
from app.routes.developer import blp as developerBlueprint
from app.classes.helper import HelperClass
from werkzeug.exceptions import HTTPException
import logging
from logging.handlers import RotatingFileHandler



def create_app():
    app = Flask(__name__)
    load_dotenv()
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/error.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] in %(module)s: %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    # configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_master:w24JyTn0SIEHfS@144.24.103.183:5432/iAndhra_anantapur'
#PRODUCTION DB
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("JALAGAM_DATABASE_URL") #DEVELOPMENT DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # or 'Lax' or 'Strict'
    app.config['SESSION_COOKIE_SECURE'] = True  # Required if SameSite=None
    app.config['SECRET_KEY']="JAL_SECRET_KEY"

    # register db
    db.init_app(app)
    current_directory = os.getcwd()
    migrations_directory = current_directory + '/migrations'
    migrate = Migrate(app, db, directory=migrations_directory)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    #register jinja filters
    app.jinja_env.filters['indian_format'] = HelperClass.indian_number_format
    @app.context_processor
    def inject_theme_info():
        THEMES = {
        'purple': {
            'name': 'Purple Theme',
            'stylesheet': url_for('static',filename='scss/purple_theme.css')
        },
        'dark': {
            'name': 'Dark Theme',
            'stylesheet': url_for('static',filename='scss/dark_theme.css')
        },
        # 'orange': {
        #     'name': 'Orange Theme',
        #     'stylesheet': url_for('static',filename='scss/orange_theme.css')
        # },
        'pink': {
            'name': 'Pink Theme',
            'stylesheet': url_for('static',filename='scss/styles.css')
        }
        }
        current_theme = session.get('theme', 'purple')
        return {
            'current_theme': current_theme,
            'theme_stylesheet': THEMES[current_theme]['stylesheet'],
            'available_themes': THEMES
        }
    # # register blueprints
    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.warning(f"404 Not Found: {request.url}")
        return render_template('auth/error.html', 
                            error_code=404, 
                            error_message="Page Not Found", 
                            description="The page you are looking for does not exist."), 404

    # Error handler for 500 Internal Server errors
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"500 Error: {request.url} - {error}")
        return render_template('auth/error.html', 
                            error_code=500, 
                            error_message="Internal Server Error", 
                            description="Something went wrong on our end. Please try again later."), 500

    # General error handler for other errors
    @app.errorhandler(Exception)
    def handle_exception(error):
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return error
        # Print the traceback to the terminal
        traceback.print_exc()
        app.logger.error("Unhandled Exception", exc_info=error)
        app.logger.error(f"URL: {request.url}")
        app.logger.error(f"Payload: {session.get('payload', 'N/A')}")
        # Non-HTTP exceptions
        return render_template('auth/error.html', 
                            error_code=500, 
                            error_message="Unexpected Error", 
                            message = "Please report the bug in the feedback page with screenshot.",
                            description="An unexpected error occurred:"+str(error)), 500
    app.register_blueprint(authBlueprint, url_prefix="/auth")
    app.register_blueprint(desktopBlueprint, url_prefix="/panchayat")
    app.register_blueprint(mobileBlueprint)
    app.register_blueprint(developerBlueprint, url_prefix="/dev")

    return app