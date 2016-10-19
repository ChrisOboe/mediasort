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
import collections
#from pprint import pprint

def write_movie_nfo(tmdb, nfo_destination, language, simulate):
    #pprint(tmdb)

    # get the metadata
    general = collections.OrderedDict()
    general['title'] = tmdb['title']
    general['originaltitle'] = tmdb['original_title']
    if tmdb['belongs_to_collection']:
        general['set'] = tmdb['belongs_to_collection']
    general['year'] = tmdb['release_date'] # maybe we only want a year

    general['runtime'] = str(tmdb['runtime'])
    general['mpaa'] = "Not available"
    for release in tmdb['release_dates']['results']:
        if release['iso_3166_1'] == language:
            general['mpaa'] = str(release['release_dates'][0]['certification'])

    general['tagline'] = tmdb['tagline']
    general['plot'] = tmdb['overview']
    general['rating'] = str(tmdb['vote_average'])
    general['votes'] = str(tmdb['vote_count'])

    studios = []
    for studio in tmdb['production_companies']:
        studios.append(studio['name'])

    countries = []
    for country in tmdb['production_countries']:
        countries.append(country['name'])

    directors = []
    writers = []
    for crew in tmdb['credits']['crew']:
        if crew['job'] == 'Director': directors.append(crew['name'])
        if crew['job'] == 'Writer': writers.append(crew['name'])

    genres = []
    for genre in tmdb['genres']:
        genres.append(genre['name'])

    actors = []
    for actor in tmdb['credits']['cast']:
        a = {}
        a['name'] = actor['name']
        a['role'] = actor['character']
        actors.append(a)

    nfo = ("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
           "<movie>\n")
    for item in general:
        nfo += "\t<{0}>{1}</{0}>\n".format(item, general[item])
    for genre in genres:
        nfo += "\t<genre>{0}</genre>\n".format(genre)
    for director in directors:
        nfo += "\t<director>{0}</director>\n".format(director)
    for writer in writers:
        nfo += "\t<credits>{0}</credits>\n".format(writer)
    for studio in studios:
        nfo += "\t<studio>{0}</studio>\n".format(studio)
    for country in countries:
        nfo += "\t<country>{0}</country>\n".format(country)
    for actor in actors:
        nfo += ("\t<actor>\n"
                "\t\t<name>{0}</name>\n"
                "\t\t<role>{1}</role>\n"
                "\t</actor>\n").format(actor['name'], actor['role'])

    nfo += "</movie>"

    logging.info("  Writing \"{0}\"".format(nfo_destination))
    if not simulate:
        create_path(nfo_destination)
        with open(nfo_destination, 'w') as nfofile:
            nfofile.write(nfo)

