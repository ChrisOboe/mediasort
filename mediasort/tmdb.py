# Copyright (C) 2016  Oboe, Chris <chrisoboe@eml.cc>
# Author: Oboe, Chris <chrisoboe@eml.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" helper functions for tmdbsimple """

import os
import logging
import datetime
import json
import dateutil.parser
import tmdbsimple

from .enums import MediaType
from . import helpers

logging.getLogger("tmdbsimple").setLevel(logging.WARNING)

# global settings
BASE_URL = None
SIZE = {}

# caches
TVSHOW_CACHE = {}
SEASON_IMAGE_CACHE = {}
EPISODE_CACHE = {}
MOVIE_CACHE = {}


def clean_cache():
    """ cleans the tmdb cache """
    # we don't clean TVSHOWS and SEASONS. we likely need it later anyways
    EPISODE_CACHE.clear()
    MOVIE_CACHE.clear()


def download_config(cachefile):
    """ downloads and caches the tmdb config """
    logging.info("Downloading TMDb config")
    tmdb_config = tmdbsimple.Configuration().info()
    tmdb_config['lastaccess'] = datetime.datetime.now().strftime('%Y-%m-%d')
    helpers.create_path(cachefile)
    with open(cachefile, 'w') as cache:
        json.dump(tmdb_config, cache)
    return tmdb_config


def init(settings):
    """ initialize tmdbsimple, caches stuff and validates config """
    tmdbsimple.API_KEY = settings['api_key']

    logging.info("Getting TMDb config")
    # if cachefile doesnt exist download the data
    if not os.path.exists(settings['cachefile']):
        logging.info("TMDB config cache doesn't exists")
        config = download_config(settings['cachefile'])

    # open cache
    with open(settings['cachefile'], 'r') as cachefile:
        tmdb_config = json.load(cachefile)
    # check if too old
    lastaccess = dateutil.parser.parse(tmdb_config['lastaccess'])
    if (datetime.datetime.now() - lastaccess).days > settings['cache_validity']:
        logging.info("Cachefile exists, but is too old")
        config = download_config(settings['cachefile'])
    else:
        logging.info("Using config from cache")
        config = tmdb_config

    # setting base url
    global BASE_URL
    if settings['https_download']:
        BASE_URL = config['images']['secure_base_url']
    else:
        BASE_URL = config['images']['base_url']

    # setting sizes
    checks = {"poster_size": "poster_sizes",
              "backdrop_size": "backdrop_sizes",
              "still_size": "still_sizes"}

    for check in checks:
        if settings[check] not in config['images'][checks[check]]:
            errortext = ("{0} is not a valid {1}.\nValid {2} are {3}"
                         .format(settings[check],
                                 check,
                                 checks[check],
                                 config['images'][checks[check]]))
            raise AttributeError(errortext)
        else:
            SIZE[check] = settings[check]


def get_ids(video_type, title, year):
    """ returns tmdb id """
    ids = {}
    tmdb_search = tmdbsimple.Search()
    logging.info("  Using TMDb to Search for \"%s\"", title)

    if video_type == MediaType.movie:
        tmdb_args = {'query': title, 'include_adult': 'true'}
        if year:
            tmdb_args['year'] = year
        tmdb_search.movie(**tmdb_args)
    elif video_type == MediaType.episode:
        tmdb_search.tv(query=title)

    if not tmdb_search.results:
        logging.info("    Didn't found anything at TMDb.")
        return None

    if tmdb_search.total_results > 1:
        logging.info("    We have multiple matches. Using the first one.")
    else:
        logging.info("    We have exatly one match at TMDb.")

    ids["tmdb"] = tmdb_search.results[0]['id']

    # get video details to get imdbid
    if video_type == MediaType.movie:
        ids["imdb"] = tmdbsimple.Movies(ids["tmdb"]).info()["imdb_id"]
    elif video_type == MediaType.episode:
        tvshow = tmdbsimple.TV(ids["tmdb"]).external_ids()
        ids["imdb"] = tvshow["imdb_id"]
        ids["tvdb"] = tvshow["tvdb_id"]

    for cid in ids:
        logging.info("    Found %s ID: %s", cid, ids[cid])

    return ids


