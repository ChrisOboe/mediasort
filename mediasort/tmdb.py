# Copyright (C) 2016-2017  Oboe, Chris <chrisoboe@eml.cc>
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
import datetime
import json
import dateutil.parser
import tmdbsimple

from .enums import MediaType
from .enums import ImageType
from . import helpers

logging.getLogger("tmdbsimple").setLevel(logging.WARNING)

# global settings
BASE_URL = None

# caches
TVSHOW_CACHE = {}
SEASON_IMAGE_CACHE = {}
EPISODE_CACHE = {}
MOVIE_CACHE = {}

# INTERNAL


def download_config(cachefile):
    """ downloads and caches the tmdb config """
    logging.info("Downloading TMDb config")
    tmdb_config = tmdbsimple.Configuration().info()
    tmdb_config['lastaccess'] = datetime.datetime.now().strftime('%Y-%m-%d')
    helpers.create_path(cachefile)
    with open(cachefile, 'w') as cache:
        json.dump(tmdb_config, cache)
    return tmdb_config


def get_tmdb_movie(tmdb_id, language):
    """ returns a tmdb movie """

    # when not in cache fill it
    if tmdb_id not in MOVIE_CACHE:
        MOVIE_CACHE[tmdb_id] = {}
    if language not in MOVIE_CACHE[tmdb_id]:
        MOVIE_CACHE[tmdb_id][language] = tmdbsimple.Movies(tmdb_id).info(
            language=language,
            append_to_response='credits,release_dates')

    return MOVIE_CACHE[tmdb_id][language]


def get_tmdb_episode(tmdb_id, season, episode, language):
    """ returns a tmdb episode """

    if not (tmdb_id in EPISODE_CACHE and
            season in EPISODE_CACHE[tmdb_id] and
            episode in EPISODE_CACHE[tmdb_id][season]):

        EPISODE_CACHE[tmdb_id] = {}
        EPISODE_CACHE[tmdb_id][season] = {}
        EPISODE_CACHE[tmdb_id][season][episode] = {}

    if language not in EPISODE_CACHE[tmdb_id][season][episode]:
        EPISODE_CACHE[tmdb_id][season][episode][language] = tmdbsimple.TV_Episodes(
            tmdb_id,
            season,
            episode).info(language=language)

    return EPISODE_CACHE[tmdb_id][season][episode][language]


def get_tmdb_tvshow(tmdb_id, language):
    """ returns a tmdb tvshow """

    if tmdb_id not in TVSHOW_CACHE:
        TVSHOW_CACHE[tmdb_id] = {}
    if language not in TVSHOW_CACHE[tmdb_id]:
        TVSHOW_CACHE[tmdb_id][language] = tmdbsimple.TV(tmdb_id).info(
            language=language,
            include_image_language="null",
            append_to_response='credits,content_ratings,images')

    return TVSHOW_CACHE[tmdb_id][language]

# MODULE


def init(tmdbconfig):
    """ initialize tmdbsimple, caches stuff and validates config """
    tmdbsimple.API_KEY = tmdbconfig['api_key']

    # if cachefile doesnt exist download the data
    if not os.path.exists(tmdbconfig['cachefile']):
        config = download_config(tmdbconfig['cachefile'])

    # open cache
    with open(tmdbconfig['cachefile'], 'r') as cachefile:
        tmdb_config = json.load(cachefile)
    # check if too old
    lastaccess = dateutil.parser.parse(tmdb_config['lastaccess'])
    if (datetime.datetime.now() - lastaccess).days > tmdbconfig['cache_validity']:
        config = download_config(tmdbconfig['cachefile'])
    else:
        config = tmdb_config

    # setting base url
    global BASE_URL
    if tmdbconfig['https_download']:
        BASE_URL = config['images']['secure_base_url']
    else:
        BASE_URL = config['images']['base_url']

    if tmdbconfig['poster_size'] not in config['images']['poster_sizes']:
        raise AttributeError("Invalid poster size. Allowed ones are: {0}\n".format(
            config['images']['poster_sizes']))
    if tmdbconfig['background_size'] not in config['images']['backdrop_sizes']:
        raise AttributeError("Invalid background size. Allowed ones are: {0}\n".format(
            config['images']['backdrop_sizes']))
    if tmdbconfig['thumbnail_size'] not in config['images']['still_sizes']:
        raise AttributeError("Invalid thumbnail size. Allowed ones are: {0}\n".format(
            config['images']['still_sizes']))


