import re
import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.movie_entity import Movie
from RatS.imdb.imdb_site import IMDB


class IMDBRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(IMDBRatingsInserter, self).__init__(IMDB(args), args)

    def _find_movie(self, movie: Movie):
        movie_url = f"https://www.imdb.com/title/{movie.id}"
        self.site.browser.get(movie_url)
        return True

    def _is_requested_movie(self, movie: Movie, search_result):
        result_annotation = search_result.find(class_="result_text").get_text()
        result_year_list = re.findall(r"\((\d{4})\)", result_annotation)
        if len(result_year_list) > 0:
            result_year = result_year_list[-1]
            return int(result_year) == movie.year
        return False

    def _click_rating(self, my_rating: int):
        user_rating_button = self.site.browser.find_element(
            By.XPATH, "//div[@data-testid='hero-rating-bar__user-rating']/button"
        )
        self.site.browser.execute_script("arguments[0].click();", user_rating_button)

        stars = self.site.browser.find_elements(
            By.CLASS_NAME, "ipc-starbar__rating__button"
        )
        rate_button = self.site.browser.find_element(
            By.CLASS_NAME, "ipc-rating-prompt__rate-button"
        )
        current_rating = len(
            self.site.browser.find_elements(By.CLASS_NAME, "ipc-starbar__star--active")
        )
        if current_rating == my_rating:
            return
        star_index = int(my_rating) - 1

        self.site.browser.execute_script(
            """
            var element = document.querySelector(".ipc-starbar__touch");
            if (element)
                element.parentNode.removeChild(element);
        """
        )
        stars[star_index].click()
        rate_button.click()
        time.sleep(0.2)  # wait for POST request to be sent
