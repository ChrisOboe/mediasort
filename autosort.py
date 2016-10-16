#!/usr/bin/env python2
from __future__ import print_function

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

import dateutil
import json
from dicttoxml import dicttoxml

# debug stuff
import pprint
pp = pprint.PrettyPrinter(indent=4)


import config
args = config.parse_arguments()
config = config.parse_configfile(args.config)

import tmdb
tmdb.set_api_key(config['general']['tmdb_api_key']
tmdb_config = tmdb.get_config()

import guess
import fs

def download_images(tmdb, t, backdrop_destination, poster_destination):
    if config['general']['simulate_download'] == 'yes':
        print("SIMULATE: ", end = "")
    print("Downloading \"{0}\" to \"{1}\".".format(backdrop_url, backdrop_destination))
    if config['general']['simulate_download'] != 'yes':
        urllib.urlretrieve(backdrop_url, backdrop_destination)
    if config['general']['simulate_download'] == 'yes':
        print("SIMULATE: ", end = "")
    print("Downloading \"{0}\" to \"{1}\".".format(poster_url, poster_destination))
    if config['general']['simulate_download'] != 'yes':
        urllib.urlretrieve(poster_url, poster_destination)
    return

def write_nfo(tmdb, t, nfo_destination):
    if t == 'movie':
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
            if release['iso_3166_1'] == config['general']['language']:
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
        xml = dicttoxml(nfo, custom_root='movie', attr_type=False)
        if config['general']['simulate_nfo'] == 'yes':
            print("SIMULATE: ", end = "")
        print("Writing \"{0}\"".format(nfo_destination))
        if config['general']['simulate_nfo'] != 'yes':
            with open(nfo_destination, 'w') as nfofile:
                nfofile.write(xml)

    return

videofiles = fs.find_video_files(
        args['source'],
        config['general']['allowed_extensions'].split(),
        config['general']['minimal_file_size']
        )

# process files
for videofile in videofiles:
    videofile_basename = os.path.basename(videofile)
    videofile_abspath = os.path.abspath(videofile)
    videofile_extension = os.path.splitext(videofile_basename)[1]

    guess = guess.guess_vid(videofile_basename)

    if guess['type'] == 'movie':
        replacement_rules = {
            '%t':movie['title'],
            '%ot':movie['original_title'],
            '%y':str(dateutil.parser.parse(movie['release_date']).year)
            '%e':
                }

        movie = tmdb.get_movie_info(
                tmdb.get_tmdb_id(guess['name']),
                config['general']['language']
                )

        fs.move(videofile_abspath,
                get_movie_name(movie, config['movie']['video_destination']))

        helpers.download(
                tmdb_config['images']['secure_base_url']+config['movie']['backdrop_size']+movie['backdrop_path'],



        download_images(movie, guess['type'],
                get_movie_name(movie, config['movie']['backdrop_destination']),
                get_movie_name(movie, config['movie']['poster_destination']))
        #pp.pprint(movie)
        #print(movie['credits']['cast'])
        write_nfo(movie, 'movie', get_movie_name(movie, config['movie']['nfo_destination']))
    else:
        continue

