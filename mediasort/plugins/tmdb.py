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
import requests
from collections import defaultdict
import dateutil.parser
import tmdbsimple
from appdirs import user_cache_dir

from mediasort.enums import MediaType
from mediasort import error


# global settings
CONFIG = {}
CACHEFILE = user_cache_dir('mediasort', 'ChrisOboe') + "/tmdb.cache"

# caches
CACHE = defaultdict(lambda: defaultdict(dict))


# INTERNAL
def download_config():
    """ downloads and caches the tmdb config """

    tmdb_config = tmdbsimple.Configuration().info()
    tmdb_config['lastaccess'] = datetime.datetime.now().strftime('%Y-%m-%d')

    pathonly = os.path.dirname(CACHEFILE)
    if not os.path.exists(pathonly):
        os.makedirs(pathonly)

    with open(CACHEFILE, 'w') as cache:
        json.dump(tmdb_config, cache)
    return tmdb_config


# MODULE
def init(tmdbconfig):
    """ initialize tmdbsimple, caches stuff and validates config """
    global CONFIG
    tmdbsimple.API_KEY = tmdbconfig['api_key']
    CONFIG['cache_validity'] = tmdbconfig['cache_validity']
    CONFIG['use_https'] = tmdbconfig['use_https']
    CONFIG['poster_size'] = tmdbconfig['sizes']['poster']
    CONFIG['background_size'] = tmdbconfig['sizes']['background']
    CONFIG['thumbnail_size'] = tmdbconfig['sizes']['thumbnail']
    CONFIG['certification_country'] = tmdbconfig['certification_country'].upper()
    CONFIG['search_language'] = tmdbconfig['search_language'].upper()

    # if cachefile doesnt exist download the data
    if not os.path.exists(CACHEFILE):
        tmdb = download_config()

    # open cache
    with open(CACHEFILE, 'r') as cache:
        tmdb = json.load(cache)
    # check if too old
    lastaccess = dateutil.parser.parse(tmdb['lastaccess'])
    if (datetime.datetime.now() - lastaccess).days > CONFIG['cache_validity']:
        tmdb = download_config()

    # setting base url
    if CONFIG['use_https']:
        CONFIG['base_url'] = tmdb['images']['secure_base_url']
    else:
        CONFIG['base_url'] = tmdb['images']['base_url']

    if CONFIG['poster_size'] not in tmdb['images']['poster_sizes']:
        raise error.InvalidConfig(
            "Invalid poster size. Allowed ones are: {0}\n".format(
                tmdb['images']['poster_sizes']))
    if CONFIG['background_size'] not in tmdb['images']['backdrop_sizes']:
        raise error.InvalidConfig(
            "Invalid background size. Allowed ones are: {0}\n".format(
                tmdb['images']['backdrop_sizes']))
    if CONFIG['thumbnail_size'] not in tmdb['images']['still_sizes']:
        raise error.InvalidConfig(
            "Invalid thumbnail size. Allowed ones are: {0}\n".format(
                tmdb['images']['still_sizes']))


