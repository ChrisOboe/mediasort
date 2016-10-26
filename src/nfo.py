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

series_written = []

def get_actors(tmdb):
    actors = []
    for actor in tmdb['credits']['cast']:
        a = {}
        a['name'] = actor['name']
        a['role'] = actor['character']
        actors.append(a)
    return actors

def get_genres(tmdb):
    genres = []
    for genre in tmdb['genres']:
        genres.append(genre['name'])
    return genres

def write_nfo(nfo, destination, simulate):
    logging.info("  Writing \"{0}\"".format(destination))
    if not simulate:
        create_path(destination)
        with open(destination, 'w') as nfofile:
            nfofile.write(nfo)

def write_series_nfo(series, nfo_destination, language, simulate, overwrite):
    if not overwrite and os.path.exists(nfo_destination): return
    if nfo_destination in series_written: return

    general = collections.OrderedDict()
    general['title'] = series['name']
    general['rating'] = series['vote_average']
    general['votes'] = series['vote_count']
    general['plot'] = series['overview']
    general['premiered'] = series['first_air_date']
    general['runtime'] = str(series['episode_run_time'][0])
    general['mpaa'] = "Not available"
    for rating in series['content_ratings']['results']:
        if rating['iso_3166_1'] == language:
            general['mpaa'] = rating['rating']
    general['tmdb_id'] = series['id']

    studios = []
    for studio in series['networks']:
        studios.append(studio['name'])

    genres = get_genres(series)
    actors = get_actors(series)

    nfo = ("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
           "<tvshow>\n")
    for item in general:
        nfo += "\t<{0}>{1}</{0}>\n".format(item, general[item])
    for genre in genres:
        nfo += "\t<genre>{0}</genre>\n".format(genre)
    for studio in studios:
        nfo += "\t<studio>{0}</studio>\n".format(studio)
    for actor in actors:
        nfo += ("\t<actor>\n"
                "\t\t<name>{0}</name>\n"
                "\t\t<role>{1}</role>\n"
                "\t</actor>\n").format(actor['name'], actor['role'])
    nfo += "</tvshow>"

    write_nfo(nfo, nfo_destination, simulate)
    series_written.append(nfo_destination)

def write_episode_nfo(series, episode, releasegroup, source, nfo_destination, simulate, overwrite):
    if not overwrite and os.path.exists(nfo_destination): return

    general = collections.OrderedDict()
    general['title'] = episode['name']
    general['showtitle'] = series['name']
    general['rating'] = episode['vote_average']
    general['votes'] = episode['vote_count']
    general['season'] = episode['season_number']
    general['episode'] = episode['episode_number']
    general['plot'] = episode['overview']
    general['aired'] = episode['air_date']
    if releasegroup: general['releasegroup'] = releasegroup
    if source: general['source'] = source
    general['tmdb_id'] = series['id']

    directors = []
    writers = []
    for crew in episode['crew']:
        if crew['job'] == 'Director': directors.append(crew['name'])
        if crew['job'] == 'Writer': writers.append(crew['name'])

    nfo = ("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
           "<episodedetails>\n")
    for item in general:
        nfo += "\t<{0}>{1}</{0}>\n".format(item, general[item])
    for director in directors:
        nfo += "\t<director>{0}</director>\n".format(director)
    for writer in writers:
        nfo += "\t<credits>{0}</credits>\n".format(writer)
    nfo += "</episodedetails>"

    write_nfo(nfo, nfo_destination, simulate)

def write_movie_nfo(movie, releasegroup, source, nfo_destination, language, simulate, overwrite):
    if not overwrite and os.path.exists(nfo_destination): return
    # get the metadata
    general = collections.OrderedDict()
    general['title'] = movie['title']
    general['originaltitle'] = movie['original_title']
    if movie['belongs_to_collection']:
        general['set'] = movie['belongs_to_collection']['name']
    general['year'] = movie['release_date'] # maybe we only want a year

    general['runtime'] = str(movie['runtime'])
    general['mpaa'] = "Not available"
    for release in movie['release_dates']['results']:
        if release['iso_3166_1'] == language:
            general['mpaa'] = str(release['release_dates'][0]['certification'])

    general['tagline'] = movie['tagline']
    general['plot'] = movie['overview']
    general['rating'] = str(movie['vote_average'])
    general['votes'] = str(movie['vote_count'])
    if releasegroup: general['releasegroup'] = releasegroup
    if source: general['source'] = source
    general['tmdb_id'] = movie['id']

    studios = []
    for studio in movie['production_companies']:
        studios.append(studio['name'])

    countries = []
    for country in movie['production_countries']:
        countries.append(country['name'])

    directors = []
    writers = []
    for crew in movie['credits']['crew']:
        if crew['job'] == 'Director': directors.append(crew['name'])
        if crew['job'] == 'Writer': writers.append(crew['name'])

    genres = get_genres(movie)
    actors = get_actors(movie)

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

    write_nfo(nfo, nfo_destination, simulate)
