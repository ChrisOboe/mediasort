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

import os
import tmdbsimple
import logging
import datetime
import dateutil.parser
import json
import helpers

logging.getLogger("tmdbsimple").setLevel(logging.WARNING)

def set_api_key(apikey):
    tmdbsimple.API_KEY = apikey

# downloads and caches the tmdb config
def download_config(cachefile):
    logging.info("Downloading TMDb config")
    tmdb_config = tmdbsimple.Configuration().info()
    tmdb_config['lastaccess'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    helpers.create_path(os.path.dirname(cachefile))
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
        return download_tmdb_config()
    else:
        logging.info("Using config from cache")
        return tmdb_config

# returns tmdb id from a guess
def get_id(name, year):
    ns = name if year == 0 else name + "(" + str(year) + ")"
    logging.info ("Searching TMDb for {0}".format(ns))
    tmdb_args = {'query':name, 'include_adult':'true'}
    if year != 0: tmdb_args['year'] = year

    tmdb_search = tmdbsimple.Search()

    tmdb_search.movie(**tmdb_args)

    if not tmdb_search.results:
        logging.info("Didn't found anything at TMDb.")
        return None

    if tmdb_search.total_results > 1:
        logging.info("We found more than one possible movie for this name. We're going to use the first one.")
    else:
        logging.info("We have exatly one match at TMDb. Bingo Bongo")

    return tmdb_search.results[0]['id']

def get_movie_info(movie_id, lang):
    return tmdbsimple.Movies(movie_id).info(language=lang, append_to_response='credits,release_dates')

