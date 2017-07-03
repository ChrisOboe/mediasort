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

""" provides guesses from filename """

import logging
from datetime import datetime

from guessit import guessit

from mediasort import error
from mediasort.enums import MediaType

# create logger
logger = logging.getLogger('mediasort')


def init(config):
    pass


def get_guess(filepath):
    """ returns a guess based on the filename """

    guess = {
        'filepath': filepath,
    }

    nameguess = guessit(filepath)

    if "title" in nameguess:
        if isinstance(nameguess['title'], list):
            guess["title"] = nameguess["title"][0]
        else:
            guess["title"] = nameguess["title"]
        logger.debug("Guessed title: {0}".format(guess['title']))

    if nameguess["type"] == "movie":
        guess["type"] = MediaType.movie
        if "year" in nameguess:
            guess["year"] = datetime.strptime(str(nameguess["year"]), "%Y")
    elif nameguess["type"] == "episode":
        if 'episode' not in nameguess:
            raise error.NotEnoughData("No episode number found")
        if 'season' not in nameguess:
            raise error.NotEnoughData("No season number found")
        guess["type"] = MediaType.episode
        if isinstance(nameguess['episode'], list):
            guess["episode"] = nameguess["episode"][0]
        else:
            guess["episode"] = nameguess["episode"]
        guess["season"] = nameguess["season"]

    if "format" in nameguess:
        guess["source"] = nameguess["format"]

    if "release_group" in nameguess:
        guess["releasegroup"] = nameguess["release_group"]

    return guess
