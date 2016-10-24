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

from guessit import guessit
import logging

def guess_vid(filename, forced_type):
    logging.info("  Guessing by filename")
    options = {}
    options['type'] = forced_type
    guess = guessit(filename, options)
    if guess['type'] == 'episode':
        logging.info("    Guessed type:    episode")
        if 'title' in guess: logging.info("    Guessed title:   {0}".format(guess['title']))
        if 'season' in guess:
            logging.info("    Guessed season:  {0}".format(guess['season']))
        else:
            raise LookupError("Couldn't guess season")
        if 'episode' in guess:
            logging.info("    Guessed episode: {0}".format(guess['episode']))
        else:
            raise LookupError("Couldn't guess episode")
    elif guess['type'] == 'movie':
        logging.info("    Guessed type:  movie")
        logging.info("    Guessed title: {0}".format(guess['title']))
        if 'year' in guess: logging.info("    Guessed year:  {0}".format(guess['year']))
    return guess
