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
import logging
import dateutil

from .guess import guess_vid
from . import helpers
from . import nfo
from . import tmdb
from . import fanarttv
from .enums import MediaType
from . import config

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


def get_image_url(ids, image_type, media_type, languages, providers,
                  episode=0, season=0):
    """ returns a specific image for a specific media """

    url = None
    for provider in providers:
        if provider is None:
            continue
        if media_type == MediaType.movie:
            if provider not in MOVIE_IMAGE_PROVIDERS:
                logging.warning("%s doesn't support movie images", provider)
                continue
            url = MOVIE_IMAGE_PROVIDERS[provider](ids,
                                                  image_type,
                                                  languages)
        elif media_type == MediaType.tvshow:
            if provider not in TVSHOW_IMAGE_PROVIDERS:
                logging.warning("%s doesn't support tvshow images", provider)
                continue
            url = TVSHOW_IMAGE_PROVIDERS[provider](ids,
                                                   image_type,
                                                   languages)
        elif media_type == MediaType.season:
            if provider not in SEASON_IMAGE_PROVIDERS:
                logging.warning("%s doesn't support season images", provider)
                continue
            url = SEASON_IMAGE_PROVIDERS[provider](ids,
                                                   season,
                                                   image_type,
                                                   languages)
        elif media_type == MediaType.episode:
            if provider not in EPISODE_IMAGE_PROVIDERS:
                logging.warning("%s doesn't support episode images", provider)
                continue
            url = EPISODE_IMAGE_PROVIDERS[provider](ids,
                                                    season,
                                                    episode,
                                                    image_type,
                                                    languages)
        if url is not None:
            return url

    print("  Sorry we didn't found a {0} for this media file".format(image_type))


