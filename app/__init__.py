'''

    app 工廠函式

'''

from flask import Flask, config
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_moment import Moment
from config import config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
db = SQLAlchemy()
csrf = CSRFProtect()
moment = Moment()

def create_app(config_name : str) -> Flask:
    ''' 創建一個 app 實體 '''

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix = '/auth')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix = '/user')

    return app