def get_movie_info(ids, languages):
    """ returns movie stuff """
    if ids["tmdb"] in MOVIE_CACHE:
        return MOVIE_CACHE[ids["tmdb"]]

    MOVIE_CACHE[ids["tmdb"]] = {}
    MOVIE_CACHE[ids["tmdb"]]["ids"] = ids
    for language in languages:
        helpers.merge_dict(MOVIE_CACHE[ids["tmdb"]],
                           tmdbsimple.Movies(ids["tmdb"]).info(
                               language=language,
                               append_to_response='credits,release_dates'
                               ))

    return MOVIE_CACHE[ids["tmdb"]]


def get_tvshow_info(ids, languages):
    """ returns tvshow stuff """
    if ids["tmdb"] in TVSHOW_CACHE:
        return TVSHOW_CACHE[id]

    TVSHOW_CACHE[ids["tmdb"]] = {}
    TVSHOW_CACHE[ids["tmdb"]]["ids"] = ids
    for language in languages:
        helpers.merge_dict(TVSHOW_CACHE[ids["tmdb"]],
                           tmdbsimple.TV(ids["tmdb"]).info(
                               language=language,
                               include_image_language="null",
                               append_to_response='credits,content_ratings,images'
                               ))

    return TVSHOW_CACHE[ids["tmdb"]]


def get_episode_info(ids, season, episode, languages):
    """ returns episode stuff """
    if ids["tmdb"] in EPISODE_CACHE and \
       season in EPISODE_CACHE[ids["tmdb"]] and \
       episode in EPISODE_CACHE[ids["tmdb"]][season]:
        return EPISODE_CACHE[ids["tmdb"]][season][episode]

    EPISODE_CACHE[ids["tmdb"]] = {}
    EPISODE_CACHE[ids["tmdb"]][season] = {}
    EPISODE_CACHE[ids["tmdb"]][season][episode] = {}
    for language in languages:
        helpers.merge_dict(EPISODE_CACHE[ids["tmdb"]][season][episode],
                           tmdbsimple.TV_Episodes(
                               ids["tmdb"],
                               season,
                               episode).info(language=language))

    return EPISODE_CACHE[ids["tmdb"]][season][episode]


def get_movie_image_url(ids, image_type, languages):
    """ returns a image_type image for id for given languages"""
    if image_type == 'poster':
        return (BASE_URL
                + SIZE['poster_size']
                + get_movie_info(ids, languages)['poster_path'])
    elif image_type == 'background':
        return (BASE_URL
                + SIZE['backdrop_size']
                + get_movie_info(ids, languages)['backdrop_path'])
    else:
        raise LookupError("TMDb doesn't support {0}".format(image_type))


def get_tvshow_image_url(ids, image_type, languages):
    """ returns the url of a tvshow image """

    if image_type == 'poster':
        return (BASE_URL
                + SIZE['poster_size']
                + get_tvshow_info(
                    ids["tmdb"],
                    languages)['images']['posters'][0]['file_path'])
    elif image_type == 'background':
        return (BASE_URL
                + SIZE['backdrop_size']
                + get_tvshow_info(
                    ids["tmdb"],
                    languages)['images']['backdrops'][0]['file_path'])
    else:
        raise LookupError("TMDb doesn't support {0}".format(image_type))


def get_season_image_url(ids, season, image_type, languages):
    """ returns the url of a season image"""
    if image_type != "poster":
        raise LookupError("TMDb only supports posters as season image")

    if ids["tmdb"] not in SEASON_IMAGE_CACHE:
        image_langs = ','.join(languages[1:])
        image_langs += ',null'
        SEASON_IMAGE_CACHE[ids["tmdb"]] = tmdbsimple.TV_Seasons(ids["tmdb"], season).images(
            language=languages[0],
            include_image_language=image_langs)

    return (BASE_URL
            + SIZE['poster_size']
            + SEASON_IMAGE_CACHE[ids["tmdb"]]['posters'][0]['file_path'])


def get_episode_image_url(ids, season, episode, image_type, languages):
    """ returns the episode thumnail, image_type and languages is ignored """
    if image_type != "thumbnail":
        raise LookupError("TMDB only supports thumnail as episode image")

    return (BASE_URL
            + SIZE['still_size']
            + get_episode_info(ids,
                               season,
                               episode,
                               languages)['still_path'])
