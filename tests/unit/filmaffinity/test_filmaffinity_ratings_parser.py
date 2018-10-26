import os
from unittest import TestCase
from unittest.mock import patch

from RatS.filmaffinity.filmaffinity_ratings_parser import FilmAffinityRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class FilmAffinityRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        with open(os.path.join(TESTDATA_PATH, 'filmaffinity', 'my_ratings.html'), encoding='UTF-8') as my_ratings:
            self.my_ratings = my_ratings.read()

    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        FilmAffinityRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.base.base_ratings_parser.RatingsParser._print_progress_bar')
    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.filmaffinity.filmaffinity_ratings_parser.FilmAffinity')
    def test_parser(self, site_mock, base_init_mock, browser_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = FilmAffinityRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'FilmAffinity'
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(20, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Jurassic World: Fallen Kingdom', parser.movies[0]['title'])
        self.assertEqual('283552', parser.movies[0]['filmaffinity']['id'])
        self.assertEqual('https://www.filmaffinity.com/en/film283552.html', parser.movies[0]['filmaffinity']['url'])
        self.assertEqual(2018, parser.movies[0]['year'])
        self.assertEqual(6, parser.movies[0]['filmaffinity']['my_rating'])
