"""

    爬取 IMdb 電影資料

"""

import time
from .model import PopularMovie, File, TopRankMovies, Movie
from typing import NoReturn

class Main():
    ''' 主程式 '''

    def __init__(self):
        self.file = File()
        self.movie = Movie()
        self.popular = PopularMovie()
        self.toprank = TopRankMovies()
        

    def get_movies_datas(self, type : str, output_file_name : str,  item_limt : int = None) -> NoReturn:
        ''' 
            取得熱門電影資料，並輸出 json 
            type = (popular or top)
        '''

        if type == 'popular':
            r = self.popular.get_imdb_datas(item_limit=item_limt)
        if type == 'top':
            r = self.toprank.get_imdb_datas(item_limit=item_limt)

        self.file.output_json_file(r,file_name=output_file_name)

    def get_movie_details(self, movie_file_name : str, output_file_name : str) -> NoReturn:
        ''' 由 tmdb api 取得熱門電影詳細資料，並輸出 json '''

        datas = self.file.input_json_file(file_name=movie_file_name)
        r = []
        for data in datas:
            tmdb_id = data['tmdb_id']
            movie_detail = self.movie.get_movie_details(tmdb_id=tmdb_id)
            r.append(movie_detail)
            print(tmdb_id)

            time.sleep(0.3)

        self.file.output_json_file(r,file_name=output_file_name)








