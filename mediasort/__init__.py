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

""" sorts a videofile """

import os
from enum import Enum
import dateutil

from .guess import guess_vid
from . import helpers
from . import fs
from . import nfo
from . import tmdb
from . import fanarttv
from . import config


class MediaType(Enum):
    """ enum for mediatypes """
    movie = 1
    tvshow = 2
    season = 3
    episode = 4
    artist = 5
    album = 6


MOVIE_IMAGE_PROVIDERS = {
    'tmdb': tmdb.get_movie_image_url,
    'fanarttv': fanarttv.get_movie_image_url,
    }
TVSHOW_IMAGE_PROVIDERS = {
    'tmdb': tmdb.get_tvshow_image_url,
    'fanarttv': fanarttv.get_tvshow_image_url,
    }
SEASON_IMAGE_PROVIDERS = {
    'tmdb': tmdb.get_season_image_url,
    }
EPISODE_IMAGE_PROVIDERS = {
    'tmdb': tmdb.get_episode_image_url,
    }


def get_movie_image_url(tmdb_id, image_type, media_type, languages, providers):
    """ returns a specific image for a movie """
    for provider in providers:
        if media_type == MediaType.movie:
            url = MOVIE_IMAGE_PROVIDERS[provider](tmdb_id, image_type, languages)
        elif media_type == MediaType.tvshow:
            url = TVSHOW_IMAGE_PROVIDERS[provider](tmdb_id, image_type, languages)
        elif media_type == MediaType.season:
            url = SEASON_IMAGE_PROVIDERS[provider](tmdb_id, image_type, languages)
        elif media_type == MediaType.episode:
            url = EPISODE_IMAGE_PROVIDERS[provider](tmdb_id, image_type, languages)
        if url is not None:
            return url


def sort(videofile, settings, force=None):
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
                                    settings['general']['languages'])

        replacers = {
            '$t': helpers.filter_fs_chars(movie['title']),
            '$ot': helpers.filter_fs_chars(movie['original_title']),
            '$y': str(dateutil.parser.parse(movie['release_date']).year),
        }

        dst = helpers.replace_by_rule(replacers, settings['movie']['movie'])
        if os.path.exists(dst) and settings['general']['overwrite_videos']:
            return

        downloads = {
            get_movie_image_url(guess['tmdb_id'], 'backdrop'
            settings['tmdb']['base_url']
            + settings['tmdb']['backdrop_size']
            + movie['backdrop_path']:
            helpers.replace_by_rule(replacers, settings['movie']['backdrop']),

            settings['tmdb']['base_url']
            + settings['tmdb']['poster_size']
            + movie['poster_path']:
            helpers.replace_by_rule(replacers, settings['movie']['poster']),
        }

        # write nfo
        nfo.write_movie_nfo(
            movie=movie,
            dst=helpers.replace_by_rule(replacers, settings['movie']['nfo']),
            rating_country=settings['general']['languages'][0],
            releasegroup=guess['releasegroup'],
            source=guess['source'],
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos']
        )

    elif guess['type'] == 'episode':
        tvshow = tmdb.get_tvshow_info(
            guess["tmdb_id"],
            settings['general']['languages'])

        episode = tmdb.get_episode_info(guess['tmdb_id'],
                                        guess['season'],
                                        guess['episode'],
                                        settings['general']['languages'])

        replacers = {
            '$st': helpers.filter_fs_chars(tvshow['name']),
            '$sot': helpers.filter_fs_chars(tvshow['original_name']),
            '$y': str(dateutil.parser.parse(tvshow['first_air_date']).year),
            '$et': helpers.filter_fs_chars(episode['name']),
            '$sn': str(episode['season_number']).zfill(2),
            '$en': str(episode['episode_number']).zfill(2),
            '$ext': videofile_extension
        }

        dst = helpers.replace_by_rule(replacers, settings['episode']['episode'])
        if os.path.exists(dst) and settings['general']['overwrite_videos']:
            return

        downloads = {
            settings['tmdb']['base_url']
            + settings['tmdb']['backdrop_size']
            + tvshow['backdrop_path']:
            helpers.replace_by_rule(replacers, settings['tvshow']['backdrop']),

            settings['tmdb']['base_url']
            + settings['tmdb']['poster_size']
            + tvshow['poster_path']:
            helpers.replace_by_rule(replacers, settings['tvshow']['poster']),

            settings['tmdb']['base_url']
            + settings['tmdb']['poster_size']
            + season['poster_path']:
            helpers.replace_by_rule(replacers,
                                    settings['tvshow']['season_poster']),

            settings['tmdb']['base_url']
            + settings['tmdb']['still_size']
            + episode['still_path']:
            helpers.replace_by_rule(replacers, settings['episode']['still']),
        }

        # write series nfo
        nfo.write_series_nfo(
            tvshow,
            settings['general']['language'],
            helpers.replace_by_rule(replacers, settings['tvshow']['nfo']),
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos'])

        # write episode nfo
        nfo.write_episode_nfo(
            tvshow,
            episode,
            helpers.replace_by_rule(replacers, settings['episode']['nfo']),
            releasegroup=guess['releasegroup'],
            source=guess['source'],
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos'])

    else:
        return

    # move file
    fs.move(videofile_abspath,
            dst,
            settings['debug']['simulate_move'],
            settings['general']['overwrite_videos'])

    # download images
    for download in downloads:
        helpers.download(src=download,
                         dst=downloads[download],
                         simulate=settings['debug']['simulate_images'],
                         overwrite=settings['general']['overwrite_images'])
