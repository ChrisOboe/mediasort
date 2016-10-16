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

import tmdbsimple
import logging
import datetime
import dateutil

def set_api_key(apikey):
    tmdbsimple.API_KEY = apikey

# downloads and caches the tmdb config
def download_config():
    logging.info("Downloading TMDb config")
    tmdb_config = tmdbsimple.Configuration().info()
    tmdb_config['lastaccess'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(tmdb_cache, 'w') as cachefile:
        json.dump(tmdb_config, cachefile)
    return tmdb_config

# gets the tmdb config from cache if not too old
def get_config():
    logging.info("Getting TMDb config")
    # if cachefile doesnt exist download the data
    if not os.path.exists(tmdb_cache):
        logging.info("TMDB config cache doesn't exists")
        return download_tmdb_config()

    # open cache
    with open(tmdb_cache, 'r') as cachefile:
        tmdb_config = json.load(cachefile)
    # check if too old
    lastaccess = dateutil.parser.parse(tmdb_config['lastaccess'])
    if (datetime.datetime.now() - lastaccess).days > config['general']['tmdb_config_cache_days']:
        logging.info("Cachefile exists, but is too old")
        return download_tmdb_config()
    else:
        logging.info("Using config from cache")
        return tmdb_config

# wants a search term
# returns tmdb id
def get_id(search_string):
    print ("Searching TMDb for {0}".format(guess['title']))
    tmdb_args = {'query':guess['title'], 'include_adult':'true'}
    if 'year' in guess: tmdb_args['year']=guess['year']

    simple.tmdb.search.movie(**tmdb_args)

    if not tmdb_search.results:
        print("Didn't found anything at TMDb.")
        return None

    if tmdb_search.total_results > 1:
        print("We found more than one possible movie for this name. We're going to use the first one.")
    else:
        print("We have exatly one match at TMDb. Bingo Bongo")

    return tmdb_search.results[0]['id']

def get_movie_info(movie_id, lang):
    return simpletmdb.Movies(movie_id).info(language=lang, append_to_response='credits,release_dates')

