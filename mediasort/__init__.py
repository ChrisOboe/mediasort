# Copyright (C) 2016-2017  Oboe, Chris <chrisoboe@eml.cc>
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

from . import nfo_reader
from . import filename
from . import helpers
from . import nfo
from . import tmdb
from . import fanarttv
from . import *

PROVIDERS = {
    'guess': {
        'nfo': nfo_reader.get_guess,
        'filename': filename.get_guess,
    },
    'identificator': {
        MediaType.movie: {
            'nfo': nfo_reader.get_identificator,
            'tmdb': tmdb.get_identificator,
        },
        MediaType.episode: {
            'nfo': nfo_reader.get_identificator,
            'tmdb': tmdb.get_identificator,
        },
    },
    'metadata': {
        MediaType.movie: {
            MetadataType.title: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.originaltitle: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.set: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.premiered: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.tagline: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.plot: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.certification: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.rating: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.votes: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.studios: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.countries: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.genres: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.writers: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.directors: {
                'tmdb': tmdb.get_movie_metadata,
            },
            MetadataType.actors: {
                'tmdb': tmdb.get_movie_metadata,
            },
        },
        MediaType.tvshow: {
            MetadataType.title: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
            MetadataType.premiered: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
            MetadataType.plot: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
            MetadataType.certification: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
            MetadataType.rating: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
            MetadataType.votes: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
            MetadataType.studios: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
            MetadataType.genres: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
            MetadataType.actors: {
                'tmdb': tmdb.get_tvshow_metadata,
            },
        },
        MediaType.episode: {
            MetadataType.title: {
                'tmdb': tmdb.get_episode_metadata,
            },
            MetadataType.premiered: {
                'tmdb': tmdb.get_episode_metadata,
            },
            MetadataType.plot: {
                'tmdb': tmdb.get_episode_metadata,
            },
            MetadataType.rating: {
                'tmdb': tmdb.get_episode_metadata,
            },
            MetadataType.votes: {
                'tmdb': tmdb.get_episode_metadata,
            },
        },
    },
    'image': {
        MediaType.movie: {
            ImageType.poster: {
                'tmdb': tmdb.get_movie_image,
                'fanarttv': fanarttv.get_movie_image,
            },
            ImageType.background: {
                'tmdb': tmdb.get_movie_image,
                'fanarttv': fanarttv.get_movie_image,
            },
            ImageType.disc: {
                'fanarttv': fanarttv.get_movie_image,
            },
            ImageType.banner: {
                'fanarttv': fanarttv.get_movie_image,
            },
            ImageType.logo: {
                'fanarttv': fanarttv.get_movie_image,
            },
            ImageType.clearart: {
                'fanarttv': fanarttv.get_movie_image,
            },
            ImageType.art: {
                'fanarttv': fanarttv.get_movie_image,
            },
        },
        MediaType.tvshow: {
            ImageType.poster: {
                'tmdb': tmdb.get_tvshow_image,
                'fanarttv': fanarttv.get_tvshow_image,
            },
            ImageType.background: {
                'tmdb': tmdb.get_tvshow_image,
                'fanarttv': fanarttv.get_tvshow_image,
            },
            ImageType.banner: {
                'fanarttv': fanarttv.get_tvshow_image,
            },
            ImageType.logo: {
                'fanarttv': fanarttv.get_tvshow_image,
            },
            ImageType.clearart: {
                'fanarttv': fanarttv.get_tvshow_image,
            },
            ImageType.charart: {
                'fanarttv': fanarttv.get_tvshow_image,
            },
            ImageType.art: {
                'fanarttv': fanarttv.get_tvshow_image,
            },
        },
        MediaType.season: {
            ImageType.poster: {
                'tmdb': tmdb.get_season_image,
            },
        },
        MediaType.episode: {
            ImageType.thumbnail: {
                'tmdb': tmdb.get_episode_image,
            }
        },
    },
}


