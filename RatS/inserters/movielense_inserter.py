import json
import time

import sys

from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.movielense_site import Movielense
from RatS.utils.command_line import print_progress


class MovielenseInserter(Inserter):
    def __init__(self):
        super(MovielenseInserter, self).__init__(Movielense())

    def insert(self, movies):
        counter = 0
        failed_movies = []

        for movie in movies:
            movielense_entry = self.find_movie(movie)
            if movielense_entry:
                self.post_movie_rating(movielense_entry, movie.trakt.my_rating)
            else:
                failed_movies.append(movie)
            counter += 1
            print_progress(counter, len(movies), prefix='Movielense:')

        success_number = len(movies) - len(failed_movies)
        sys.stdout.write('\r\n===== sucessfully posted %i of %i movies =====\r\n' % (success_number, len(movies)))
        for failed_movie in failed_movies:
            sys.stdout.write('FAILED TO FIND: [IMDB:%s] %s\r\n' % (failed_movie.imdb.id, failed_movie.title))
        sys.stdout.flush()

        self.site.kill_browser()

    def find_movie(self, movie):
        self.site.browser.get('https://movielens.org/api/movies/explore?q=%s' % movie.title)
        time.sleep(1)
        data = ''
        try:
            data = self.get_json_from_html(data)
        except NoSuchElementException:
            time.sleep(2)
            data = self.get_json_from_html(data)
        for search_result in data['data']['searchResults']:
            if self.is_requested_movie(movie, search_result['movie']):
                return search_result['movie']

    def get_json_from_html(self, data):
        response = self.site.browser.find_element_by_tag_name("pre").text
        data = json.loads(response)
        return data

    @staticmethod
    def is_requested_movie(movie, param):
        if movie.movielense.id != '':
            return movie.movielense.id == param['movieId']
        else:
            return movie.imdb.id.replace('tt', '') == param['imdbMovieId'].replace('tt', '')

    def post_movie_rating(self, movielense_entry, my_rating):
        # paste_ratings_url = 'https://movielens.org/api/users/me/ratings'
        # data = {
        #     'movieId': movielense_entry['movieId'],
        #     'predictedRating': my_rating,
        #     'rating': my_rating
        # }
        # self.site.browser.request('POST', str(paste_ratings_url), data=data)
        movie_page_url = 'https://movielens.org/movies/'
        self.site.browser.get(movie_page_url + str(movielense_entry['movieId']))
        time.sleep(1)
        try:
            self.click_rating(my_rating)
        except ElementNotVisibleException:
            time.sleep(2)
            self.click_rating(my_rating)

    def click_rating(self, my_rating):
        stars = self.site.browser.find_element_by_class_name('rating').find_elements_by_tag_name('span')
        star_index = 10 - int(my_rating)
        stars[star_index].click()