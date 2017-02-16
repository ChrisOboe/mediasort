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

import os
import re
import xml.etree.ElementTree

from .enums import MediaType


def get_guess(filepath, config):
    # pylint: disable=unused-argument
    """ returns a guess based on a nfo """

    guess = {
        'filepath': filepath,
    }

    nfofile = os.path.splitext(filepath)[0] + ".nfo"

    try:
        xmlfile = xml.etree.ElementTree.parse(nfofile)
    except xml.etree.ElementTree.ParseError:
        raise LookupError("Malformed nfo")

    root = xmlfile.getroot()

    if root.tag == "movie":
        guess["type"] = MediaType.movie
        guess["title"] = root.find("title").text
    elif root.tag == "episodedetails":
        guess["type"] = MediaType.episode
        guess["title"] = root.find("showtitle").text

    wanted = ["releasegroup", "source", "episode", "season"]
    for i in wanted:
        entry = root.find(i)
        if entry is not None:
            guess[i] = entry.text

    return guess


def get_identificator(guess, identificator, config):
    # pylint: disable=unused-argument
    """ tries to find imdb ids in nfo """

    nfofile = os.path.splitext(guess['filepath'])[0] + ".nfo"
    with open(nfofile, 'r') as nfo:
        for line in nfo:
            imdb_id = re.search(r'tt\d{7}', line)
            if imdb_id is not None:
                identificator['imdb'] = imdb_id.group(0)
                break

    return identificator


