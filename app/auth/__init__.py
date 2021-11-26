'''

    使用者認證相關視圖

'''

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views