"""

    爬取 IMdb 電影資料

"""

from model import PopularMovie


def get_popular_movies():
    ''' 取得熱門電影資料，並輸出 json '''

    movies = PopularMovie()

    r = movies.get_imdb_datas(api_key='d202f8126b1a52f67cc558860680dfa4')

    d = movies.make_imdb_datas_to_dict(r)

    movies.output_json_file(d, file_name='popular.json')

    print('完成')


if __name__ == '__main__':
    get_popular_movies()



