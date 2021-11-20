'''

    app 的錯誤處理

'''

from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return '<h1> 404 </h1>'