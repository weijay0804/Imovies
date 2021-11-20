'''

    app 主視圖

'''

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors