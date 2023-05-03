import os

from selenium.webdriver.common.by import By

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.trakt.trakt_site import Trakt
from RatS.utils import file_impex

class TraktRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(TraktRatingsParser, self).__init__(Trakt(args), args)
        self.downloaded_file_name = "Axameat-ratings-all-all.csv"

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file(self.downloaded_file_name)
        self.movies = file_impex.load_movies_from_trakt_csv(
            os.path.join(self.exports_folder, self.csv_filename)
        )

    def _call_download_url(self):
        self.site.browser.get(
            f"https://trakt.tv/users/axameat/ratings.csv?slurm=543d424b2f41508388fca2f3e58ee46c&"
        )