# IDENTIFICATOR
def get_identificator(guess, identificator, callback):
    """ returns ids for the guessed videofile """

    # get episode and season from guessed
    if guess['type'] == MediaType.episode or \
       guess['type'] == MediaType.season:
        if not identificator['season']:
            identificator['season'] = guess['season']

    if guess['type'] == MediaType.episode and \
       not identificator['episode']:
        identificator['episode'] = guess['episode']

    # get tmdb id from imdb id
    if guess['type'] == MediaType.movie and identificator['imdb']:
        info = tmdbsimple.Find(
            identificator['imdb']
        ).info(external_source='imdb_id')

        if guess['type'] == MediaType.movie:
            identificator['tmdb'] = info['movie_results'][0]['id']
            identificator['tmdb'] = callback(
                [{'title': info['movie_results'][0]['title'],
                  'description': info['movie_results'][0]['overview'],
                  'id': info['movie_results'][0]['id']}],
                guess['type'].name
            )

        elif guess['type'] == MediaType.episode:
            identificator['tmdb'] = info['tv_results'][0]['id']
            tvshow = tmdbsimple.TV(identificator['tmdb']).external_ids()
            identificator['tvdb'] = tvshow['tvdb_id']
            identificator['tmdb'] = callback(
                [{'title': info['tv_results'][0]['name'],
                  'description': info['tv_results'][0]['overview'],
                  'id': info['tv_results'][0]['id']}],
                guess['type'].name
            )

    # get tmdb id from title
    if not identificator['tmdb']:
        args = {'query': guess['title'], 'language': CONFIG['search_language']}
        if guess['type'] == MediaType.movie and guess['year']:
            args['year'] = guess['year']
        search = tmdbsimple.Search()
        if guess['type'] == MediaType.movie:
            search.movie(**args)
        elif guess['type'] == MediaType.episode:
            search.tv(**args)

        if not search.results:
            raise error.NotEnoughData("TMDb search didn't found anything.")

        if callback is None and len(search.results) == 1:
            identificator['tmdb'] = search.results[0]['id']
        else:
            # call callback function
            callback_list = []
            for result in search.results:
                if guess['type'] == MediaType.movie:
                    movie = tmdbsimple.Movies(result['id']).info(
                        language=CONFIG['search_language'])

                    callback_list.append(
                        {'title': "{0} ({1})".format(movie['title'], movie['release_date']),
                         'descprition': result['overview'],
                         'id': result['id']}
                    )
                elif guess['type'] == MediaType.episode or \
                     guess['type'] == MediaType.tvshow or \
                     guess['type'] == MediaType.season:
                    callback_list.append(
                        {'title': result['name'],
                         'descprition': result['overview'],
                         'id': result['id']}
                    )
            identificator['tmdb'] = callback(callback_list,
                                             guess['type'].name)

    # now we should have a tmdb id. get the rest of ids
    if guess['type'] == MediaType.movie and not identificator['imdb']:
        identificator['imdb'] = tmdbsimple.Movies(identificator['tmdb']).info()['imdb_id']
    elif guess['type'] == MediaType.episode:
        tvshow = tmdbsimple.TV(identificator['tmdb']).external_ids()
        identificator['imdb'] = tvshow['imdb_id']
        identificator['tvdb'] = tvshow['tvdb_id']

    return identificator


def get_identificator_list(mediatype):
    if mediatype == MediaType.movie.name:
        return ['tmdb', 'imdb']
    if mediatype == MediaType.episode.name:
        return ['tmdb', 'imdb', 'tvdb']


# METADATA
def get_needed_ids(mediatype):
    return ['tmdb']


def get_metadata(identificator, metadatatype, language):
    """ returns the metadata """
    if identificator['type'] == MediaType.movie:
        return get_movie_metadata(identificator, metadatatype, language)

    elif identificator['type'] == MediaType.tvshow:
        return get_tvshow_metadata(identificator, metadatatype, language)

    elif identificator['type'] == MediaType.episode:
        return get_episode_metadata(identificator, metadatatype, language)

    else:
        raise error.InvalidMediaType


def get_movie_metadata(identificator, metadatatype, language):
    """ returns movie metadata """

    # use value from cache if cache exists
    try:
        movie_cache = CACHE['metadata']['movie'][identificator['tmdb']]
    except KeyError:
        movie_cache = None

    if movie_cache:
        return movie_cache[metadatatype]

    movie = tmdbsimple.Movies(identificator['tmdb']).info(
            language=language,
            append_to_response='credits,release_dates')

    metadata = {
        'title': movie.get('title'),
        'originaltitle': movie.get('original_title'),
        'premiered': movie.get('release_date'),
        'tagline': movie.get('tagline'),
        'plot': movie.get('overview'),
        'rating': movie.get('vote_average'),
        'votes': movie.get('vote_count')
    }

    if movie['belongs_to_collection'] is not None:
        metadata['set'] = movie['belongs_to_collection']['name']
    else:
        metadata['set'] = None

    metadata['certification'] = None
    for release in movie['release_dates']['results']:
        if release['iso_3166_1'] == CONFIG['certification_country']:
            metadata['certification'] = str(
                release['release_dates'][0]['certification']
            )

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
        metadata['actors'].append(
            {'name': actor['name'],
             'role': actor['character']}
        )

    # write metadata to cache
    CACHE['metadata']['movie'][identificator['tmdb']] = metadata
    return metadata[metadatatype]


