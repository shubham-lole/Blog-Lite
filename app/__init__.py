from flask import Flask
from config import Config
from app.extensions import db, login_manager, Bootstrap

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    with app.app_context():
        db.create_all()
    login_manager.init_app(app)
    Bootstrap(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

#    @app._got_first_request
#    db.create_all()

    return app
