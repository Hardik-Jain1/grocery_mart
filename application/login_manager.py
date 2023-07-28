from flask_login import LoginManager
from flask import current_app as app

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'