def check_providers(config):
    """ checks if there is a misconfigured provider """
    for providertype in config['providers']:
        if providertype == 'guess':
            for provider in config['providers'][providertype]:
                if provider not in PROVIDERS[providertype]:
                    raise ConfigError(
                        "{0} is not a valid {1} provider".format(
                            provider,
                            providertype))
        if providertype == 'identificator':
            for mediatype in config['providers']['identificator']:
                for provider in config['providers']['identificator'][mediatype]:


        
        
        if (providertype == 'guess'
                or providertype == 'identificator'
                or providertype == 'metadata'):
            for provider in config['providers'][providertype]:
                if provider not in PROVIDERS[providertype]:
                    raise ConfigError(
                        "{0} is not a valid {1} provider".format(
                            provider,
                            providertype))
        elif providertype == 'image':


def get_guess(filepath, config):
    """ returns a guess for a filename """

    guess = {
        'filepath': None,
        'type': None,
        'title': None,
        'year': None,
        'releasegroup': None,
        'source': None,
        'season': None,
        'episode': None,
    }

    for provider in config['providers']['guess']:
        if provider not in PROVIDERS['guess']:
            logging.warning("%s isn't a allowed guess provider", provider)
            continue
        helpers.merge_dict(guess,
                           GUESS_PROVIDERS[provider](filepath,
                                                     config[provider]))

    needed = ['filepath', 'title', 'type']
    if not helpers.contains_elements(needed, guess):
        raise NotEnoughData("Needed value couldn't be guessed")

    if guess['type'] == MediaType.episode:
        needed = ['season', 'episode']
        if not helpers.contains_elements(needed, guess):
            raise NotEnoughData("Needed value couldn't be guessed")

    return guess


def get_identificator(guess, config):
    """ returns a identificator for a guess """

    providers = PROVIDERS['identificator'][guess['type']]

    if guess['type'] == MediaType.movie:
        identificator = {
            'type': MediaType.movie,
            'tmdb': None,
            'imdb': None,
        }
    elif guess['type'] == MediaType.episode:
        identificator = {
            'type': MediaType.episode,
            'tmdb': None,
            'imdb': None,
            'tvdb': None,
            'season': guess['season'],
            'episode': guess['episode'],
        }

    for provider in config['providers']['identificator'][guess['type']]:
        helpers.merge_dict(identificator,
                           providers[provider](guess,
                                               identificator,
                                               config[provider]))

    if guess['type'] == MediaType.movie:
        needed = ['tmdb', 'imdb']
    elif guess['type'] == MediaType.episode:
        needed = ['tmdb', 'imdb', 'tvdb', 'season', 'episode']
    if not helpers.contains_elements(needed, identificator):
        raise NotEnoughData("Needed idendificator couldn't be found")

    return identificator


def get_metadata(identificator, config):
    """ returns the metadata """

    if identificator['type'] == MediaType.movie:
        metadata = {
            MetadataType.title: None,
            MetadataType.originaltitle: None,
            MetadataType.premiered: None,
            MetadataType.tagline: None,
            MetadataType.plot: None,
            MetadataType.set: None,
            MetadataType.certification: None,
            MetadataType.rating: None,
            MetadataType.votes: None,
            MetadataType.studios: [],
            MetadataType.countries: [],
            MetadataType.genres: [],
            MetadataType.directors: [],
            MetadataType.scriptwriters: [],
            MetadataType.actors: [],
        }
    elif identificator['type'] == MediaType.episode:
        metadata = {
            MetadataType.title: None,
            MetadataType.showtitle: None,
            MetadataType.plot: None,
            MetadataType.premiered: None,
            MetadataType.rating: None,
            MetadataType.votes: None,
        }
    elif identificator['type'] == MediaType.tvshow:
        metadata = {
            MetadataType.title: None,
            MetadataType.premiered: None,
            MetadataType.plot: None,
            MetadataType.certification: None,
            MetadataType.rating: None,
            MetadataType.votes: None,
            MetadataType.studios: [],
            MetadataType.genres: [],
            MetadataType.actors: [],
        }

    for language in config['languages']['metadata']:
        for metadatatype in metadata:
            for provider in config['providers']['metadata'][identificator['type']][metadatatype]:
                helpers.merge_entry(metadata[metadatatype], PROVIDERS['metadata'][identificator['type']][provider](
                    identificator,
                    metadatatype,
                    language,
                    config[provider]))

    return metadata


