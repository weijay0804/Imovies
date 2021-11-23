'''

    app 主藍圖的路由

'''

from flask import render_template, request, redirect
from sqlalchemy import or_
from . import main
from ..movie_model import Movies, TopRankMoives, PopularMovies
import random

@main.route('/')
def index():
    rowCount = int(Movies.query.count())
    movies = Movies.query.offset(int(rowCount * random.random())).limit(30)

    return render_template('main/index.html', movies = movies)


@main.route('/movies')
def movies():
    ''' 所有電影路由 '''
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    args = {'sort' : sort_type, 'desc' : desc}
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

    return render_template('main/movies.html', movies = movies, pagination = pagination, page = page,  args = args)

@main.route('/top250')
def top250():
    ''' imdb top 250 電影 '''

    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    args = {'sort' : sort_type, 'desc' : desc}

    if sort_type == 'rate':
        if desc:
            pagination = Movies.query.join(
                TopRankMoives, Movies.tmdb_id == TopRankMoives.tmdb_id
                ).order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.join(
                TopRankMoives, Movies.tmdb_id == TopRankMoives.tmdb_id
                ).order_by(Movies.vote_average).paginate(page, per_page = 10, error_out = False)
    elif sort_type == 'year':
        if desc:
            pagination = Movies.query.join(
                TopRankMoives, Movies.tmdb_id == TopRankMoives.tmdb_id
                ).order_by(Movies.release_date.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.join(
                TopRankMoives, Movies.tmdb_id == TopRankMoives.tmdb_id
                ).order_by(Movies.release_date).paginate(page, per_page = 10, error_out = False)
    else:
        pagination = Movies.query.join(
            TopRankMoives, Movies.tmdb_id == TopRankMoives.tmdb_id
            ).order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
    movies = pagination.items
    return render_template('main/top250.html', pagination = pagination, page = page, movies = movies, args = args)

@main.route('/popular')
def popular():
    ''' 熱門電影 '''

    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    args = {'sort' : sort_type, 'desc' : desc}

    if sort_type == 'rate':
        if desc:
            pagination = Movies.query.join(
                PopularMovies, Movies.tmdb_id == PopularMovies.tmdb_id
                ).order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.join(
                PopularMovies, Movies.tmdb_id == PopularMovies.tmdb_id
                ).order_by(Movies.vote_average).paginate(page, per_page = 10, error_out = False)
    elif sort_type == 'year':
        if desc:
            pagination = Movies.query.join(
                PopularMovies, Movies.tmdb_id == PopularMovies.tmdb_id
                ).order_by(Movies.release_date.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.join(
                PopularMovies, Movies.tmdb_id == PopularMovies.tmdb_id
                ).order_by(Movies.release_date).paginate(page, per_page = 10, error_out = False)
    else:
        pagination = Movies.query.join(
            PopularMovies, Movies.tmdb_id == PopularMovies.tmdb_id
            ).order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
    movies = pagination.items
    return render_template('main/popular.html', pagination = pagination, page = page, movies = movies, args = args)


@main.route('/movies/<int:id>')
def movie(id):
    ''' 電影詳細資料路由 '''

    movie = Movies.query.get_or_404(id)

    return render_template('main/movie.html', movie = movie)

@main.route('/search', methods = ['POST'])
def search():
    ''' 搜尋路由 '''

    if request.method == 'POST':
        search_key = request.form.get('key')
        if not search_key:
            return redirect(request.referrer)
        
        movies = Movies.query.filter(
            or_( 
                ( Movies.title.like(f'%{search_key}%') ), 
                ( Movies.original_title.like(f'%{search_key}%') )
                )
            ).order_by(Movies.original_title).all()

        return render_template('main/search.html', movies = movies)