def get_tvshow_metadata(identificator, metadatatype, language):
    """ returns tvshow metadata """

    try:
        tvshow_cache = CACHE['metadata']['tvshow'][identificator['tmdb']]
    except KeyError:
        tvshow_cache = None

    # use value from cache if cache exists
    if tvshow_cache:
        return tvshow_cache[metadatatype]

    tvshow = tmdbsimple.TV(identificator['tmdb']).info(
        language=language,
        include_image_language="null",
        append_to_response='credits,content_ratings,images'
    )

    metadata = {
        'showtitle': tvshow.get('name'),
        'premiered': tvshow.get('first_air_date'),
        'plot': tvshow.get('overview'),
        'rating': tvshow.get('vote_average'),
        'votes': tvshow.get('vote_count'),
    }

    metadata['certification'] = None
    for certification in tvshow['content_ratings']['results']:
        if certification['iso_3166_1'] == CONFIG['certification_country']:
            metadata['certification'] = str(certification['rating'])

    metadata['creators'] = []
    for creator in tvshow['created_by']:
        metadata['creators'].append(creator['name'])

    metadata['studios'] = []
    for studio in tvshow['production_companies']:
        metadata['studios'].append(studio['name'])

    metadata['networks'] = []
    for network in tvshow['networks']:
        metadata['networks'].append(network['name'])

    metadata['genres'] = []
    for genre in tvshow['genres']:
        metadata['genres'].append(genre['name'])

    metadata['actors'] = []
    for actor in tvshow['credits']['cast']:
        metadata['actors'].append(
            {'name': actor['name'],
             'role': actor['character']}
        )

    CACHE['metadata']['tvshow'][identificator['tmdb']] = metadata
    return metadata[metadatatype]


def get_episode_metadata(identificator, metadatatype, language):
    """ returns episode metadata """

    try:
        episode_cache = CACHE['metadata']['episode'][identificator['tmdb']][identificator['season']][identificator['episode']]
    except KeyError:
        episode_cache = None

    # use value from cache if cache exists
    if episode_cache:
        return episode_cache[metadatatype]

    try:
        episode = tmdbsimple.TV_Episodes(
            identificator['tmdb'],
            identificator['season'],
            identificator['episode']
        ).info(language=language)
    except requests.exceptions.HTTPError:
        raise error.NotEnoughData("Problem with accessing TMDb")

    metadata = {
        'showtitle': get_tvshow_metadata(identificator, 'showtitle', language),
        'title': episode.get('name'),
        'premiered': episode.get('air_date'),
        'show_premiered': get_tvshow_metadata(identificator, 'premiered', language),
        'plot': episode.get('overview'),
        'rating': episode.get('vote_average'),
        'votes': episode.get('vote_count'),
        'studios': get_tvshow_metadata(identificator, 'studios', language),
        'networks': get_tvshow_metadata(identificator, 'networks', language),
        'certification': get_tvshow_metadata(identificator, 'certification', language),
    }

    metadata['directors'] = []
    metadata['scriptwriters'] = []

    if 'crew' in episode:
        for crewmember in episode['crew']:
            if crewmember['job'] == 'Director':
                metadata['directors'].append(crewmember['name'])
            elif crewmember['job'] == 'Writer':
                metadata['scriptwriters'].append(crewmember['name'])

    metadata['actors'] = get_tvshow_metadata(identificator, 'actors', language)
    if 'guest_stars' in episode:
        for guest_star in episode['guest_stars']:
            if guest_star['character']:
                metadata['actors'].append(
                    {'name': guest_star['name'],
                     'role': guest_star['character']})


    # write metadata to cache
    tmdb = identificator['tmdb']
    episode = identificator['episode']
    season = identificator['season']
    if tmdb not in CACHE['metadata']['episode']:
        CACHE['metadata']['episode'][tmdb] = {}
    if season not in CACHE['metadata']['episode'][tmdb]:
        CACHE['metadata']['episode'][tmdb][season] = {}

    CACHE['metadata']['episode'][tmdb][season][episode] = metadata

    return metadata[metadatatype]


