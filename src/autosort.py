#!/usr/bin/env python3

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

from pprint import pprint

import config
args = config.parse_arguments()
config = config.parse_configfile(args.config)

if args.force != "episode" and args.force != "movie": args.force = None

# logging
log = logging.getLogger()
log.setLevel(logging.INFO)

logout = logging.StreamHandler(sys.stdout)
logout.setLevel(logging.INFO)
log.addHandler(logout)

logging.getLogger("requests").setLevel(logging.WARNING)

import tmdb
tmdb.set_api_key(config['general']['tmdb_api_key'])
tmdb_config = tmdb.get_config(
        os.path.expanduser(config['general']['cache_path'])+'tmdb.cache',
        config['general']['tmdb_config_cache_days']
        )

if config['images']['https_download']:
    image_url = tmdb_config['images']['secure_base_url']
else:
    image_url = tmdb_config['images']['base_url']

from guess import guess_vid
import fs
import nfo

videofiles = fs.find_video_files(
    args.source,
    config['general']['allowed_extensions'],
    config['general']['minimal_file_size']
    )

# were caching tvshow entries to prevent redownloading the same again and again
tvshows = {}

# process files
for videofile in videofiles:

    videofile_basename = os.path.basename(videofile)
    videofile_abspath = os.path.abspath(videofile)
    videofile_extension = os.path.splitext(videofile_basename)[1].lower()[1:]

    print("\nProcessing \"{0}\"".format(videofile_abspath))
    try:
        guess = guess_vid(videofile_abspath, args.force)
    except LookupError as err:
        print(err)
        print("Skipping this file")
        continue

    tmdb_id = tmdb.get_id(guess['type'], guess['title'], None if 'year' not in guess else guess['year'])
    if not tmdb_id:
        continue

    if guess['type'] == 'movie':
        movie = tmdb.get_movie_info(tmdb_id, config['general']['language'])

        replacement_rules = {
            '$t':helpers.filter_fs_chars(movie['title']),
            '$ot':helpers.filter_fs_chars(movie['original_title']),
            '$y':str(dateutil.parser.parse(movie['release_date']).year),
            '$ext':videofile_extension
            }

        # move file
        try:
            fs.move(videofile_abspath,
                    helpers.replace_by_rule(replacement_rules, config['movie']['video_destination']),
                    config['general']['simulate_move'])
        except FileExistsError as err:
            print(err)
            print("Skipping this file")
            continue

        # download fanart
        helpers.download(
                image_url+config['images']['backdrop_size']+movie['backdrop_path'],
                helpers.replace_by_rule(replacement_rules, config['movie']['backdrop_destination']),
                config['general']['simulate_download']
                )

        # download poster
        helpers.download(
                image_url+config['images']['poster_size']+movie['poster_path'],
                helpers.replace_by_rule(replacement_rules, config['movie']['poster_destination']),
                config['general']['simulate_download']
                )

        # write nfo
        nfo.write_movie_nfo(
                movie,
                helpers.replace_by_rule(replacement_rules, config['movie']['nfo_destination']),
                config['general']['language'],
                config['general']['simulate_nfo']
                )

    elif guess['type'] == 'episode':
        if not tmdb_id in tvshows: tvshows[tmdb_id] = tmdb.get_tvshow_info(tmdb_id, config['general']['language'])
        episode = tmdb.get_episode_info(tmdb_id, guess['season'], guess['episode'], config['general']['language'])

        replacement_rules = {
            '$st':helpers.filter_fs_chars(tvshows[tmdb_id]['name']),
            '$sot':helpers.filter_fs_chars(tvshows[tmdb_id]['original_name']),
            '$y':str(dateutil.parser.parse(tvshows[tmdb_id]['first_air_date']).year),
            '$et':helpers.filter_fs_chars(episode['name']),
            '$sn':str(episode['season_number']).zfill(2),
            '$en':str(episode['episode_number']).zfill(2),
            '$ext':videofile_extension
            }

        # move file
        try:
            fs.move(videofile_abspath,
                    helpers.replace_by_rule(replacement_rules, config['episode']['video_destination']),
                    config['general']['simulate_move'])
        except FileExistsError as err:
            print(err)
            print("Skipping this file")
            continue

        # download series poster
        helpers.download(
            image_url
                +config['images']['poster_size']
                +tvshows[tmdb_id]['poster_path'],
            helpers.replace_by_rule(replacement_rules, config['episode']['series_poster_destination']),
            config['general']['simulate_download']
            )

        # download series backdrop
        helpers.download(
            image_url
                +config['images']['backdrop_size']
                +tvshows[tmdb_id]['backdrop_path'],
            helpers.replace_by_rule(replacement_rules, config['episode']['series_backdrop_destination']),
            config['general']['simulate_download']
            )

        # download season poster
        helpers.download(
            image_url
                +config['images']['poster_size']
                +tvshows[tmdb_id]['seasons'][episode['season_number']]['poster_path'],
            helpers.replace_by_rule(replacement_rules, config['episode']['season_poster_destination']),
            config['general']['simulate_download']
            )

        # download episode_thumb
        helpers.download(
            image_url
                +config['images']['thumb_size']
                +episode['still_path'],
            helpers.replace_by_rule(replacement_rules, config['episode']['episode_thumb_destination']),
            config['general']['simulate_download']
            )

        # write series nfo
        nfo.write_series_nfo(
                tvshows[tmdb_id],
                helpers.replace_by_rule(replacement_rules, config['episode']['series_nfo_destination']),
                config['general']['language'],
                config['general']['simulate_nfo']
                )

        # write episode nfo
        nfo.write_episode_nfo(
                tvshows[tmdb_id],
                episode,
                helpers.replace_by_rule(replacement_rules, config['episode']['episode_nfo_destination']),
                config['general']['simulate_nfo']
                )

    else:
        continue

