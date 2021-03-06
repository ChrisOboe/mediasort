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

from enum import Enum
from mediasort.mediatypes import season, tvshow

class episode(Enum):
    neededGuess = ['title', 'season', 'episode']

    def get_successors():
        from mediasort.enums import MediaType
        return [MediaType.tvshow, MediaType.season]

    idTypes = {
        'tmdb': "tmdb",
        'tvdb': "tvdb",
        'season': "season",
        'episode': "episode",
    }

    metadataTypes = {
        'title': "title",
        'showtitle': "showtitle",
        'premiered': "premiered",
        'show_premiered': "show_premiered",
        'plot': "plot",
        'rating': "rating",
        'votes': "votes",
        'studios': "studios",
        'networks': "networks",
        'directors': "directors",
        'scriptwriters': "scriptwriters",
        'actors': "actors",
        'certification': "certification"
    }

    imageTypes = {
        'thumbnail': "thumbnail",
    }
