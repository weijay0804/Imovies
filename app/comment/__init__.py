'''

    app 評論相關藍圖

'''

from flask import Blueprint

comment = Blueprint('comment', __name__)

from . import views