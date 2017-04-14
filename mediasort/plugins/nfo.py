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

""" provides guesses from nfo """

import logging
import os
import re
import xml.etree.ElementTree

from mediasort.enums import MediaType
from mediasort import error


def init(config):
    pass


def get_guess(filepath):
    """ returns a guess based on a nfo """

    guess = {
        'filepath': filepath,
    }

    nfofile = os.path.splitext(filepath)[0] + ".nfo"

    try:
        xmlfile = xml.etree.ElementTree.parse(nfofile)
    except xml.etree.ElementTree.ParseError:
        raise error.NotEnoughData("no xml based nfo")
    except FileNotFoundError:
        raise error.NotEnoughData("nfo not found")

    root = xmlfile.getroot()

    if root.tag == "movie":
        guess["type"] = MediaType.movie
        entry = root.find('title')
        if entry is not None:
            guess['title'] = entry.text
    elif root.tag == "episodedetails":
        guess["type"] = MediaType.episode
        entry = root.find('showtitle')
        if entry is not None:
            guess['title'] = entry.text

    wanted = ["releasegroup", "source", "episode", "season"]
    for i in wanted:
        entry = root.find(i)
        if entry is not None:
            guess[i] = entry.text

    return guess


def get_identificator_list(mediatype):
    if mediatype == MediaType.movie.name or \
       mediatype == MediaType.episode.name:
        return ['imdb']


def get_identificator(guess, identificator, callback):
    """ tries to find imdb ids in nfo """

    nfofile = os.path.splitext(guess['filepath'])[0] + ".nfo"
    try:
        with open(nfofile, 'r') as nfo:
            for line in nfo:
                imdb_id = re.search(r'tt\d{7}', line)
                if imdb_id is not None:
                    identificator['imdb'] = imdb_id.group(0)
                    break
    except FileNotFoundError:
        raise error.NotEnoughData("nfo not found")
    except UnicodeDecodeError:
        raise error.NotEnoughData("Invalid char in nfo")

    return identificator
