'''

    使用者相關藍圖路由

'''



from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from . import user
from ..user_model import Users
from ..movie_model import Generes, Movies


@user.route('/profile/<int:id>')
def profile(id):
    ''' 使用者個人檔案路由 '''

    # 獲得當前時間，讓模板可以處理
    now  = datetime.utcnow()

    user = Users.query.get_or_404(id)

    return render_template('user/profile.html', user = user, now = now)

@user.route('/profile/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit_profile(id):
    ''' 使用者編輯個人檔案路由 '''

    # 取得電影的所有類別
    genres_dict = Generes.generes_en
    user = Users.query.get_or_404(id)

    if current_user != user:
        abort(403)

    user_datas = {
        'form_name' : user.name or '',
        'form_location' : user.location or '',
        'form_about_me' : user.about_me or '',
        'form_genres' : set(user.favorite_movie_genres.split(',')) if user.favorite_movie_genres else set()
    }

    # 處理表單
    if request.method == 'POST':
        name = request.form.get('name') 
        location = request.form.get('location') 
        about_me = request.form.get('about_me') 
        movie_genres = []

        # 處理使用者勾選喜歡的電影類別回傳的資料
        for genre in set(genres_dict.values()):
            if request.form.get(genre):
                movie_genres.append(request.form.get(genre))

        user.name = name
        user.location = location
        user.about_me = about_me
        user.favorite_movie_genres = ','.join(movie_genres)

        db.session.commit()
        flash('資料已更新')
        return redirect(url_for('user.profile', id = user.id))

    return render_template('user/edit_profile.html', genres_dict = genres_dict, **user_datas)


@user.route('/add/movie/<int:id>')
@login_required
def user_add_movie(id):
    ''' 使用者加入電影到收藏清單路由 '''

    movie = Movies.query.get_or_404(id)

    # 獲得使用者收藏和看過的電影
    user_movies = current_user.movies.all()
    user_watched_movies = current_user.watched_movies.all()

    # 處理使用者加入電影的邏輯
    if movie not in user_movies and movie not in user_watched_movies:
        current_user.movies.append(movie)
        db.session.commit()
        flash('加入成功')
    elif movie in user_watched_movies:
        flash('你已經看過這個電影')
    else:
        flash('已經在清單中')

    return redirect(request.referrer)

@user.route('/delete/movie/<int:id>')
@login_required
def user_delete_movie(id):
    ''' 使用者刪除收藏清單中的電影 '''

    movie = Movies.query.get_or_404(id)

    user_movies = current_user.movies.all()


    if movie in user_movies:
        current_user.movies.remove(movie)
        db.session.commit()
        flash('刪除成功')

        return redirect(request.referrer)
    else:
        return redirect(url_for('main.index'))

@user.route('/movies/<int:id>')
@login_required
def user_movies(id):
    ''' 使用者收藏的電影 '''

    user = Users.query.get_or_404(id)

    if current_user != user:
        abort(403)

    # 獲得使用者的收藏電影 (query 物件)
    query = user.movies

    # 獲得使用者收藏的電影數量
    movies_count = query.count()

    # 或得 url 參數
    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')

    args = {'sort' : sort_type, 'desc' : desc, 'id' : id}

    # 排序電影
    if sort_type == 'rate':
        if desc:
            pagination = query.order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = query.order_by(Movies.vote_average).paginate(page, per_page = 10, error_out = False)
    elif sort_type == 'year':
        if desc:
            pagination = query.order_by(Movies.release_date.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = query.order_by(Movies.release_date).paginate(page, per_page = 10, error_out = False)

    else:
        pagination = query.order_by(Movies.original_title).paginate(page, per_page = 10, error_out = False)
    
    movies = pagination.items

    return render_template('user/user_movies.html', movies = movies, pagination = pagination, args = args, movies_count = movies_count)

@user.route('/add/watched/<int:id>')
@login_required
def user_add_watched_movie(id):
    ''' 使用者加入電影到已觀看清單 '''

    movie = Movies.query.get_or_404(id)

    # 獲得使用者已觀看的電影
    user_watched_movies = current_user.watched_movies.all()

    # 處理加入已觀看電影的邏輯
    if movie not in user_watched_movies:
        current_user.watched_movies.append(movie)
        current_user.movies.remove(movie)
        db.session.commit()
        flash('加入成功')

        return redirect(request.referrer)

    else:
        return redirect(url_for('main.index'))

@user.route('/delete/watched/<int:id>')
@login_required
def user_delete_watched_movie(id):
    ''' 使用者刪出已觀看的電影 '''

    movie = Movies.query.get_or_404(id)

    user_watched_movies = current_user.watched_movies.all()

    if movie in user_watched_movies:
        current_user.watched_movies.remove(movie)
        db.session.commit()
        flash('刪除成功')

        return redirect(request.referrer)

    else:
        return redirect(url_for('main.index'))


@user.route('/watched/<int:id>')
@login_required
def user_watched_movies(id):
    ''' 使用者已觀看電影路由 '''

    user = Users.query.get_or_404(id)

    if current_user != user:
        abort(403)

    query = user.watched_movies

    movies_count = query.count()

    page = request.args.get('page', 1, type=int)
    sort_type = request.args.get('sort')
    desc = request.args.get('desc')

    args = {'sort' : sort_type, 'desc' : desc, 'id' : id}


    if sort_type == 'rate':
        if desc:
            pagination = query.order_by(Movies.vote_average.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = query.order_by(Movies.vote_average).paginate(page, per_page = 10, error_out = False)
    elif sort_type == 'year':
        if desc:
            pagination = query.order_by(Movies.release_date.desc()).paginate(page, per_page = 10, error_out = False)
        else:
            pagination = query.order_by(Movies.release_date).paginate(page, per_page = 10, error_out = False)

    else:
        pagination = query.order_by(Movies.original_title).paginate(page, per_page = 10, error_out = False)
    
    movies = pagination.items

    return render_template('user/user_watched_movies.html', movies = movies, pagination = pagination, args = args, movies_count = movies_count)




