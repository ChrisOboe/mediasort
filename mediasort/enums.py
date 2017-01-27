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
    movie = "movie"
    tvshow = "tvshow"
    season = "season"
    episode = "episode"
    artist = "artist"
    album = "album"


class ImageType(Enum):
    """ enum for imagetypes """
    poster = "poster"
    background = "background"
    disc = "disc"
    banner = "banner"
    logo = "logo"
    charart = "charart"
    clearart = "clearart"
    art = "art"
    thumbnail = "thumbnail"


class MetadataType(Enum):
    """ enum for movie metadata """
    title = "title"
    originaltitle = "originaltitle"
    set = "set"
    premiered = "premiered"
    tagline = "tagline"
    plot = "plot"
    certification = "certification"
    rating = "rating"
    votes = "votes"
    studios = "studios"
    countries = "countries"
    genres = "genres"
    writers = "writers"
    directors = "directors"
    actors = "actors"


class ConfigError(Exception):
    """ Should be raised when configuration is invalid """
    pass


class NotEnoughData(Exception):
    """ Should be raised when a needet value is missing """
    pass