def sort(videofile, settings):
    """ sorts a videofile """
    videofile_basename = os.path.basename(videofile)
    videofile_abspath = os.path.abspath(videofile)
    videofile_extension = os.path.splitext(videofile_basename)[1].lower()[1:]
    nfofile = os.path.splitext(videofile_abspath)[0]+".nfo"

    dst = None
    downloads = []

    print("\nProcessing \"{0}\"".format(videofile_abspath))

    try:
        guess = guess_vid(videofile_abspath, nfofile)
    except LookupError as err:
        print(err)
        print("Skipping this file")
        return

    if guess['type'] == MediaType.movie:
        # Get movie info from tmdb
        movie = tmdb.get_movie_info(guess["ids"],
                                    settings['general']['languages'])

        # set replacement rules
        replacers = {
            '$t': helpers.filter_fs_chars(movie['title']),
            '$ot': helpers.filter_fs_chars(movie['original_title']),
            '$y': str(dateutil.parser.parse(movie['release_date']).year),
        }

        # check if movie destination already exists
        dst = helpers.replace_by_rule(replacers,
                                      settings['movie']['base_path']
                                      + settings['movie']['movie_path'])
        if os.path.exists(dst) and settings['general']['overwrite_videos']:
            return

        # set image downloads
        downloads = [
            {"mediatype": MediaType.movie,
             "ids":   guess['ids'],
             "images": [
                 {"imagetype":   "poster",
                  "providers":   settings['movie']['poster_providers'],
                  "destination": settings['movie']['poster_path']},
                 {"imagetype":   "background",
                  "providers":   settings['movie']['background_providers'],
                  "destination": settings['movie']['background_path']},
                 {"imagetype":   "disc",
                  "providers":   settings['movie']['disc_providers'],
                  "destination": settings['movie']['disc_path']},
                 {"imagetype":   "banner",
                  "providers":   settings['movie']['banner_providers'],
                  "destination": settings['movie']['banner_path']},
                 {"imagetype":   "logo",
                  "providers":   settings['movie']['logo_providers'],
                  "destination": settings['movie']['logo_path']},
                 {"imagetype":   "clearart",
                  "providers":   settings['movie']['clearart_providers'],
                  "destination": settings['movie']['clearart_path']},
                 {"imagetype":   "art",
                  "providers":   settings['movie']['art_providers'],
                  "destination": settings['movie']['art_path']}]}
        ]

        # write nfo
        nfo.write_movie_nfo(
            movie=movie,
            dst=helpers.replace_by_rule(replacers, settings['movie']['nfo_path']),
            rating_country=settings['general']['languages'][0],
            releasegroup=guess['releasegroup'],
            source=guess['source'],
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos']
        )

    elif guess['type'] == MediaType.episode:
        tvshow = tmdb.get_tvshow_info(
            guess["ids"],
            settings['general']['languages'])

        episode = tmdb.get_episode_info(guess['ids'],
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

        dst = (settings['tvshow']['base_path']
               + helpers.replace_by_rule(replacers,
                                         settings['episode']['episode_path']))
        if os.path.exists(dst) and settings['general']['overwrite_videos']:
            return

        downloads = [
            {"mediatype": MediaType.tvshow,
             "ids":   guess['ids'],
             "images": [
                 {"imagetype":   "poster",
                  "providers":   settings['tvshow']['poster_providers'],
                  "destination": settings['tvshow']['poster_path']},
                 {"imagetype":   "background",
                  "providers":   settings['tvshow']['background_providers'],
                  "destination": settings['tvshow']['background_path']},
                 {"imagetype":   "banner",
                  "providers":   settings['tvshow']['banner_providers'],
                  "destination": settings['tvshow']['banner_path']},
                 {"imagetype":   "logo",
                  "providers":   settings['tvshow']['logo_providers'],
                  "destination": settings['tvshow']['logo_path']},
                 {"imagetype":   "clearart",
                  "providers":   settings['tvshow']['clearart_providers'],
                  "destination": settings['tvshow']['clearart_path']},
                 {"imagetype":   "charart",
                  "providers":   settings['tvshow']['charart_providers'],
                  "destination": settings['tvshow']['charart_path']},
                 {"imagetype":   "art",
                  "providers":   settings['movie']['art_providers'],
                  "destination": settings['movie']['art_path']}]},
            {"mediatype": MediaType.season,
             "ids":       guess['ids'],
             "season":    episode['season_number'],
             "images": [
                 {"imagetype":   "poster",
                  "providers":   settings['season']['poster_providers'],
                  "destination": settings['season']['poster_path']}]},
            {"mediatype": MediaType.episode,
             "ids":       guess['ids'],
             "season":    episode['season_number'],
             "episode":   episode['episode_number'],
             "images": [
                 {"imagetype":   "thumbnail",
                  "providers":   settings['episode']['thumbnail_providers'],
                  "destination": settings['episode']['thumbnail_path']}]},
        ]

        # write series nfo
        nfo.write_tvshow_nfo(
            tvshow,
            settings['general']['languages'][0],
            helpers.replace_by_rule(replacers,
                                    settings['tvshow']['base_path']
                                    + settings['tvshow']['nfo_path']),
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos'])

        # write episode nfo
        nfo.write_episode_nfo(
            tvshow,
            episode,
            helpers.replace_by_rule(replacers,
                                    settings['tvshow']['base_path']
                                    + settings['episode']['nfo_path']),
            releasegroup=guess['releasegroup'],
            source=guess['source'],
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos'])

    else:
        return

    # download images
    for download in downloads:
        for image in download['images']:
            # check if special provider "None" is used
            if image["providers"][0] == "None":
                continue

            if download['mediatype'] == MediaType.movie:
                base_path = settings['movie']['base_path']
            else:
                base_path = settings['tvshow']['base_path']

            url = get_image_url(
                ids=download['ids'],
                image_type=image['imagetype'],
                media_type=download['mediatype'],
                languages=settings['general']['languages'],
                providers=image['providers'],
                season=None if 'season' not in download else download['season'],
                episode=None if 'episode' not in download else download['episode']
            )

            if url is not None:
                helpers.download(
                    src=url,
                    dst=helpers.replace_by_rule(
                        replacers,
                        base_path + image['destination']),
                    simulate=settings['debug']['simulate_images'],
                    overwrite=settings['general']['overwrite_images'])

    # move file
    helpers.move(videofile_abspath,
                 dst,
                 settings['debug']['simulate_move'],
                 settings['general']['overwrite_videos'])
