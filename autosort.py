#!/usr/bin/env python2

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
import sys
import os
import logging
import helpers

import config
args = config.parse_arguments()
config = config.parse_configfile(args.config)

# logging
log = logging.getLogger()
log.setLevel(logging.INFO)

logout = logging.StreamHandler(sys.stdout)
logout.setLevel(logging.INFO)
log.addHandler(logout)

logging.getLogger("dicttoxml").setLevel(logging.WARNING)

import tmdb
tmdb.set_api_key(config['general']['tmdb_api_key'])
tmdb_config = tmdb.get_config(
        os.path.expanduser(config['general']['cache_path'])+'tmdb.cache',
        config['general']['tmdb_config_cache_days']
        )

import guess
import fs
import nfo

videofiles = fs.find_video_files(
        args.source,
        config['general']['allowed_extensions'].split(),
        config['general']['minimal_file_size']
        )

# process files
for videofile in videofiles:
    videofile_basename = os.path.basename(videofile)
    videofile_abspath = os.path.abspath(videofile)
    videofile_extension = os.path.splitext(videofile_basename)[1]

    print("Processing \"{0}\"".format(videofile_abspath))

    guess = guess.guess_vid(videofile_basename)

    if guess['type'] == 'movie':
        movie = tmdb.get_movie_info(
                tmdb.get_id(guess['title'], 0 if 'year' not in guess else guess['year']),
                config['general']['language']
                )

        replacement_rules = {
            '%m':config['movie']['main_path'],
            '%t':movie['title'],
            '%ot':movie['original_title'],
            '%y':str(dateutil.parser.parse(movie['release_date']).year),
            '%e':videofile_extension
            }

        # move file
        fs.move(videofile_abspath,
                helpers.replace_by_rule(replacement_rules, config['movie']['video_destination']),
                config['general']['simulate_move'])

        # download fanart
        helpers.download(
                tmdb_config['images']['secure_base_url']+config['movie']['backdrop_size']+movie['backdrop_path'],
                helpers.replace_by_rule(replacement_rules, config['movie']['backdrop_destination']),
                True if config['general']['simulate_download'] == "yes" else False
                )

        # download poster
        helpers.download(
                tmdb_config['images']['secure_base_url']+config['movie']['poster_size']+movie['poster_path'],
                helpers.replace_by_rule(replacement_rules, config['movie']['poster_destination']),
                True if config['general']['simulate_download'] == "yes" else False
                )

        # write nfo
        nfo.write_movie_nfo(
                movie,
                helpers.replace_by_rule(replacement_rules, config['movie']['nfo_destination']),
                config['general']['language'],
                True if config['general']['simulate_nfo'] == "yes" else False
                )
    else:
        continue
