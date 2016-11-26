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

""" helpers for guessit """

import os
import logging
from datetime import datetime
import xml.etree.ElementTree

from guessit import guessit
from . import tmdb
from . import helpers
from .enums import MediaType


def guess_nfo(nfofile):
    """ returns a guess based on a nfo """

    logging.info("    Guessing based on nfo")

    try:
        xmlfile = xml.etree.ElementTree.parse(nfofile)
    except xml.etree.ElementTree.ParseError:
        logging.info("      Malformed nfo")
        return {}

    guess = {}
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

    # special treatment for ids
    guess['ids'] = {}
    ids = root.find("ids")
    wanted = ["tmdb", "tvdb", "imdb"]
    for i in wanted:
        entry = ids.find(i)
        if entry is not None:
            guess['ids'][i] = entry.text

    return guess


def guess_filename(filename):
    """ returns a guess based on the filename """

    logging.info("    Guessing based on filename")

    nameguess = guessit(filename)

    guess = {}

    if "title" in nameguess:
        guess["title"] = nameguess["title"]

    if nameguess["type"] == "movie":
        guess["type"] = MediaType.movie
        if "year" in nameguess:
            guess["year"] = datetime.strptime(str(nameguess["year"]), "%Y")
    elif nameguess["type"] == "episode":
        guess["type"] = MediaType.episode
        guess["episode"] = nameguess["episode"]
        guess["season"] = nameguess["season"]

    if "format" in nameguess:
        guess["source"] = nameguess["format"]

    if "release_group" in nameguess:
        guess["releasegroup"] = nameguess["release_group"]

    return guess


def guess_vid(filename, nfofile):
    """ guess based on nfo. if not found based on filename """

    logging.info("  Trying to guess file")

    if os.path.exists(nfofile):
        guess = guess_nfo(nfofile)
    else:
        guess = {}

    helpers.merge_dict(guess, guess_filename(filename))

    for entry in guess:
        logging.info("    Guessed %s as %s", entry, guess[entry])

    if "ids" not in guess or \
       "tmdb" not in guess["ids"] or \
       "imdb" not in guess["ids"] or \
       ("tvdb" not in guess["ids"] and guess["type"] == MediaType.episode):
        guess["ids"] = tmdb.get_ids(guess["type"],
                                    guess["title"],
                                    None if "year" not in guess else guess["year"])

    if "ids" not in guess:
        raise LookupError("No IDs found")
    if guess["type"] == MediaType.episode:
        if "episode" not in guess:
            raise LookupError("No episode number found")
        if "season" not in guess:
            raise LookupError("No season number found")

    return guess
