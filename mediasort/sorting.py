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

    # TODO: the mediatype shouldn't be hardcoded anywere.
    # think about a possible solution
    needed = ['filepath', 'title', 'type']
    if guess['type'] == MediaType.episode:
        needed.extend(['season', 'episode'])

    if not contains_elements(needed, guess):
        raise error.NotEnoughData("Needed value couldn't be guessed")

    return guess


def get_identificator(guess, providers, ids):
    """ returns a identificator for a guess """

    identificator = {'type': guess['type']}
    for idtype in guess['type'].IdType:
        identificator[idtype] = None

    for provider in providers[guess['type']]['modules']:
        identificator.update(provider.get_identificator(guess, identificator))

    if not contains_elements(ids['wanted'], identificator):
        raise error.NotEnoughData(
            "Needed id wasn't provided by any selected identificator"
        )

    return identificator


def get_metadata(identificator, languages, providers):
    """ returns the metadata """

    metadata = {}
    for metadatatype in identificator['type'].metadataTypes:
        metadata[metadatatype] = None

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

    images = {}
    for imagetype in identificator['type'].imageTypes:
        images[imagetype] = None

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
