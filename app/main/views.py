'''

    app 主藍圖的路由

'''

import random
from flask import render_template, request, redirect, flash, url_for
from sqlalchemy import or_
from flask_login import current_user
from app import db
from . import main
from ..movie_model import Movies, TopRankMoives, PopularMovies, Generes
from ..user_model import Comments
from ..app_function import sort_movies, sort_need_join_movies


@main.app_context_processor
def inject_movie_geners():
    ''' 讓模板可以讀取到電影類別的資料 '''

    genres = Generes.genres_set
    return dict(genres = genres)


@main.route('/')
def index():
    ''' 主頁面 '''

    # 隨機取資料，確保取出的電影每次都不同
    rowCount = int(Movies.query.count())
    movies = Movies.query.offset(int(rowCount * random.random())).limit(30)

    # TODO 客製化推薦電影

    movie_genres = Generes.genres_set.copy()   # 電影類別

    if '電視電影' in movie_genres:
        movie_genres.remove('電視電影')

    ra_numbers = random.sample(range(0, len(movie_genres)) ,3)  # 產生 3 個隨機數字當 index

    recommend_movies = []
    recommend_genres = []

    for index, genrs_index in enumerate(ra_numbers):
        genre = movie_genres[genrs_index]

        re_movies = Movies.query.filter(Movies.genres.like(f'%{genre}%')).limit(10).all()


        recommend_movies.append(list(re_movies))
        recommend_genres.append(genre)

    return render_template('main/index.html', movies = movies, recommend_movies = recommend_movies, recommend_genres = recommend_genres)


@main.route('/movies')
def movies():
    ''' 所有電影路由 '''
    
    # 取得 url 的參數
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    args = {'sort' : sort_type, 'desc' : desc}
    
    # 排序電影
    if sort_type:
        pagination = sort_movies(sort_type=sort_type, desc=desc).paginate(page, per_page = 10, error_out = False)
    else:
        pagination = Movies.query.paginate(page, per_page = 10, error_out = False)
    movies = pagination.items

    return render_template('main/movies.html', movies = movies, pagination = pagination, page = page,  args = args)

@main.route('/top250')
def top250():
    ''' imdb top 250 電影 '''

    # 取得 url 的參數
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    args = {'sort' : sort_type, 'desc' : desc}

    # 排序電影
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

    # 取得 url 的參數
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    args = {'sort' : sort_type, 'desc' : desc}

    # 排序電影
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

    # 將電影名稱以 : 分割
    movie_title = movie.title.split('：')[0]    
    movie_original_title = movie.original_title.split(':')[0]

    # 用分割後的電影名稱去資料庫尋找
    similar_title = Movies.query.filter(
        or_(
        (Movies.title.like(f'%{movie_title}%')),
        (Movies.original_title.like(f'%{movie_original_title}%'))
        )
    ).limit(similar_movie_numbers).all()

    # 如果沒有找到或數量不夠時，用電影的類別去尋找
    # 使用 offset 隨機取資料
    if not similar_title or len(similar_title) < similar_movie_numbers:
        movie_genre = movie.genres.split(',')[0]
        rowCount = int(Movies.query.filter(Movies.genres.like(f'%{movie_genre}%')).count())
        similar_genre = Movies.query.filter(
            Movies.genres.like(f'%{movie_genre}%')
        ).offset(int(rowCount * random.random())).limit(similar_movie_numbers - len(similar_title)).all()
    else:
        similar_genre = []

    # 將找到的資料合併成一個 list
    similar_movies = similar_title
    similar_movies.extend(similar_genre)

    
    # 處理表單
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

    # 取得 url 參數
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')
    search_key = request.args.get('key')

    pagination_args = {'sort' : sort_type, 'desc' : desc, 'key' : search_key}
    sort_args = {'key' : search_key}

    # 如果搜尋框沒有輸入東西就導回之前的頁面
    if not search_key:
        return redirect(request.referrer)

    # 排序電影
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


    # 取得 url 參數
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')

    pagination_args = {'sort' : sort_type, 'desc' : desc, 'genre' : genre}
    sort_args = {'genre' : genre}

    # 排序電影
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