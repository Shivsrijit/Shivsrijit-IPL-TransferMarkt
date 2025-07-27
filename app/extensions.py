from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()

# Set up login manager
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info' 