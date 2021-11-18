'''

    imovies 主腳本


'''

import os
from app import create_app, db
from flask_migrate import Migrate
from app.model import Movies, PopularMovies


app = create_app('development')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db = db, Movies = Movies, PopularMovies = PopularMovies)