def get_images(identificator, config):
    """ returns a specific image url """

    if identificator['type'] == MediaType.movie:
        images = {
            ImageType.poster: None,
            ImageType.background: None,
            ImageType.disc: None,
            ImageType.banner: None,
            ImageType.logo: None,
            ImageType.clearart: None,
            ImageType.art: None,
        }
    elif identificator['type'] == MediaType.episode:
        images = {
            ImageType.thumbnail: None,
        }
    elif identificator['type'] == MediaType.tvshow:
        images = {
            ImageType.poster: None,
            ImageType.background: None,
            ImageType.banner: None,
            ImageType.logo: None,
            ImageType.clearart: None,
            ImageType.charart: None,
            ImageType.art: None,
        }
    elif identificator['type'] == MediaType.season:
        images = {
            ImageType.poster: None,
        }

    url = None
    for imagetype in images:
        for language in config['languages']['images']:
            for provider in config['providers'][imagetype]:
                if provider is None:
                    continue
                images[imagetype] = PROVIDERS['image_' + identificator['type']][provider](
                    identificator,
                    imagetype,
                    language)

    return images


def sort(videofile, config):
    """ sorts a videofile """
    videofile_basename = os.path.basename(videofile)
    videofile_abspath = os.path.abspath(videofile)
    videofile_extension = os.path.splitext(videofile_basename)[1].lower()[1:]

    print("\nProcessing \"{0}\"".format(videofile_abspath))

    try:
        guess = get_guess(videofile_abspath, config)
        identificator = get_identificator(guess, config)
        if identificator['type'] == MediaType.episode:
            tvshow_identificator = identificator.copy()
            tvshow_identificator['type'] = MediaType.tvshow
            tvshow_identificator['episode'] = None
            tvshow_identificator['season'] = None
            season_identificator = identificator.copy()
            season_identificator['type'] = MediaType.season
            season_identificator['episode'] = None
            tvshow_metadata = get_metadata(tvshow_identificator, config)
            tvshow_images = get_images(tvshow_identificator, config)
            season_images = get_images(season_identificator, config)
        metadata = get_metadata(identificator, config)
        images = get_images(identificator, config)
    except NotEnoughData as err:
        print(err)
        print("Skipping this file")
        return

    # set replacement rules
    if identificator['type'] == MediaType.movie:
        replacers = {
            '$t': helpers.filter_fs_chars(metadata['title']),
            '$ot': helpers.filter_fs_chars(metadata['originaltitle']),
            '$y': str(dateutil.parser.parse(metadata['premiered']).year),
        }
    elif identificator['type'] == MediaType.episode:
        replacers = {
            '$tt': helpers.filter_fs_chars(tvshow_metadata['title']),
            '$y': str(dateutil.parser.parse(tvshow_metadata['premiered']).year),
            '$et': helpers.filter_fs_chars(metadata['title']),
            '$sn': str(identificator['season']).zfill(2),
            '$en': str(identificator['episode']).zfill(2),
        }

    # check if movie destination already exists
    video_dst = helpers.replace_by_rule(
        replacers,
        config['paths'][identificator['type']]['base_path']
        + config['paths'][identificator['type']]['videofile'])

    if os.path.exists(video_dst) and config['general']['overwrite_videos']:
        print("Videofile already exists")
        print("Skipping this file")
        return

    # download images
    def download_images(identificator, images):
        for image in images:
            image_dst = helpers.replace_by_rule(
                replacers,
                config['paths'][identificator['type']][image])
            if (not os.paths.exists(image_dst)
               or config['general']['overwrite_images']):
                helpers.download(images[image], image_dst)

    download_images(identificator, images)
    if identificator['type'] == MediaType.episode:
        download_images(tvshow_identificator, tvshow_images)
        download_images(season_identificator, season_images)

    # write nfo
        nfo.write_movie_nfo(
            movie=movie,
            dst=helpers.replace_by_rule(replacers,
                                        settings['movie']['base_path']
                                        + settings['movie']['nfo_path']),
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

        dst = (helpers.replace_by_rule(replacers,
                                       settings['tvshow']['base_path']
                                       + settings['episode']['episode_path']))
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
            overwrite=settings['general']['overwrite_nfos']
        )

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
        },
        'tvshow': {
            'tmdb': tmdb.get_tvshow_image,
            'fanarttv': fanarttv.get_tvshow_image,
        },
        'season': {
            'tmdb': tmdb.get_season_image,
        },
        'episode': {
            'tmdb': tmdb.get_episode_image,
        },
    },
}
