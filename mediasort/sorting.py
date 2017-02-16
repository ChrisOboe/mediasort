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

import os
from shutil import move

from mediasort import error
from mediasort.enums import PluginType, MediaType, MetadataType, ImageType
from mediasort.template import get_paths, write_nfo
from mediasort.download import download


# helpers
def contains_elements(elements, dictionary):
    """ returns False if any element is not in dictionary or none """
    for element in elements:
        if element not in dictionary:
            return False
        if dictionary[element] is None:
            return False
    return True


# plugins
def get_guess(filepath, providers):
    """ returns a guess for a filename """

    guess = {
         'filepath': None,
         'type': None,
         'title': None,
         'year': None,
         'releasegroup': None,
         'source': None,
         'season': None,
         'episode': None,
     }

    for provider in providers:
        guess.update(provider.get_guess(filepath))

    needed = ['filepath', 'title', 'type']
    if guess['type'] == MediaType.episode:
        needed.extend(['season', 'episode'])

    if not contains_elements(needed, guess):
        raise error.NotEnoughData("Needed value couldn't be guessed")

    return guess


def get_identificator(guess, providers):
    """ returns a identificator for a guess """

    identificator = None

    if guess['type'] == MediaType.movie:
        identificator = {
            'type': MediaType.movie,
            'tmdb': None,
            'imdb': None,
        }
    elif guess['type'] == MediaType.episode:
        identificator = {
            'type': MediaType.episode,
            'tmdb': None,
            'imdb': None,
            'tvdb': None,
            'season': guess['season'],
            'episode': guess['episode'],
        }
    else:
        raise error.InvalidMediaType

    for provider in providers[guess['type']]['modules']:
        identificator.update(provider.get_identificator(guess, identificator))

    if guess['type'] == MediaType.movie:
        needed = ['tmdb', 'imdb']
    elif guess['type'] == MediaType.episode:
        needed = ['tmdb', 'imdb', 'tvdb', 'season', 'episode']

    if not contains_elements(needed, identificator):
        raise error.NotEnoughData("Needed idendificator couldn't be found")

    return identificator


def get_metadata(identificator, languages, providers):
    """ returns the metadata """

    metadata = None

    if identificator['type'] == MediaType.movie:
        metadata = {
            MetadataType.title: None,
            MetadataType.originaltitle: None,
            MetadataType.premiered: None,
            MetadataType.tagline: None,
            MetadataType.plot: None,
            MetadataType.set: None,
            MetadataType.certification: None,
            MetadataType.rating: None,
            MetadataType.votes: None,
            MetadataType.studios: [],
            MetadataType.countries: [],
            MetadataType.genres: [],
            MetadataType.directors: [],
            MetadataType.scriptwriters: [],
            MetadataType.actors: [],
        }
    elif identificator['type'] == MediaType.episode:
        metadata = {
            MetadataType.title: None,
            MetadataType.showtitle: None,
            MetadataType.plot: None,
            MetadataType.premiered: None,
            MetadataType.rating: None,
            MetadataType.votes: None,
        }
    elif identificator['type'] == MediaType.tvshow:
        metadata = {
            MetadataType.title: None,
            MetadataType.premiered: None,
            MetadataType.plot: None,
            MetadataType.certification: None,
            MetadataType.rating: None,
            MetadataType.votes: None,
            MetadataType.studios: [],
            MetadataType.genres: [],
            MetadataType.actors: [],
        }
    else:
        raise error.InvalidMediaType

    for metadatatype in metadata:
        for language in languages:
            for provider in providers[metadatatype]:
                metadata[metadatatype].update(provider.get_metadata(
                    identificator,
                    metadatatype,
                    language))

    return metadata


def get_images(identificator, languages, providers):
    """ returns a specific image url """

    images = None

    if identificator['type'] == MediaType.movie:
        images = {
            ImageType.poster: None,
            ImageType.background: None,
            ImageType.disc: None,
            ImageType.banner: None,
            ImageType.logo: None,
            ImageType.clearart: None,
            ImageType.art: None,
        }
    elif identificator['type'] == MediaType.episode:
        images = {
            ImageType.thumbnail: None,
        }
    elif identificator['type'] == MediaType.tvshow:
        images = {
            ImageType.poster: None,
            ImageType.background: None,
            ImageType.banner: None,
            ImageType.logo: None,
            ImageType.clearart: None,
            ImageType.charart: None,
            ImageType.art: None,
        }
    elif identificator['type'] == MediaType.season:
        images = {
            ImageType.poster: None,
        }
    else:
        raise error.InvalidMediaType

    for imagetype in images:
        for language in languages:
            for provider in providers:
                images[imagetype].update(provider.get_image(
                    identificator,
                    imagetype,
                    language))

    return images


# sorting
def sort(videofile, plugins, paths, languages, overwrite):
    """ sorts a videofile """
    videofile = {
        'basename': os.path.basename(videofile),
        'abspath': os.path.abspath(videofile),
        'extension': os.path.splitext(
            os.path.basename(videofile)
        )[1].lower()[1:]
    }

    print("\nProcessing \"{0}\"".format(videofile['abspath']))

    # get the data
    guess = get_guess(videofile['abspath'], plugins[PluginType.guess])
    identificator = get_identificator(guess, plugins[PluginType.identificator])
    metadata = get_metadata(identificator,
                            languages['metadata'],
                            plugins[PluginType.metadata])
    images = get_images(identificator,
                        languages['metadata'],
                        plugins[PluginType.images])

    # render the paths
    rendered_paths = get_paths(paths[identificator['type']], metadata)

    # create all the paths
    for path in rendered_paths:
        pathonly = os.path.dirname(path)
        if not os.path.exists(pathonly):
            os.makedirs(pathonly)

    # write the nfo
    if overwrite['nfo'] and not os.path.isfile(rendered_paths['nfo']):
        write_nfo(rendered_paths['template'], metadata, rendered_paths['nfo'])

    # download the images
    for image in images:
        if overwrite['images'] and not os.path.isfile(rendered_paths[image]):
            download(images[image], rendered_paths[image])

    # move the media
    if overwrite['media'] and not os.path.isfile(rendered_paths['media']):
        move(videofile['abspath'], rendered_paths['media'])
