'''

    imovies 主腳本


'''

import os
import click
from app import create_app, db
from flask_migrate import Migrate
from app.movie_model import Movies, PopularMovies, TopRankMoives
from app.user_model import Users
from crawler.main import Main
import time


app = create_app('development')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(
        db = db, 
        Movies = Movies, 
        PopularMovies = PopularMovies, 
        TopRankMovies = TopRankMoives,
        Users = Users,
        )


@app.cli.command()
@click.option('--type', '-t', 'type', help = 'type = popular or top', required = True)
@click.option('--name', '-n',  'name', help = 'file name without extension', required = True)
@click.option('--detail/--no-detail', default = True, help = 'is crawling movie detail datas')
@click.option('--limit', '-l',  'limit', help = 'item limit', default = None)
def crawling(type, limit, name, detail):
    ''' 爬取 imdb 電影資料 '''

    main = Main()   # 實例化

    item_limit = int(limit) if limit else None  # 將型態由 str 轉為 int

    if type == 'popular':
        main.get_movies_datas(type='popular', item_limt=item_limit, output_file_name=f'{name}.json')
    if type == 'top':
        main.get_movies_datas(type='top', item_limt=item_limit, output_file_name=f'{name}.json')

    # 爬取電影詳細資料
    if detail:
        time.sleep(1) # 先等待 1 秒，確保輸入的文件存在
        main.get_movie_details(movie_file_name=f'{name}.json', output_file_name=f'{name}_detail.json')

@app.cli.command()
@click.option('--database', '-db', 'db', help = 'insert to which database', required = True)
@click.option('--file', '-f', 'file', help = 'which file you want to insert (without extension)', required = True)
def insert(db, file):
    ''' 寫入資料到資料庫 '''

    if db == 'popular':
        database = PopularMovies
    if db == 'top':
        database = TopRankMoives
    if db == 'movies':
        database = Movies

    database.insert(file = f'{file}.json')

@app.cli.command()
@click.option('--database', '-db', 'db', help = 'update which database', required = True)
@click.option('--file', '-f', 'file', help = 'which file you want to update (without extension)', required = True)
def update(db, file):
    ''' 更新資料庫中的資料 '''

    if db == 'popular':
        database = PopularMovies
    if db == 'top':
        database = TopRankMoives
    if db == 'movies':
        database = Movies

    database.update(file = f'{file}.json')