# IDENTIFICATOR


def get_identificator(guess, identificator, config):
    """ returns ids for the guessed videofile """

    if identificator['imdb'] is None:
        tmdb_search = tmdbsimple.Search()
        tmdb_args = {'query': guess['title']}
        if guess['type'] == MediaType.movie and guess['year']:
            tmdb_args['year'] = guess['year']
        tmdb_search.movie(**tmdb_args)

        if not tmdb_search.results:
            logging.info("Didn't found anything at TMDb.")
            return identificator

        if tmdb_search.total_results > 1:
            logging.info("We have multiple matches. Using the first one.")
        else:
            logging.info("We have exatly one match at TMDb.")

        identificator['tmdb'] = tmdb_search.results[0]['id']

        # get video details to get imdbid
        if guess['type'] == MediaType.movie:
            identificator['imdb'] = tmdbsimple.Movies(identificator['tmdb']).info()['imdb_id']
        elif guess['type'] == MediaType.episode:
            tvshow = tmdbsimple.TV(identificator['tmdb']).external_ids()
            identificator['imdb'] = tvshow['imdb_id']
            identificator['tvdb'] = tvshow['tvdb_id']
    else:
        tmdb_find = tmdbsimple.find()
        info = tmdb_find.info(external_sources={'imdb_id': identificator['imdb']})
        if guess['type'] == MediaType.movie:
            identificator['tmdb'] = info['movie_results'][0]['id']
        elif guess['type'] == MediaType.episode:
            identificator['tmdb'] = info['tv_results'][0]['id']
            tvshow = tmdbsimple.TV(identificator['tmdb']).external_ids()
            identificator['tvdb'] = tvshow['tvdb_id']

    return identificator

# METADATA


def get_movie_metadata(identificator, metadatatype, language, config):
    """ returns movie metadata """

    movie = get_tmdb_movie(identificator['tmdb'], language)

    metadata = {
        'title': helpers.get_entry('title', movie),
        'originaltitle': helpers.get_entry('original_title', movie),
        'premiered': helpers.get_entry('release_date', movie),
        'tagline': helpers.get_entry('tagline', movie),
        'plot': helpers.get_entry('overview', movie),
        'rating': helpers.get_entry('vote_average', movie),
        'votes': helpers.get_entry('vote_count', movie)
    }

    if movie['belongs_to_collection']:
        metadata['set'] = movie['belongs_to_collection']['name']

    for release in movie['release_dates']['results']:
        if release['iso_3166_1'] == config['certification_country']:
            metadata['certification'] = str(release['release_dates'][0]['certification'])

    metadata['studios'] = []
    for studio in movie['production_companies']:
        metadata['studios'].append(studio['name'])

    metadata['countries'] = []
    for country in movie['production_countries']:
        metadata['countries'].append(country['name'])

    metadata['genres'] = []
    for genre in movie['genres']:
        metadata['genres'].append(genre['name'])

    metadata['directors'] = []
    metadata['writers'] = []
    for crew in movie['credits']['crew']:
        if crew['job'] == 'Director':
            metadata['directors'].append(crew['name'])
        elif crew['job'] == 'Writer':
            metadata['writers'].append(crew['name'])

    metadata['actors'] = []
    for actor in movie['credits']['cast']:
        actor = {}
        actor['name'] = actor['name']
        actor['role'] = actor['character']
        metadata['actors'].append(actor)

    return metadata[metadatatype]


def get_episode_metadata(identificator, metadatatype, language, config):
    """ returns episode metadata """

    episode = get_tmdb_episode(identificator['tmdb'],
                               identificator['season'],
                               identificator['episode'],
                               language)

    metadata = {
        'title': helpers.get_entry('name', episode),
        'premiered': helpers.get_entry('air_date', episode),
        'plot': helpers.get_entry('overview', episode),
        'rating': helpers.get_entry('vote_average', episode),
        'votes': helpers.get_entry('vote_count', episode),
    }

    return metadata[metadatatype]


