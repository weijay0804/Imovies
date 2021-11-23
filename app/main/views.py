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
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    if sort_type == 'rate':
        if desc:
            pagination = Movies.query.order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.order_by(Movies.vote_average).paginate(page, per_page = 10, error_out = False)
    elif sort_type == 'year':
        if desc:
            pagination = Movies.query.order_by(Movies.release_date.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.order_by(Movies.release_date).paginate(page, per_page = 10, error_out = False)
    else:
        pagination = Movies.query.paginate(page, per_page = 10, error_out = False)
    movies = pagination.items

    return render_template('main/movies.html', movies = movies, pagination = pagination, sort_type = sort_type, desc = desc)