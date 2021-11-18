'''

    app 工廠函式

'''

from flask import Flask, config
from flask_sqlalchemy import SQLAlchemy
from config import config


db = SQLAlchemy()

def create_app(config_name : str) -> Flask:
    ''' 創建一個 app 實體 '''

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    return app