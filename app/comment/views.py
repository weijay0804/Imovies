'''

    app 評論相關路由

'''

from flask import request, redirect, url_for, flash
from flask_login import current_user
from app import db
from . import comment
from app.movie_model import Movies
from app.user_model import Comments


@comment.route('/movie/<int:id>', methods = ['POST'])
def comment_movie(id):

    movie = Movies.query.get_or_404(id)

    if request.method == 'POST':
        comment_data = request.form.get('comment')
        comment = Comments(body = comment_data, movie = movie, user = current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('評論已經送出')
        return redirect(url_for('main.movie', id = id))
    
    return redirect(url_for('main.index'))

@comment.route('/movie/<int:movie_id>/comment/<int:id>')
def user_comment(id, movie_id):

    comment = Comments.query.get_or_404(id)

    comment.like += 1

    db.session.commit()

    return redirect(url_for('main.movie', id = movie_id))