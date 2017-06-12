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
import copy
from shutil import move
import logging

from mediasort import error
from mediasort.enums import PluginType
from mediasort.template import get_paths, write_nfo
from mediasort.download import download


# create logger
logger = logging.getLogger('mediasort')


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
        logger.debug("Using {0} to guess from file".format(provider.__name__))
        try:
            guess.update(provider.get_guess(filepath))
        except error.NotEnoughData:
            logger.debug("{0} didn't got anything".format(provider.__name__))
            pass

    if 'type' not in guess:
        raise error.NotEnoughData("Needed value couldn't be guessed")

    needed = ['filepath', 'title']
    needed.extend(guess['type'].value.neededGuess.value)

    if not contains_elements(needed, guess):
        raise error.NotEnoughData("Needed value couldn't be guessed")

    logger.debug("Guessed as {0}".format(guess['type'].name))
    return guess


def get_identificator(guess, providers, ids, callback):
    """ returns a identificator for a guess """

    identificator = {'type': guess['type']}
    for idtype in guess['type'].value.idTypes.value:
        identificator[idtype] = None

    for provider in providers[guess['type'].name]:
        logger.debug("Using {0} to get ids".format(provider.__name__))
        try:
            identificator.update(
                provider.get_identificator(guess, identificator, callback)
            )
        except error.NotEnoughData:
            logger.debug("{0} didn't got anything".format(provider.__name__))
            pass

    if not contains_elements(ids['wanted'][guess['type'].name], identificator):
        raise error.NotEnoughData(
            "Needed id wasn't provided by any selected identificator"
        )

    return identificator


def get_metadata(identificator, languages, providers):
    """ returns the metadata """

    metadata = {}
    for metadatatype in identificator['type'].value.metadataTypes.value:
        metadata[metadatatype] = None

    for metadatatype in metadata:
        for language in languages:
            for provider in providers[metadatatype]:
                if metadata[metadatatype] is None:
                    logger.debug("Using {0}/{2} to get {1}".format(
                        provider.__name__,
                        metadatatype,
                        language
                    ))
                    metadata[metadatatype] = provider.get_metadata(
                        identificator,
                        metadatatype,
                        language
                    )

    return metadata


def get_images(identificator, languages, providers):
    """ returns a specific image url """

    images = {}
    for imagetype in identificator['type'].value.imageTypes.value:
        images[imagetype] = None

    for imagetype in images:
        for language in languages:
            for provider in providers[imagetype]:
                if images[imagetype] is None:
                    logger.debug("Using {0}/{2} to get {1}".format(
                        provider.__name__,
                        imagetype,
                        language
                    ))
                    images[imagetype] = provider.get_image(
                        identificator,
                        imagetype,
                        language
                    )

    return images


# sorting helpers
def meta_sort(guess, identificator, metadata, plugins, paths, languages,
              overwrite):
    """ writes nfo and downloads images"""
    images = get_images(
        identificator,
        languages['metadata'],
        plugins[PluginType.images.name][identificator['type'].name]
    )

    # write the nfo
    if overwrite['nfo'] or not os.path.isfile(paths['nfo']):
        logger.debug("Writing " + paths['nfo'])
        write_nfo(paths['template'],
                  {'metadata': metadata,
                   'identificator': identificator,
                   'guess': guess},
                  paths['nfo'])

    # download the images
    for image in images:
        if images[image] and \
           (overwrite['images'] or not os.path.isfile(paths[image])):
            logger.debug("Downloading " + paths[image])
            download(images[image], paths[image])


# sorting
def sort(videofile, plugins, ids, paths, languages, overwrite=False,
         callbacks=None):
    """ sorts a videofile """
    videofile = {
        'basename': os.path.basename(videofile),
        'abspath': os.path.abspath(videofile),
        'extension': os.path.splitext(
            os.path.basename(videofile)
        )[1].lower()[1:]
    }

    if not callbacks:
        callbacks = {}

    logger.info("Processing \"{0}\"".format(videofile['abspath']))

    try:
        guess = get_guess(videofile['abspath'], plugins[PluginType.guess.name])
        identificator = get_identificator(guess,
                                          plugins[PluginType.identificator.name],
                                          ids,
                                          callbacks.get('identificator'))
    except error.NotEnoughData as e:
        logger.error(str(e))
        logger.debug("---- Cut here ----\n")
        return None
    except error.CallbackBreak:
        logger.debug("---- Cut here ----\n")
        return None

    metadata = get_metadata(
        identificator,
        languages['metadata'],
        plugins[PluginType.metadata.name][identificator['type'].name]
    )

    # get paths
    try:
        rendered_paths = get_paths(paths[identificator['type'].name], metadata)
    except PermissionError as e:
        logger.error("You don't have needed permissions: {0}".format(e))
        logger.debug("---- Cut here ----\n")
        return None

    # create base path
    os.makedirs(rendered_paths['base'], exist_ok=True)

    # write nfo and download images
    try:
        meta_sort(guess, identificator, metadata, plugins, rendered_paths,
                  languages, overwrite)
    except FileNotFoundError as e:
        logger.error("A needed file wasn't found: {0}".format(e))
        logger.debug("---- Cut here ----\n")
        return None

    # move the media
    if overwrite['media'] or not os.path.isfile(rendered_paths['media']):
        logger.debug("Moving media to " + rendered_paths['media'])
        #move(
        #    videofile['abspath'],
        #    "{0}.{1}".format(rendered_paths['media'], videofile['extension'])
        #)

    # sort successors
    if hasattr(identificator['type'], 'successors'):
        for mediatype in identificator['type'].successors:
            newIdentificator = copy.deepcopy(identificator)
            newIdentificator['type'] = mediatype
            newMetadata = get_metadata(newIdentificator,
                                    languages['metadata'],
                                    plugins[PluginType.metadata.name])
            newPaths = get_paths(paths[newIdentificator['type'].__name__],
                                 metadata)
            meta_sort(guess, newIdentificator, newMetadata, plugins, newPaths,
                      languages, overwrite)

    logger.debug("---- Cut here ----\n")
