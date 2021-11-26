'''

    使用者相關藍圖路由

'''


from datetime import datetime
from flask.helpers import url_for
from . import user
from flask import render_template, request, flash, redirect
from flask_login import login_required
from ..user_model import Users
from ..movie_model import Generes
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



