'''

    app 主藍圖的路由

'''

from flask import render_template, request, redirect
from flask.helpers import flash, url_for
from sqlalchemy import or_
from . import main
from ..movie_model import Movies, TopRankMoives, PopularMovies, Generes
from ..user_model import Comments
import random
from ..app_function import sort_movies, sort_need_join_movies
from app import db
from flask_login import current_user

@main.app_context_processor
def inject_movie_geners():
    genres = Generes.genres_set
    return dict(genres = genres)

# TODO 重構 排序程式

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
    
    if sort_type:
        pagination = sort_movies(sort_type=sort_type, desc=desc).paginate(page, per_page = 10, error_out = False)
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

    if sort_type:
        pagination = sort_need_join_movies(TopRankMoives, sort_type=sort_type, desc=desc).paginate(page, per_page = 10, error_out = False)
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

    if sort_type:
        pagination = sort_need_join_movies(PopularMovies, sort_type=sort_type, desc=desc).paginate(page, per_page = 10, error_out = False)
    else:
        pagination = Movies.query.join(
            PopularMovies, Movies.tmdb_id == PopularMovies.tmdb_id
            ).order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
    movies = pagination.items
    return render_template('main/popular.html', pagination = pagination, page = page, movies = movies, args = args)


@main.route('/movies/<int:id>', methods = ['GET', 'POST'])
def movie(id):
    ''' 電影詳細資料路由 '''

    movie = Movies.query.get_or_404(id)

    similar_movie_numbers = 8   # 相似電影的數量 ( 4 * 2 )

    similar_title = Movies.query.filter(

        or_(
        (Movies.title.like(f'%{movie.title}%')),
        (Movies.original_title.like(f'%{movie.original_title}%'))
        )
    ).limit(similar_movie_numbers).all()

    if not similar_title or len(similar_title) < similar_movie_numbers:
        movie_genre = movie.genres.split(',')[0]
        rowCount = int(Movies.query.filter(Movies.genres.like(f'%{movie_genre}%')).count())
        similar_genre = Movies.query.filter(
            Movies.genres.like(f'%{movie_genre}%')
        ).offset(int(rowCount * random.random())).limit(similar_movie_numbers - len(similar_title)).all()
    else:
        similar_genre = []

    similar_movies = similar_title
    similar_movies.extend(similar_genre)

            
    if request.method == 'POST':
        comment_data = request.form.get('comment')
        comment = Comments(body = comment_data, movie = movie, user = current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('評論已經送出')

        return redirect(url_for('main.movie', id = id))

    comments = movie.comments.order_by(Comments.timestamp.desc()).all()

    return render_template('main/movie.html', movie = movie, comments = comments, similar_movies = similar_movies)

@main.route('/search',)
def search():
    ''' 搜尋路由 '''

    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    search_key = request.args.get('key')

    pagination_args = {'sort' : sort_type, 'desc' : desc, 'key' : search_key}
    sort_args = {'key' : search_key}

    if not search_key:
        return redirect(request.referrer)

    if sort_type == 'rate':
        if desc:
            pagination = Movies.query.filter(
                or_( 
                ( Movies.title.like(f'%{search_key}%') ), 
                ( Movies.original_title.like(f'%{search_key}%') )
                )
            ).order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.filter(
                or_( 
                ( Movies.title.like(f'%{search_key}%') ), 
                ( Movies.original_title.like(f'%{search_key}%') )
                )
            ).order_by(Movies.vote_average).paginate(page, per_page = 10, error_out = False)
    elif sort_type == 'year':
        if desc:
            pagination = Movies.query.filter(
                    or_( 
                    ( Movies.title.like(f'%{search_key}%') ), 
                    ( Movies.original_title.like(f'%{search_key}%') )
                    )
                ).order_by(Movies.release_date.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.filter(
                    or_( 
                    ( Movies.title.like(f'%{search_key}%') ), 
                    ( Movies.original_title.like(f'%{search_key}%') )
                    )
                ).order_by(Movies.release_date).paginate(page, per_page = 10, error_out = False)
    else:

        pagination = Movies.query.filter(
            or_( 
                ( Movies.title.like(f'%{search_key}%') ), 
                ( Movies.original_title.like(f'%{search_key}%') )
                )
            ).order_by(Movies.original_title).paginate(page, per_page = 10, error_out = False)
    
    movies = pagination.items

    return render_template('main/search.html', movies = movies, pagination = pagination, sort_args = sort_args, pagination_args = pagination_args)

@main.route('/movies/<genre>')
def movie_genre(genre):
    ''' 電影分類路由 '''


    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')

    pagination_args = {'sort' : sort_type, 'desc' : desc, 'genre' : genre}
    sort_args = {'genre' : genre}

    if sort_type == 'rate':
        if desc:
            pagination = Movies.query.filter(
                Movies.genres.like(f'%{genre}%')
            ).order_by(
                Movies.vote_average.desc()
            ).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.filter(
                Movies.genres.like(f'%{genre}%')
            ).order_by(
                Movies.vote_average
            ).paginate(page, per_page = 10, error_out = False)
    elif sort_type == 'year':
        if desc:
            pagination = Movies.query.filter(
                Movies.genres.like(f'%{genre}%')
            ).order_by(
                Movies.release_date.desc()
            ).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = Movies.query.filter(
                Movies.genres.like(f'%{genre}%')
            ).order_by(
                Movies.release_date
            ).paginate(page, per_page = 10, error_out = False)
    else:
        pagination = Movies.query.filter(
            Movies.genres.like(f'%{genre}%')
        ).order_by(Movies.original_title).paginate(page, per_page = 10, error_out = False)

    movies = pagination.items

    return render_template('main/movie_gener.html', movies = movies, genre = genre, pagination = pagination, pagination_args = pagination_args, sort_args = sort_args)