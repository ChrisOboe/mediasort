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

import logging
from helpers import create_path
from dicttoxml import dicttoxml

def write_movie_nfo(tmdb, nfo_destination, language, simulate):
    studios = []
    genres = []
    actors = []
    mpaa = "Not available"
    for studio in tmdb['production_companies']:
        studios.append(studio['name'])
    for genre in tmdb['genres']:
        genres.append(genre['name'])
    for actor in tmdb['credits']['cast']:
        a = {}
        a['name'] = actor['name']
        a['role'] = actor['character']
        actors.append(a)
    for release in tmdb['release_dates']['results']:
        if release['iso_3166_1'] == language:
            mpaa = release['release_dates']['certification']

    nfo = {}
    nfo['title'] = tmdb['title']
    nfo['originaltitle'] = tmdb['original_title']
    nfo['year'] = tmdb['release_date'] # maybe we only want a year
    nfo['rating'] = tmdb['vote_average']
    nfo['votes'] = tmdb['vote_count']
    nfo['plot'] = tmdb['overview']
    nfo['tagline'] = tmdb['tagline']
    nfo['runtime'] = tmdb['runtime']
    nfo['mpaa'] = mpaa
    nfo['studio'] = studios
    nfo['genre'] = genres
    nfo['genre'] = actors
    #nfo['id'] = tmdb['imdb_id']
    my_item_func = lambda x: 'list_item'
    xml = dicttoxml(nfo, custom_root='movie', attr_type=False, item_func=my_item_func)
    logmsg = "Writing \"{0}\"".format(nfo_destination)

    if simulate:
        logging.info("SIMULATE: {0}".format(logmsg))
    else:
        logging.info(logmsg)
        create_path(nfo_destination)
        with open(nfo_destination, 'w') as nfofile:
            nfofile.write(xml)