def get_tvshow_metadata(identificator, metadatatype, language, config):
    """ returns tvshow metadata """

    tvshow = get_tmdb_tvshow(identificator['tmdb'],
                             language)

    metadata = {
        'title': helpers.get_entry('name', tvshow),
        'premiered': helpers.get_entry('first_air_date', tvshow),
        'plot': helpers.get_entry('overview', tvshow),
        'rating': helpers.get_entry('vote_average', tvshow),
        'votes': helpers.get_entry('vote_count', tvshow),
    }

    for rating in tvshow['content_ratings']['results']:
        if rating['iso_3166_1'] == config['certification_country']:
            metadata['certification'] = str(rating['release_dates'][0]['rating'])

    metadata['studios'] = []
    for studio in tvshow['networks']:
        metadata['studios'].append(studio['name'])

    metadata['genres'] = []
    for genre in tvshow['genres']:
        metadata['genres'].append(genre['name'])

    metadata['actors'] = []
    for actor in tvshow['credits']['cast']:
        actor = {}
        actor['name'] = actor['name']
        actor['role'] = actor['character']
        metadata['actors'].append(actor)

    return metadata[metadatatype]

# IMAGES


def get_movie_image(identificator, imagetype, config):
    """ returns a image_type image for id for given languages"""
    if imagetype == ImageType.poster:
        key = 'poster_path'
    elif imagetype == ImageType.background:
        key = 'backdrop_path'
    else:
        # TODO check on init
        raise LookupError("TMDb doesn't support the wanted ImageType")

    if get_tmdb_movie(identificator['tmdb'],
                      config['image_languages'])[key] is None:
        return None

    return (BASE_URL
            + config[imagetype + "_size"]
            + get_tmdb_movie(identificator['tmdb'],
                             config['image_languages'])[key])


def get_tvshow_image(identificator, imagetype, config):
    """ returns the url of a tvshow image """
    if imagetype == 'poster':
        key = 'posters'
    elif imagetype == 'background':
        key = 'backdrops'
    else:
        # TODO check on init
        raise LookupError("TMDb doesn't support the wanted ImageType")

    if not get_tmdb_tvshow(identificator['tmdb'],
                           config['image_languages'])['images'][key]:
        return None

    return (BASE_URL
            + config[imagetype + "_size"]
            + get_tmdb_tvshow(identificator['tmdb'],
                              config['image_languages'])['images'][key][0]['file_path'])


def get_season_image(identificator, imagetype, config):
    """ returns the url of a season image"""
    if imagetype != "poster":
        raise LookupError("TMDb only supports posters as season image")

    if identificator['tmdb'] not in SEASON_IMAGE_CACHE:
        image_langs = ','.join(config['image_languages'][1:])
        image_langs += ',null'
        SEASON_IMAGE_CACHE[identificator['tmdb']] = tmdbsimple.TV_Seasons(identificator['tmdb'], identificator['season']).images(
            language=config['image_languages'][0],
            include_image_language=image_langs)

        if not SEASON_IMAGE_CACHE[identificator['tmdb']]['posters']:
            return None

    return (BASE_URL
            + config['poster_size']
            + SEASON_IMAGE_CACHE[identificator['tmdb']]['posters'][0]['file_path'])


def get_episode_image(identificator, imagetype, config):
    """ returns the episode thumnail """
    if imagetype != "thumbnail":
        raise LookupError("TMDB only supports thumnail as episode image")

    if get_tmdb_episode(identificator['tmdb'],
                        identificator['season'],
                        identificator['episode'],
                        config['image_languages'])['still_path'] is None:
        return None

    return (BASE_URL
            + config['thumbnail_size']
            + get_tmdb_episode(identificator['tmdb'],
                               identificator['season'],
                               identificator['episode'],
                      ter dem Titel Tatort sind streng genommen Dutzende von Krimiserien vereint. Jede ARD-Anstalt produziert innerhalb der Tatort-Reihe 90 Minuten lange Filme mit eigenen Ermittlern, die in der Regel Mordfälle aufzuklären haben. Auch das Schweizer und das Österreichische Fernsehen schicken eigene Polizisten ins Rennen. Die Filme mit den verschiedenen Hauptdarstellern werden abwechselnd und in loser Folge sonntags um 20.15 Uhr gezeigt, wobei die Ermittler der größeren ARD-Anstalten wie WDR und NDR alle paar Wochen im Einsatz sind und die der kleinen Anstalten wie RB und SR manchmal jahrelang gar nicht auftreten. Zunächst liefen nur etwa elf Folgen im Jahr, Ende der 90er-Jahre waren es 30.         config['image_languages'])['still_path'])
