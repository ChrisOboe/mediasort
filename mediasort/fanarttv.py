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

from urllib.request import urlopen
import json

FANARTTV_BASE_URL = "http://webservice.fanart.tv/v3"


# MOVIE IMAGES
# |MediaSort name|fanart.tv name|fanart.tv api  |description                  |
# |--------------|--------------|---------------|-----------------------------|
# |logo          |HD ClearLOGO  |hdmovielogo    |logo with transparent bg     |
# |logo          |ClearLOGO     |movielogo      |fallback for logo            |
# |disc          |cdART         |moviedisc      |disc with transparent bg     |
# |poster        |Poster        |movieposter    |poster without tagline       |
# |clearart      |HD ClearART   |hdmovieclearart|logo + chars + transparent bg|
# |clearart      |ClearART      |movieart       |fallback for clearart        |
# |background    |Background    |moviebackground|fullhd image without text    |
# |banner        |Banner        |moviebanner    |old xbox scene style banner  |
# |art           |Movie Thumbs  |moviethumb     |like clearart but with bg    |

# TVSHOW IMAGES
# |MediaSort name|fanart.tv name|fanart.tv api  |description                  |
# |--------------|--------------|---------------|-----------------------------|
# |logo          |HD ClearLOGO  |hdtvlogo       |logo with transparent bg     |
# |logo          |ClearLOGO     |tvlogo         |fallback for logo            |
# |poster        |Poster        |tvposter       |poster without tagline       |
# |charart       |CharacterArt  |characterart   |characters + transparent bg  |
# |clearart      |HD ClearART   |hdclearart     |logo + chars + transparent bg|
# |clearart      |ClearART      |clearart       |fallback for clearart        |
# |background    |Background    |showbackground |fullhd image without text    |
# |banner        |Banner        |tvbanner       |old xbox scene style banner  |
# |art           |Movie Thumbs  |tvthumb        |like clearart but with bg    |

# SEASON IMAGES
# Since fanart.tv doesn't have an api for selecting a sepcific season, we can't
# use their season specific images

# EPISODE IMAGES
# fanart.tv doesn't have tumbnails for episodes.

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

    with urlopen(FANARTTV_BASE_URL + "/" + category + "/"
                 + tmdb_id + "?api_key=" + API_KEY) as response:

        IMAGE_CACHE[tmdb_id] = json.loads(response.read())
        return IMAGE_CACHE[tmdb_id]


def get_movie_image_url(tmdb_id, image_type, languages):
    """ returns the url of an specified image """
    if image_type not in MOVIE_IMAGE_TYPES:
        raise LookupError("This provider doesn't support {0}"
                          .format(image_type))

    for language in languages:
        for images in get_images(tmdb_id,
                                 'movies')[MOVIE_IMAGE_TYPES[image_type]]:
            for image in images:
                if image['lang'] == language:
                    return image['url']

    raise LookupError("No images for the languages {0} in type {1} found"
                      .format(languages, image_type))


def get_tvshow_image_url(tmdb_id, image_type, languages):
    """ returns the url of an specified image """
    if image_type not in TVSHOW_IMAGE_TYPES:
        raise LookupError("fanart.tv doesn't support {0}"
                          .format(image_type))

    for language in languages:
        for images in get_images(tmdb_id,
                                 'tv')[MOVIE_IMAGE_TYPES[image_type]]:
            for image in images:
                if image['lang'] == language:
                    return image['url']

    raise LookupError("No images for the languages {0} in type {1} found"
                      .format(languages, image_type))
