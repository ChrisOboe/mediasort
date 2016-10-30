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
from guessit import guessit
from . import tmdb


def parse_nfo(nfofile):
    """ parses an nfo """
    import xml.etree.ElementTree
    try:
        xml = xml.etree.ElementTree.parse(nfofile)
    except xml.etree.ElementTree.ParseError as err:
        print(err)
        return {}

    nfo = {}
    root = xml.getroot()

    if root.tag == "movie":
        nfo['type'] = "movie"
        nfo['title'] = root.find('title').text
    elif root.tag == "episodedetails":
        nfo['type'] = "episode"

    wanted = ["releasegroup", "source", "tmdb_id", "episode", "season"]
    for i in wanted:
        entry = root.find(i)
        if entry is not None:
            nfo[i] = entry.text

    return nfo


def guess_vid(filename, nfofile, forced_type):
    """ guess based on nfo. if not found based on filename """
    guess = {}
    complete = False
    if os.path.exists(nfofile):
        complete = True
        logging.info("  Guessing by nfofile")
        nfo = parse_nfo(nfofile)
        if "type" in nfo:
            logging.info("    Found type: {0}".format(nfo["type"]))
            guess["type"] = nfo["type"]
            if guess["type"] == "episode" and "episode" in nfo:
                logging.info("    Found episode: {0}".format(nfo["episode"]))
                guess["episode"] = nfo["episode"]
            else: complete = False
            if guess["type"] == "episode" and "season" in nfo:
                logging.info("    Found season: {0}".format(nfo["season"]))
                guess["season"] = nfo["season"]
            else: complete = False
        else: complete = False
        if "tmdb_id" in nfo:
            logging.info("    Found TMDb ID: {0}".format(nfo["tmdb_id"]))
            guess["tmdb_id"] = nfo["tmdb_id"]
        else: complete = False
        if "releasegroup" in nfo:
            logging.info("    Found releasegroup: {0}".format(nfo["releasegroup"]))
            guess["releasegroup"] = nfo["releasegroup"]
        else: complete = False
        if "source" in nfo:
            logging.info("    Found source: {0}".format(nfo["source"]))
            guess["source"] = nfo["source"]
        else: complete = False

    if not complete:
        logging.info("  Guessing by filename")

        options = {}
        if "type" in guess and forced_type == None: forced_type = guess["type"]
        options['type'] = forced_type

        guess_filename = guessit(filename, options)

        if "type" not in guess:
            logging.info("    Guessed type: {0}".format(guess_filename["type"]))
            guess["type"] = guess_filename["type"]

        if "releasegroup" not in guess and "release_group" in guess_filename:
            logging.info("    Guessed releasegroup: {0}".format(guess_filename["release_group"]))
            guess["releasegroup"] = guess_filename["release_group"]

        if "source" not in guess and "format" in guess_filename:
            logging.info("    Guessed source: {0}".format(guess_filename["format"]))
            guess["source"] = guess_filename["format"]

        if guess["type"] == "episode":
            if "episode" not in guess and "episode" in guess_filename:
                logging.info("    Guessed episode: {0}".format(guess_filename["episode"]))
                guess["episode"] = guess_filename["episode"]

            if "seaseon" not in guess and "season" in guess_filename:
                logging.info("    Guessed season: {0}".format(guess_filename["season"]))
                guess["season"] = guess_filename["season"]

        if "tmdb_id" not in guess:
            title = None
            year = None
            if guess["type"] == "movie":
                if "title" in guess_filename:
                    logging.info("    Guessed title: {0}".format(guess_filename["title"]))
                    title = guess_filename["title"]

                if "year" in guess_filename:
                    logging.info("    Guessed year: {0}".format(guess_filename["year"]))
                    year = guess_filename["year"]

            if guess["type"] == "episode" and "title" in guess_filename:
                logging.info("    Guessed tvshow name: {0}".format(guess_filename["title"]))
                title = guess_filename["title"]

            guess["tmdb_id"] = tmdb.get_id(guess["type"], title, year)

    if "releasegroup" not in guess:
        guess['releasegroup'] = None
    if "source" not in guess:
        guess['source'] = None

    if guess["tmdb_id"] == None: raise LookupError("No TMDb entry found")
    if guess["type"] == "episode":
        if "episode" not in guess: raise LookupError("No episode number found")
        if "season" not in guess: raise LookupError("No season number found")
    return guess
