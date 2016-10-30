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

import os
import dateutil

from .guess import guess_vid
from . import helpers
from . import fs
from . import nfo
from . import tmdb
from . import config

# were caching tvshow entries to prevent redownloading the same again and again
TVSHOWS = {}


def sort(videofile, config, force=None):
    """ sorts a videofile """
    videofile_basename = os.path.basename(videofile)
    videofile_abspath = os.path.abspath(videofile)
    videofile_extension = os.path.splitext(videofile_basename)[1].lower()[1:]
    nfofile = os.path.splitext(videofile_abspath)[0]+".nfo"

    dst = None
    downloads = {}

    print("\nProcessing \"{0}\"".format(videofile_abspath))

    try:
        guess = guess_vid(videofile_abspath, nfofile, force)
    except LookupError as err:
        print(err)
        print("Skipping this file")
        return

    if guess['type'] == 'movie':
        movie = tmdb.get_movie_info(guess["tmdb_id"],
                                    config['general']['language'])

        replacers = {
            '$t': helpers.filter_fs_chars(movie['title']),
            '$ot': helpers.filter_fs_chars(movie['original_title']),
            '$y': str(dateutil.parser.parse(movie['release_date']).year),
            '$ext': videofile_extension
        }

        dst = helpers.replace_by_rule(replacers, config['movie']['movie'])
        if os.path.exists(dst) and config['general']['overwrite_videos']:
            return

        downloads = {
            config['tmdb']['base_url']
            + config['tmdb']['backdrop_size']
            + movie['backdrop_path']:
            helpers.replace_by_rule(replacers, config['movie']['backdrop']),

            config['tmdb']['base_url']
            + config['tmdb']['poster_size']
            + movie['poster_path']:
            helpers.replace_by_rule(replacers, config['movie']['poster']),
        }

        # write nfo
        nfo.write_movie_nfo(
            movie=movie,
            dst=helpers.replace_by_rule(replacers, config['movie']['nfo']),
            language=config['general']['language'],
            releasegroup=guess['releasegroup'],
            source=guess['source'],
            simulate=config['debug']['simulate_nfo'],
            overwrite=config['general']['overwrite_nfos']
        )

    elif guess['type'] == 'episode':
        if not guess["tmdb_id"] in TVSHOWS:
            TVSHOWS[guess["tmdb_id"]] = tmdb.get_tvshow_info(
                guess["tmdb_id"],
                config['general']['language']
                )

        tvshow = TVSHOWS[guess['tmdb_id']]

        episode = tmdb.get_episode_info(guess['tmdb_id'],
                                        guess['season'],
                                        guess['episode'],
                                        config['general']['language'])

        season = None
        for tmp_season in tvshow['seasons']:
            if tmp_season['season_number'] == episode['season_number']:
                season = tmp_season

        replacers = {
            '$st': helpers.filter_fs_chars(tvshow['name']),
            '$sot': helpers.filter_fs_chars(tvshow['original_name']),
            '$y': str(dateutil.parser.parse(tvshow['first_air_date']).year),
            '$et': helpers.filter_fs_chars(episode['name']),
            '$sn': str(episode['season_number']).zfill(2),
            '$en': str(episode['episode_number']).zfill(2),
            '$ext': videofile_extension
        }

        dst = helpers.replace_by_rule(replacers, config['episode']['episode'])
        if os.path.exists(dst) and config['general']['overwrite_videos']:
            return

        downloads = {
            config['tmdb']['base_url']
            + config['tmdb']['backdrop_size']
            + tvshow['backdrop_path']:
            helpers.replace_by_rule(replacers, config['tvshow']['backdrop']),

            config['tmdb']['base_url']
            + config['tmdb']['poster_size']
            + tvshow['poster_path']:
            helpers.replace_by_rule(replacers, config['tvshow']['poster']),

            config['tmdb']['base_url']
            + config['tmdb']['poster_size']
            + season['poster_path']:
            helpers.replace_by_rule(replacers,
                                    config['tvshow']['season_poster']),

            config['tmdb']['base_url']
            + config['tmdb']['still_size']
            + episode['still_path']:
            helpers.replace_by_rule(replacers, config['episode']['still']),
        }

        # write series nfo
        nfo.write_series_nfo(
            tvshow,
            config['general']['language'],
            helpers.replace_by_rule(replacers, config['tvshow']['nfo']),
            simulate=config['debug']['simulate_nfo'],
            overwrite=config['general']['overwrite_nfos'])

        # write episode nfo
        nfo.write_episode_nfo(
            tvshow,
            episode,
            helpers.replace_by_rule(replacers, config['episode']['nfo']),
            releasegroup=guess['releasegroup'],
            source=guess['source'],
            simulate=config['debug']['simulate_nfo'],
            overwrite=config['general']['overwrite_nfos'])

    else:
        return

    # move file
    fs.move(videofile_abspath,
            dst,
            config['debug']['simulate_move'],
            config['general']['overwrite_videos'])

    # download images
    for download in downloads:
        helpers.download(src=download,
                         dst=downloads[download],
                         simulate=config['debug']['simulate_images'],
                         overwrite=config['general']['overwrite_images'])
