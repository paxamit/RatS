import json
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel


class Site(str, Enum):
    ALLOCINE = "ALLOCINE"
    CRITICKER = "CRITICKER"
    FILMAFFINITY = "FILMAFFINITY"
    FILMTIPSET = "FILMTIPSET"
    FLIXSTER = "FLIXSTER"
    ICHECKMOVIES = "ICHECKMOVIES"
    IMDB = "IMDB"
    LETTERBOXD = "LETTERBOXD"
    LISTAL = "LISTAL"
    METACRITIC = "METACRITIC"
    MOVIELENS = "MOVIELENS"
    MOVIEPILOT = "MOVIEPILOT"
    PLEX = "PLEX"
    ROTTENTOMATOES = "ROTTENTOMATOES"
    TMDB = "TMDB"
    TRAKT = "TRAKT"


class SiteSpecificMovieData(BaseModel):
    id: Optional[str]
    url: Optional[str]
    my_rating: Optional[int]  # 1 - 10

    def __str__(self):
        return dict(self)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return self.__str__()

    @staticmethod
    def from_json(json_dct):
        data = SiteSpecificMovieData(id=json_dct["id"], url=json_dct["url"])
        if "my_rating" in json_dct:
            data.my_rating = json_dct["my_rating"]
        return data


class Movie(BaseModel):
    title: Optional[str]
    year: Optional[int]
    site_data: Dict[Site, SiteSpecificMovieData] = dict()

    def __str__(self):
        return json.dumps(self.to_json())

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        movie_json = {"title": self.title, "year": self.year}
        site_data = {}
        for key, site_specific_movie_data in self.site_data.items():
            site_data[key] = site_specific_movie_data.to_json()

        movie_json["site_data"] = site_data
        return movie_json

    @staticmethod
    def from_json(movie_json):
        if "id" in movie_json.keys():
            return SiteSpecificMovieData.from_json(movie_json)
        elif "site_data" in movie_json.keys():
            return Movie(
                title=movie_json["title"],
                year=movie_json["year"] if "year" in movie_json else None,
                site_data=_convert_dict_to_movie_site_date(movie_json["site_data"])
                if "site_data" in movie_json
                else None,
            )
        else:
            return movie_json


def _convert_dict_to_movie_site_date(
    site_data: Dict,
) -> Dict[Site, SiteSpecificMovieData]:
    result: Dict[Site, SiteSpecificMovieData] = dict()
    if not site_data:
        return result
    for site_name, site_data in site_data.items():
        site: Site = Site(site_name.upper())
        site_specific_movie_data: SiteSpecificMovieData = (
            SiteSpecificMovieData.from_json(site_data)
        )
        result[site] = site_specific_movie_data
    return result
