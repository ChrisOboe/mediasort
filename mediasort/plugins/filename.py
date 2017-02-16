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

from .enums import MediaType


def get_guess(filepath, config):
    # pylint: disable=unused-argument
    """ returns a guess based on the filename """

    logging.info("Guessing based on filename")

    guess = {
        'filepath': filepath,
    }

    nameguess = guessit(filepath)

    if "title" in nameguess:
        guess["title"] = nameguess["title"]

    if nameguess["type"] == "movie":
        guess["type"] = MediaType.movie
        if "year" in nameguess:
            guess["year"] = datetime.strptime(str(nameguess["year"]), "%Y")
    elif nameguess["type"] == "episode":
        if 'episode' not in nameguess:
            raise LookupError("No episode number found")
        if 'season' not in nameguess:
            raise LookupError("No season number found")
        guess["type"] = MediaType.episode
        guess["episode"] = nameguess["episode"]
        guess["season"] = nameguess["season"]

    if "format" in nameguess:
        guess["source"] = nameguess["format"]

    if "release_group" in nameguess:
        guess["releasegroup"] = nameguess["release_group"]

    return guess
