"""

    模組

"""

import json
import requests
import time
import os
from bs4 import BeautifulSoup
from typing import List, NoReturn


class Movie():
    ''' 電影類別 '''

    def __init__(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))

    def get_url_datas(self, url : str) -> requests:
        ''' 獲得 url 的資料 '''

        response = requests.get(url)

        if response.status_code != 200:
            return f" 網路連線錯誤: {response.status_code} "
        
        return response

    def get_imdb_datas(self, url : str, item_limit : int = None, api_key :str = None) -> List[tuple]:
        ''' 獲得 imdb 電影資料 '''

        response = self.get_url_datas(url)
        item_list = []

        soup = BeautifulSoup(response.text, 'html.parser')

        movie_items = soup.find('tbody', class_ = 'lister-list').find_all('tr', limit = item_limit)

        for movie_item in movie_items:
            title = movie_item.find('td', class_ = 'titleColumn').find('a').text
            imdb_id = movie_item.find('td', class_ = 'titleColumn').find('a').get('href').split('/')[2]
            tmdb_id = self.get_tmdb_id(imdb_id, api_key) if api_key else None
            item_list.append( (imdb_id, tmdb_id, title ))

            print(title)
            time.sleep(0.5)
        
        return item_list


    def get_tmdb_id(self, imdb_id : str, api_key : str) -> int:
        ''' 根據 imdb id 獲得 tmdb 電影 id '''

        url = f'https://api.themoviedb.org/3/movie/{imdb_id}/external_ids?api_key={api_key}'
        response = self.get_url_datas(url)
        j = json.loads(response.text)

        tmdb_id = int(j.get('id')) if j.get('id') else None

        return tmdb_id

    
    def make_imdb_datas_to_dict(self, imdb_datas : List[tuple]) -> List[dict]:
        ''' 將從 imdb 獲取的電影資料轉換成 dict type '''

        if len(imdb_datas[0]) != 3:
            return ' 資料格式錯誤，必須為 (imdb_id, tmdb_id, title) '

        r = []

        for data in imdb_datas:
            imdb_id, tmdb_id, title = data

            r.append({
                'imdb_id' : imdb_id,
                'tmdb_id' : tmdb_id,
                'title' : title
            })    

        return r

    def output_json_file(self, datas : List[dict], file_path : str = None, file_name : str = None) -> NoReturn:
        ''' 將資料儲存成 json 檔 '''
        
        f_path = file_path if file_path else self.basedir
        f_name = file_name if file_name else 'datas.json'
        file = os.path.join(f_path, f_name)

        if os.path.exists(file):
            print('錯誤!! 檔案已存在')
            return None

        if not file.endswith('.json'):
            print('錯誤!! 檔案副檔名必須是 .json')
            return None

        with open(file, 'w', encoding='utf-8') as f:
            json.dump(datas, f, indent=4)

            


class PopularMovie(Movie):
    ''' 熱門電影類別 '''

    def __init__(self):
        super().__init__()
        self.url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'

    def get_imdb_datas(self, api_key : str = None, item_limit: int = None,) -> List[tuple]:
        return super().get_imdb_datas(url = self.url, item_limit=item_limit, api_key=api_key)





