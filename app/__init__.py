import os
from dotenv import load_dotenv
from flask import Flask, session, url_for,render_template
from flask_migrate import Migrate
from flask_login import LoginManager
from app.models.users import User
from app.db import db
from app.routes.auth import blp as authBlueprint
from app.routes.desktop import blp as desktopBlueprint
from app.routes.mobile import blp as mobileBlueprint
from app.classes.helper import HelperClass
from werkzeug.exceptions import HTTPException
def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    # configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_master:w24JyTn0SIEHfS@144.24.103.183:5432/iAndhra'
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
        return render_template('auth/error.html', 
                            error_code=404, 
                            error_message="Page Not Found", 
                            description="The page you are looking for does not exist."), 404

    # Error handler for 500 Internal Server errors
    @app.errorhandler(500)
    def internal_server_error(error):
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

        # Non-HTTP exceptions
        return render_template('auth/error.html', 
                            error_code=500, 
                            error_message="Unexpected Error", 
                            description="An unexpected error occurred:"+error), 500
    app.register_blueprint(authBlueprint, url_prefix="/auth")
    app.register_blueprint(desktopBlueprint, url_prefix="/panchayat")
    app.register_blueprint(mobileBlueprint)

    return app