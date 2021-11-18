"""

    app 設定檔

"""

import os
from dotenv import load_dotenv

load_dotenv()



class Config():
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASEDIR = os.path.abspath(os.path.dirname(__file__))


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig
}
