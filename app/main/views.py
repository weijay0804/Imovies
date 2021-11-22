'''

    app 主藍圖的路由

'''

from flask import render_template, request
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
    page = request.args.get('page', 1, type=int)
    rowCount = int(Movies.query.count())
    pagination = Movies.query.paginate(page, per_page = 10, error_out = False)
    movies = pagination.items

    
    return render_template('main/movies.html', movies = movies, pagination = pagination)