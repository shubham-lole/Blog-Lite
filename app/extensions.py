from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
login_manager = LoginManager()