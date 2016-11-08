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

""" provides an interface for fanart.tv """

import urllib
import json

FANARTTV_BASE_URL = "http://webservice.fanart.tv/v3"

MOVIE_IMAGE_TYPES = {'logo':       ['hdmovielogo', 'movielogo'],
                     'disc':       ['moviedisc'],
                     'poster':     ['movieposter'],
                     'clearart':   ['hdmovieclearart', 'movieart'],
                     'background': ['moviebackground'],
                     'banner':     ['moviebanner'],
                     'art':        ['moviethumb']}

TVSHOW_IMAGE_TYPES = {'logo':       ['hdtvlogo', 'tvlogo'],
                      'poster':     ['tvposter'],
                      'charart':    ['characterart'],
                      'clearart':   ['hdclearart', 'clearart'],
                      'background': ['showbackground'],
                      'banner':     ['tvbanner'],
                      'art':        ['tvthumb']}

API_KEY = None
IMAGE_CACHE = {}


def clean_cache():
    """ cleans the fanart.tv cache """
    IMAGE_CACHE.clear()


def init(settings):
    """ sets the fanart.tv api key """
    global API_KEY
    API_KEY = settings['api_key']


def get_movie_image_types():
    """ returns the availabel image types """
    return MOVIE_IMAGE_TYPES.keys()


def get_tvshow_image_types():
    """ returns the availabel image types """
    return TVSHOW_IMAGE_TYPES.keys()


def get_episode_image_types():
    """ returns the available images types """
    return None


def get_images(tmdb_id, category):
    """ gets the answer from fanart.tv and caches it """
    if tmdb_id in IMAGE_CACHE:
        return IMAGE_CACHE[tmdb_id]

    request = urllib.request.Request(
        FANARTTV_BASE_URL + "/"
        + category + "/"
        + str(tmdb_id)
        + "?api_key=" + API_KEY)

    try:
        response = urllib.request.urlopen(request)
        IMAGE_CACHE[tmdb_id] = json.loads(
            response.read().decode(response.headers.get_content_charset()))
    except urllib.error.HTTPError:
        IMAGE_CACHE[tmdb_id] = None

    return IMAGE_CACHE[tmdb_id]


def get_movie_image_url(tmdb_id, image_type, languages):
    """ returns the url of an specified image """
    if image_type not in MOVIE_IMAGE_TYPES:
        raise LookupError("This provider doesn't support {0}"
                          .format(image_type))

    for language in languages:
        for images in MOVIE_IMAGE_TYPES[image_type]:
            for image in get_images(tmdb_id, 'movies')[images]:
                if image['lang'] == language:
                    return image['url']

    raise LookupError("No images for the languages {0} in type {1} found"
                      .format(languages, image_type))


def get_tvshow_image_url(tmdb_id, image_type, languages):
    """ returns the url of an specified image """
    if image_type not in TVSHOW_IMAGE_TYPES:
        raise LookupError("fanart.tv doesn't support {0}"
                          .format(image_type))

    if get_images(tmdb_id, 'tv') is None:
        raise LookupError("fanart.tv doesn't support this tvshow")

    for language in languages:
        for images in get_images(tmdb_id, 'tv')[MOVIE_IMAGE_TYPES[image_type]]:
            for image in images:
                if image['lang'] == language:
                    return image['url']

    raise LookupError("No images for the languages {0} in type {1} found"
                      .format(languages, image_type))