# IMAGES
def get_image(identificator, imagetype, language):
    """ return the image """
    if identificator['type'] == MediaType.movie:
        return get_movie_image(identificator, imagetype, language)

    elif identificator['type'] == MediaType.tvshow:
        return get_tvshow_image(identificator, imagetype, language)

    elif identificator['type'] == MediaType.season:
        return get_season_image(identificator, imagetype, language)

    elif identificator['type'] == MediaType.episode:
        return get_episode_image(identificator, imagetype, language)

    else:
        raise error.InvalidMediaType


def get_movie_image(identificator, imagetype, language):
    """ returns a image_type image for id for given languages"""

    try:
        movie_cache = CACHE['images']['movie'][identificator['tmdb']]
    except KeyError:
        movie_cache = None

    # use value from cache if cache exists
    if movie_cache:
        return movie_cache.get(imagetype)

    movie = tmdbsimple.Movies(identificator['tmdb']).info(
        language=language
    )

    images = {}
    if movie['poster_path']:
        images['poster'] = CONFIG['base_url'] + \
                           CONFIG['poster_size'] + \
                           movie['poster_path']

    if movie['backdrop_path']:
        images['background'] = CONFIG['base_url'] + \
                               CONFIG['background_size'] + \
                               movie['backdrop_path']

    CACHE['images']['movie'][identificator['tmdb']] = images
    return images.get(imagetype)


def get_tvshow_image(identificator, imagetype, language):
    """ returns the url of a tvshow image """

    try:
        tvshow_cache = CACHE['images']['tvshow'][identificator['tmdb']]
    except KeyError:
        tvshow_cache = None

    if tvshow_cache:
        return tvshow_cache.get(imagetype)

    tvshow = tmdbsimple.TV(identificator['tmdb']).info(
        language=language,
        include_image_language="null",
        append_to_response='images'
    )

    images = {}
    if tvshow['images']['posters']:
        images['poster'] = CONFIG['base_url'] + \
                           CONFIG['poster_size'] + \
                           tvshow['images']['posters'][0]['file_path']

    if tvshow['images']['backdrops']:
        images['background'] = CONFIG['base_url'] + \
                               CONFIG['background_size'] + \
                               tvshow['images']['backdrops'][0]['file_path']

    CACHE['images']['tvshow'][identificator['tmdb']] = images
    return images.get(imagetype)


def get_season_image(identificator, imagetype, language):
    """ returns the url of a season image"""

    try:
        season_cache = CACHE['images']['season'][identificator['tmdb']][identificator['season']]
    except KeyError:
        season_cache = None

    if season_cache:
        return season_cache.get(imagetype)

    season = tmdbsimple.TV_Seasons(
        identificator['tmdb'],
        identificator['season']
    ).images(
        language=language,
        #include_image_language="null" #bug in tmdb
    )

    images = {}
    if season['posters']:
        images['poster'] = CONFIG['base_url'] + \
                           CONFIG['poster_size'] + \
                           season['posters'][0]['file_path']

    tmdb = identificator['tmdb']
    season = identificator['season']
    if tmdb not in CACHE['images']['season']:
        CACHE['images']['season'][tmdb] = {}

    CACHE['images']['season'][tmdb][season] = images
    return images.get(imagetype)


def get_episode_image(identificator, imagetype, language):
    """ returns the episode thumnail """

    try:
        episode_cache = CACHE['images']['episode'][identificator['tmdb']][identificator['season']][identificator['episode']]
    except KeyError:
        episode_cache = None

    if episode_cache:
        return episode_cache[imagetype]

    episode = tmdbsimple.TV_Episodes(
        identificator['tmdb'],
        identificator['season'],
        identificator['episode']
    ).info(language=language)

    if episode['still_path']:
        images = {
            'thumbnail':
            CONFIG['base_url'] +
            CONFIG['thumbnail_size'] +
            episode['still_path']
        }
    else:
        images = {'thumbnail': None}

    tmdb = identificator['tmdb']
    episode = identificator['episode']
    season = identificator['season']
    if tmdb not in CACHE['images']['episode']:
        CACHE['images']['episode'][tmdb] = {}
    if season not in CACHE['images']['episode'][tmdb]:
        CACHE['images']['episode'][tmdb][season] = {}

    CACHE['images']['episode'][tmdb][season][episode] = images
    return images[imagetype]
