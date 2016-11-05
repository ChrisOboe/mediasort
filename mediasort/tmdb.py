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
    tmdb_config['lastaccess'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
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
        config = download_config(cachefile)
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
            SIZE[check] = config['images'][checks[check]]


def get_id(video_type, title, year):
    """ returns tmdb id """
    tmdb_search = tmdbsimple.Search()
    logging.info("  Searching TMDb for {0}".format(title))

    if video_type == 'movie':
        tmdb_args = {'query': title, 'include_adult': 'true'}
        if year:
            tmdb_args['year'] = year
        tmdb_search.movie(**tmdb_args)
    elif video_type == 'episode':
        tmdb_search.tv(query=title)

    if not tmdb_search.results:
        logging.info("    Didn't found anything at TMDb.")
        return None

    if tmdb_search.total_results > 1:
        logging.info("    We have multiple matches. Using the first one.")
    else:
        logging.info("    We have exatly one match at TMDb.")

    logging.info("    Using TMDb ID: {0}".format(tmdb_search.results[0]['id']))
    return tmdb_search.results[0]['id']


def get_movie_info(tmdb_id, languages):
    """ returns movie stuff """
    if tmdb_id in MOVIE_CACHE:
        return MOVIE_CACHE[tmdb_id]

    MOVIE_CACHE[tmdb_id] = {}
    for language in languages:
        helpers.merge_dict(MOVIE_CACHE[tmdb_id],
                           tmdbsimple.Movies(tmdb_id).info(
                               language=language,
                               append_to_response='credits,release_dates'
                               ))

    return MOVIE_CACHE[tmdb_id]


def get_tvshow_info(tmdb_id, languages):
    """ returns tvshow stuff """
    if tmdb_id in TVSHOW_CACHE:
        return TVSHOW_CACHE[tmdb_id]

    image_langs = ','.join(languages[1:])
    image_langs += ',null'

    TVSHOW_CACHE[tmdb_id] = {}
    for language in languages:
        helpers.merge_dict(TVSHOW_CACHE[tmdb_id],
                           tmdbsimple.TV(tmdb_id).info(
                               language=language,
                               include_image_language=image_langs,
                               append_to_response='credits,content_ratings,images'
                               ))

    return TVSHOW_CACHE[tmdb_id]


def get_episode_info(tmdb_id, season, episode, languages):
    """ returns episode stuff """
    if tmdb_id in EPISODE_CACHE and \
       season in EPISODE_CACHE[tmdb_id] and \
       episode in EPISODE_CACHE[tmdb_id][season]:
        return EPISODE_CACHE[tmdb_id][season][episode]

    EPISODE_CACHE[tmdb_id][season][episode] = {}
    for language in languages:
        helpers.merge_dict(EPISODE_CACHE[tmdb_id][season][episode],
                           tmdbsimple.TV_Episodes(
                               tmdb_id,
                               season,
                               episode).info(language=language))

    return EPISODE_CACHE[tmdb_id][season][episode]


def get_movie_image_url(tmdb_id, image_type, languages):
    """ returns a image_type image for tmdb_id for given languages"""
    if image_type == 'poster':
        return (BASE_URL
                + SIZE['poster_size']
                + get_movie_info(tmdb_id, languages)['poster_path'])
    elif image_type == 'backdrop':
        return (BASE_URL
                + SIZE['backdrop_size']
                + get_movie_info(tmdb_id, languages)['backdrop_path'])
    else:
        raise LookupError("TMDb doesn't support {0}".format(image_type))


def get_tvshow_image_url(tmdb_id, image_type, languages):
    """ returns the url of a tvshow image """
    if image_type == 'poster':
        return (BASE_URL
                + SIZE['poster_size']
                + get_tvshow_info(tmdb_id, languages)['images']['poster'][0]['path'])
    elif image_type == 'backdrop':
        return (BASE_URL
                + SIZE['backdrop_size']
                + get_tvshow_info(tmdb_id, languages)['images']['backdrop'][0]['path'])
    else:
        raise LookupError("TMDb doesn't support {0}".format(image_type))


def get_season_image_url(tmdb_id, season, image_type, languages):
    """ returns the url of a season image"""
    if image_type != "poster":
        raise LookupError("TMDb only supports posters as season image")

    if tmdb_id not in SEASON_IMAGE_CACHE:
        image_langs = ','.join(languages[1:])
        image_langs += ',null'
        SEASON_IMAGE_CACHE[tmdb_id] = tmdbsimple.TV_Seasons(tmdb_id, season).images(
            language=languages[0],
            include_image_language=image_langs)

    return (BASE_URL
            + SIZE['poster_size']
            + SEASON_IMAGE_CACHE[tmdb_id]['posters'][0]['file_path'])


def get_episode_image_url(tmdb_id, season, episode, image_type, languages):
    """ returns the episode thumnail, image_type and languages is ignored """
    if image_type != "thumbnail":
        raise LookupError("TMDB only supports thumnail as episode image")

    return (BASE_URL
            + SIZE['still_size']
            + get_episode_info(tmdb_id, season, episode, languages)['still_path'])
