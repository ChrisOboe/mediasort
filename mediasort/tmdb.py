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


def set_api_key(apikey):
    """ Sets the TMDb API key """
    tmdbsimple.API_KEY = apikey


def download_config(cachefile):
    """ downloads and caches the tmdb config """
    logging.info("Downloading TMDb config")
    tmdb_config = tmdbsimple.Configuration().info()
    tmdb_config['lastaccess'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    helpers.create_path(cachefile)
    with open(cachefile, 'w') as cf:
        json.dump(tmdb_config, cf)
    return tmdb_config

# gets the tmdb config from cache if not too old
def get_config(cachefile, validity):
    logging.info("Getting TMDb config")
    # if cachefile doesnt exist download the data
    if not os.path.exists(cachefile):
        logging.info("TMDB config cache doesn't exists")
        return download_config(cachefile)

    # open cache
    with open(cachefile, 'r') as cf:
        tmdb_config = json.load(cf)
    # check if too old
    lastaccess = dateutil.parser.parse(tmdb_config['lastaccess'])
    if (datetime.datetime.now() - lastaccess).days > validity:
        logging.info("Cachefile exists, but is too old")
        return download_config(cachefile)
    else:
        logging.info("Using config from cache")
        return tmdb_config

# returns tmdb id
def get_id(video_type, title, year):
    tmdb_search = tmdbsimple.Search()
    logging.info ("  Searching TMDb for {0}".format(title))

    if video_type == 'movie':
        tmdb_args = {'query':title, 'include_adult':'true'}
        if year: tmdb_args['year'] = year
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


def get_movie_info(movie_id, lang):
    return tmdbsimple.Movies(movie_id).info(language=lang, append_to_response='credits,release_dates')

def get_tvshow_info(tvshow_id, lang):
    return tmdbsimple.TV(tvshow_id).info(language=lang, append_to_response='credits,content_ratings')

def get_episode_info(tvshow_id, season, episode, lang):
    return tmdbsimple.TV_Episodes(tvshow_id, season, episode).info(language=lang)

