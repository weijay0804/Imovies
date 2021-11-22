'''

    app 主藍圖的路由

'''

from flask import render_template, request, redirect
from flask.helpers import make_response, url_for
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
    
    pagination = Movies.query.order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
    movies = pagination.items

    return render_template('main/movies.html', movies = movies, pagination = pagination)