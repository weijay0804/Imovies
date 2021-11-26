'''

    app 常用函式

'''

from flask_sqlalchemy import BaseQuery
from .movie_model import Movies, TopRankMoives, PopularMovies

class MovieTable():

    toprankmovies = TopRankMoives
    popularmovies = PopularMovies


def sort_movies(sort_type : str, desc : bool) -> BaseQuery:
    ''' 將電影依照特定方式排序 '''

    if sort_type == 'rate':
        if desc:
            movies_query = Movies.query.order_by(Movies.vote_average.desc())
        else:
            movies_query = Movies.query.order_by(Movies.vote_average)
    elif sort_type == 'year':
        if desc:
            movies_query = Movies.query.order_by(Movies.release_date.desc())
        else:
            movies_query = Movies.query.order_by(Movies.release_date)

    return movies_query

def sort_need_join_movies(join_table : MovieTable, sort_type : str, desc : bool) -> BaseQuery:
    ''' 將需要 join 操作的電影依照特定方式排序 '''

    if sort_type == 'rate':
        if desc:
            movies_query = Movies.query.join(
                join_table, Movies.tmdb_id == join_table.tmdb_id
                ).order_by(Movies.vote_average.desc())
        else:
            movies_query = Movies.query.join(
                join_table, Movies.tmdb_id == join_table.tmdb_id
                ).order_by(Movies.vote_average)
    elif sort_type == 'year':
        if desc:
            movies_query = Movies.query.join(
                join_table, Movies.tmdb_id == join_table.tmdb_id
                ).order_by(Movies.release_date.desc())
        else:
            movies_query = Movies.query.join(
                join_table, Movies.tmdb_id == join_table.tmdb_id
                ).order_by(Movies.release_date)

    return movies_query
