'''

    app 工廠函式

'''

from flask import Flask, config
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import config


db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(config_name : str) -> Flask:
    ''' 創建一個 app 實體 '''

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    csrf.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix = '/auth')

    return app