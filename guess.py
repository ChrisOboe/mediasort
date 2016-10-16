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

def guess_vid(filename):
    print("Guessing {0}".format(filename))
    guess = guessit(filename)
    if guess['type'] == 'episode':
        print("Guessed type:    episode")
        print("Guessed title:   {0}".format(guess['title']))
        print("Guessed season:  {0}".format(guess['season']))
        print("Guessed episode: {0}".format(guess['episode']))
    elif guess['type'] == 'movie':
        print("Guessed type:  movie")
        print("Guessed title: {0}".format(guess['title']))
        if 'year' in guess: print("Guessed year:  {0}".format(guess['year']))
    else:
        print("Can't guess type.")
    return guess
