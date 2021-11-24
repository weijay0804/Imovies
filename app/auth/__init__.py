'''

    使用者相關視圖

'''

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views