'''

    app 的錯誤處理

'''

from . import main
from flask import render_template

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html')

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html')