'''

    使用者相關藍圖路由

'''


from datetime import datetime
from flask.helpers import url_for
from . import user
from flask import render_template, request, flash, redirect
from flask_login import login_required, current_user
from ..user_model import Users
from ..movie_model import Generes, Movies
from app import db


@user.route('/profile/<int:id>')
@login_required
def profile(id):
    ''' 使用者個人檔案路由 '''

    now  = datetime.utcnow()

    user = Users.query.get_or_404(id)

    return render_template('user/profile.html', user = user, now = now)

@user.route('/profile/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit_profile(id):
    ''' 使用者編輯個人檔案路由 '''

    genres_dict = Generes.generes_en
    user = Users.query.get_or_404(id)

    user_datas = {
        'form_name' : user.name or '',
        'form_location' : user.location or '',
        'form_about_me' : user.about_me or '',
        'form_genres' : set(user.favorite_movie_genres.split(',')) if user.favorite_movie_genres else set()
    }

    if request.method == 'POST':
        name = request.form.get('name') 
        location = request.form.get('location') 
        about_me = request.form.get('about_me') 
        movie_genres = []

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

    user_movies = current_user.movies.all()

    if movie not in user_movies:
        current_user.movies.append(movie)
        db.session.commit()
        flash('加入成功')
    else:
        flash('已經在清單中')

    return redirect(request.referrer)

@user.route('/movies/<int:id>')
@login_required
def user_movies(id):
    ''' 使用者收藏的電影 '''

    user = Users.query.get_or_404(id)

    movies = user.movies.all()

    return render_template('user/user_movies.html', movies = movies)






