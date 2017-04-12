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

from mediasort.enums import MediaType
from mediasort import error

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

CONFIG = {}
CACHE = {}


# INTERNAL
def get_images(_id, category):
    """ gets the answer from fanart.tv and caches it """

    if _id in CACHE:
        return CACHE[_id]

    request = urllib.request.Request(
        FANARTTV_BASE_URL + "/"
        + category + "/"
        + str(_id)
        + "?api_key=" + CONFIG['key'])

    try:
        response = urllib.request.urlopen(request)
        CACHE[_id] = json.loads(
            response.read().decode(response.headers.get_content_charset()))
    except urllib.error.HTTPError:
        CACHE[_id] = []

    return CACHE[_id]


# MODULE
def init(fanarttvconfig):
    """ sets the fanart.tv api key """
    global CONFIG
    CONFIG['key'] = fanarttvconfig['api_key']


def get_needed_ids(mediatype):
    if mediatype == MediaType.movie.name:
        return ['tmdb']
    elif mediatype == MediaType.tvshow.name:
        return ['tvdb']
    elif mediatype == MediaType.episode.name:
        return ['tvdb']


# IMAGES
def get_image(identificator, imagetype, language):
    """ returns the url of an specified image """

    imagetypes = None
    category = None
    _id = None

    if identificator['type'] == MediaType.movie:
        imagetypes = MOVIE_IMAGE_TYPES
        category = 'movies'
        _id = identificator['tmdb']
    elif identificator['type'] == MediaType.tvshow:
        imagetypes = TVSHOW_IMAGE_TYPES
        category = 'tv'
        _id = identificator['tvdb']
    else:
        raise error.InvalidMediaType

    for fanarttype in imagetypes[imagetype]:
        images = get_images(_id, category)
        if fanarttype in images:
            for image in images[fanarttype]:
                if image['lang'] == language or image['lang'] == "00":
                    return image['url']

    return None
