import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# api keys
THE_MOVIE_DB_API_KEY = os.getenv('THE_MOVIE_DB_API_KEY')


# helper functions
async def fetch_movies(session, url, params, format=False):
    async with session.get(url, params=params) as response:
        response = await response.json()
        if format:
            return response['results']
        return response


async def fetch_imdb_id(session, url, params):
    async with session.get(url, params=params) as response:
        response = await response.json()
        return response['imdb_id']


async def search_for_movies_with_subtitle_from(start_year, end_year, subtitle):
    get_movies_url = "https://api.themoviedb.org/3/discover/movie"
    async with aiohttp.ClientSession() as session:
        for year in range(start_year, end_year + 1):
            get_movies_params = {
                'api_key': THE_MOVIE_DB_API_KEY,
                'primary_release_year': year,
                'sort_by': 'release_date.desc',
                'with_original_language': 'en'
            }
            data = await fetch_movies(session, get_movies_url, get_movies_params)
            pages_count = data["total_pages"]
            for page in range(1, pages_count + 1):
                movies = await fetch_movies(session, get_movies_url, {**get_movies_params, 'page': page}, True)
                for movie in movies:
                    # get imdb id of the movie
                    get_imdb_id_url = 'https://api.themoviedb.org/3/movie/1216535/external_ids'
                    get_imdb_id_params = {
                        'api_key': THE_MOVIE_DB_API_KEY,
                    }
                    movie['imdb_id'] = await fetch_imdb_id(session, get_imdb_id_url, get_imdb_id_params)
                    print(movie['title'], movie['imdb_id'])
                break
            break



async def check_if_movie_has_subtitle(title, sub_title):
    # get subtitles from an external source

    # format it to lowercase

    # check if sub_title is found

    # if found store the result in a text file
    pass


def main():
    start_year = 2005
    end_year = 2023
    subtitle = "right is right"
    asyncio.run(search_for_movies_with_subtitle_from(2005, 2023, subtitle))


if __name__ == '__main__':
    main()
