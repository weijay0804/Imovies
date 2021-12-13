'''

    app 主藍圖的路由

'''

import os
import random
import json
import requests
from flask import render_template, request, redirect
from sqlalchemy import or_
from flask_login import current_user
from dotenv import load_dotenv
from . import main
from ..movie_model import Movies, TopRankMoives, PopularMovies, Generes
from ..user_model import Comments
from ..app_function import sort_movies, sort_need_join_movies

load_dotenv()

@main.app_context_processor
def inject_movie_geners():
    ''' 讓模板可以讀取到電影類別的資料 '''

    genres = Generes.genres_set
    return dict(genres = genres)


@main.route('/')
def index():
    ''' 主頁面 '''

    # 隨機取資料，確保取出的電影每次都不同
    rowCount = int(Movies.query.count()) - 30
    movies = Movies.query.offset(int(rowCount * random.random())).limit(30)


    movie_genres = Generes.genres_set.copy()   # 電影類別，使用深複製

    # 移除 電視電影類別 因為電影太少
    if '電視電影' in movie_genres:
        movie_genres.remove('電視電影')

    recommend_movies = []   # 儲存推薦的電影
    recommend_genres = []   # 儲存推薦電影的類別

    # 如果使用者登入並且使用者有勾選喜歡的電影類別，就使用使用者勾選的電影類別查詢
    if current_user.is_authenticated and current_user.favorite_movie_genres:
        
        # 將使用者喜歡的類別轉換成 list
        user_genres = current_user.favorite_movie_genres.split(',')

        # 3 是頁面上要顯示的電影類別數量
        if len(user_genres) > 3:

            # 如果使用者喜歡的類別數量大於 3 ，就隨機取 3 個類別
            ra_number = random.sample(range(0, len(user_genres)), 3)
            for ra in ra_number:
                recommend_genres.append(user_genres[ra])
        else:
            recommend_genres.extend(user_genres)
        
        # 使用使用者喜歡的電影類別查詢，並用 offset 確保隨機
        for genre in recommend_genres:
            rowCount = int(Movies.query.filter(Movies.genres.like(f'%{genre}%')).count()) - 10
            if rowCount < 0:
                user_re_movies = Movies.query.filter(Movies.genres.like(f'%{genre}%')).all()
            else:
                user_re_movies = Movies.query.filter(Movies.genres.like(f'%{genre}%')).offset(int(rowCount * random.random())).limit(10).all()
            recommend_movies.append(list(user_re_movies))

    # 如果使用者選取的電影數量小於 3，或使用者沒有登入
    if len(recommend_genres) < 3:

        # 產生 3 個隨機數字當 index
        ra_numbers = random.sample(range(0, len(movie_genres)) ,3 - len(recommend_genres)) 

        # 使用隨機存取的電影類別查詢，使用 offset 卻保隨機
        for genrs_index in ra_numbers:
            genre = movie_genres[genrs_index]

            rowCount = int(Movies.query.filter(Movies.genres.like(f'%{genre}%')).count()) - 10
            if rowCount < 0:
                re_movies = Movies.query.filter(Movies.genres.like(f'%{genre}%')).all()
            else:
                re_movies = Movies.query.filter(Movies.genres.like(f'%{genre}%')).offset(int(rowCount * random.random())).limit(10).all()

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


@main.route('/movies/<int:id>', methods = ['GET'])
def movie(id):
    ''' 電影詳細資料路由 '''

    api_key = os.environ.get('API_KEY')

    movie = Movies.query.get_or_404(id)

    url = f'https://api.themoviedb.org/3/movie/{movie.tmdb_id}/watch/providers?api_key={api_key}'

    response = requests.get(url)

    j = json.loads(response.text)

    if j and j.get('results').get('TW'):
        try:
            if j['results'].get('TW').get('flatrate')[0].get('provider_name') == 'Netflix':
                netflix_link = j['results'].get('TW').get('link')
            else:
                netflix_link = None
        except:
            netflix_link = None
    else:
        netflix_link = None

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
        if int(Movies.query.filter(Movies.genres.like(f'%{movie_genre}%')).count()) >= 8:
            rowCount = int(Movies.query.filter(Movies.genres.like(f'%{movie_genre}%')).count()) - 8
            similar_genre = Movies.query.filter(
                Movies.genres.like(f'%{movie_genre}%')
            ).offset(int(rowCount * random.random())).limit(similar_movie_numbers - len(similar_title)).all()
        else:
            similar_genre = []
    else:
        similar_genre = []

    # 將找到的資料合併成一個 list
    similar_movies = similar_title
    similar_movies.extend(similar_genre)


    comments = movie.comments.order_by(Comments.timestamp.desc()).all()

    return render_template('main/movie.html', movie = movie, comments = comments, similar_movies = similar_movies, netflix_link = netflix_link)

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