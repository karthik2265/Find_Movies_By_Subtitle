import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from opensubtitlescom import OpenSubtitles

load_dotenv()

# api keys
THE_MOVIE_DB_API_KEY = os.getenv('THE_MOVIE_DB_API_KEY')
OPEN_SUBTITLES_API_KEY = os.getenv('OPEN_SUBTITLES_API_KEY')
OPEN_SUBTITLES_USERNAME = os.getenv('OPEN_SUBTITLES_USERNAME')
OPEN_SUBTITLES_PASSWORD = os.getenv('OPEN_SUBTITLES_PASSWORD')

# Initialize the OpenSubtitles client
subtitles = OpenSubtitles("Find movie by subtitle", OPEN_SUBTITLES_API_KEY)

# Log in
subtitles.login(OPEN_SUBTITLES_USERNAME, OPEN_SUBTITLES_PASSWORD)


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


def fetch_subtitles_of_a_movie_and_check_if_subtitle_matched(movie, subtitle):
    # we are only considering 1st page of the search result
    response = subtitles.search(languages='en', imdb_id=movie['imdb_id'])
    response = response.to_dict()
    for res in response['data']:
        movie_subtitles = subtitles.download_and_parse(file_id=res.file_id, sub_format='srt')
        for movie_subtitle in movie_subtitles:
            if subtitle in movie_subtitle.content.lower():
                return True
    return False


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
                    if fetch_subtitles_of_a_movie_and_check_if_subtitle_matched(movie, subtitle):
                        with open('result.txt', 'a') as file:
                            file.write(f'title = {movie["title"]}, imdb_id = {movie["imdb_id"]} \n')
                    break
                break
            break


def main():
    start_year = 2005
    end_year = 2023
    subtitle = "right is right"
    asyncio.run(search_for_movies_with_subtitle_from(2005, 2023, subtitle))


if __name__ == '__main__':
    main()
