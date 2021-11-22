'''

    app 主藍圖的路由

'''

from flask import render_template
from . import main
from ..movie_model import Movies
import random

@main.route('/')
def index():
    rowCount = int(Movies.query.count())
    movies = Movies.query.offset(int(rowCount * random.random())).limit(30)

    return render_template('main/index.html', movies = movies)

@main.route('/movies')
def movies():
    movies = Movies.query.limit(10)
    return render_template('main/movies.html', movies = movies)