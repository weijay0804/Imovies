'''

    使用者相關視圖

'''

from flask import Blueprint

user = Blueprint('user', __name__)

from . import views