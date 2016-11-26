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


""" some enums used everywhere in the programm """

from enum import Enum


class MediaType(Enum):
    """ enum for mediatypes """
    (movie,
     tvshow,
     season,
     episode,
     artist,
     album) = range(6)


class ImageType(Enum):
    """ enum for imagetypes """
    (poster,
     background,
     logo,
     disc,
     art,
     clearart,
     banner,
     charart,
     thumb) = range(9)
