'''

    imovies 主腳本


'''

import os

import click
from app import create_app, db
from flask_migrate import Migrate
from app.model import Movies, PopularMovies, TopRankMoives
from crawler.main import Main
import time


app = create_app('development')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db = db, Movies = Movies, PopularMovies = PopularMovies, TopRankMovies = TopRankMoives)


@app.cli.command()
def crawling():
    main = Main()
    # main.get_popular_movies(output_file_name='popular.json')
    # time.sleep(2)
    main.get_top_rank_movies('toprank.json')
    main.get_top_rank_movie_details('toprank.json', 'toprank_movies.json')
    # main.get_popular_movie_details('popular.json', 'popular_movies.json')
    


