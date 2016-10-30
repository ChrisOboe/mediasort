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

"""Reads configuration via arguments and configfile"""

import argparse
import configparser
from xdg.BaseDirectory import xdg_config_home, xdg_cache_home


def parse_arguments():
    """Returns a dict of command line arguments."""

    parser = argparse.ArgumentParser(
        description='Scrapes metadata for movies and episodes from TMDb '
        'by guessing the title from scene standard naming conventions.\n'
        'This product uses the TMDb API but is not endorsed or certified '
        'by TMDb.')
    parser.add_argument(
        "source",
        help="The file or the folder which should be scanned for files ")
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        default=False,
        help="Displays more stuff to stdout")
    parser.add_argument(
        '-c',
        '--config',
        default="{0}/mediasort/config.ini".format(xdg_config_home),
        help="the config file")
    parser.add_argument(
        '-t',
        '--force-type',
        help="force either a episode or a movie")

    return vars(parser.parse_args())


def parse_configfile(path):
    """Returns a dict of settings."""

    base_path = '/var/lib/media'

    settings = {
        'debug': {
            'simulate_move': False,
            'simulate_images': False,
            'simulate_nfo': False
            },
        'general': {
            'language': 'EN-US',
            'cache_path': xdg_cache_home+"/mediasort/",
            'overwrite_nfos': True,
            'overwrite_images': True,
            'overwrite_videos': False
            },
        'videofiles': {
            'allowed_extensions': 'mkv avi'.split(),
            'minimal_file_size': 100,
            },
        'tmdb': {
            'config_cache_days': 7,
            'api_key': 'bd65f46c799046c2d4286966d76c37c6',
            'https_download': False,
            'poster_size': 'w500',
            'backdrop_size': 'w1280',
            'still_size': 'w300'
            },
        'movie': {
            'movie':    base_path + '/movies/$t ($y)/$t ($y).$ext',
            'nfo':      base_path + '/movies/$t ($y)/$t ($y).nfo',
            'backdrop': base_path + '/movies/$t ($y)/fanart.jpg',
            'poster':   base_path + '/movies/$t ($y)/poster.jpg',
            },
        'movie_set': {
            'movie':    base_path + '/movies/$s/$t ($y)/$t ($y).$ext',
            'nfo':      base_path + '/movies/$s/$t ($y)/$t ($y).nfo',
            'backdrop': base_path + '/movies/$s/$t ($y)/fanart.jpg',
            'poster':   base_path + '/movies/$s/$t ($y)/poster.jpg',
            },
        'tvshow': {
            'nfo':      base_path + '/tvshows/$st ($y)/tvshow.nfo',
            'poster':   base_path + '/tvshows/$st ($y)/poster.jpg',
            'backdrop': base_path + '/tvshows/$st ($y)/fanart.jpg',
            'season_poster':   (base_path + '/tvshows/$st ($y)'
                                + '/season$sn-poster.jpg'),
            },
        'episode': {
            'episode': (base_path + '/tvshows/$st ($y)/Season $sn'
                        + '/S$snE$en $et.$ext'),
            'nfo':     (base_path + '/tvshows/$st ($y)/Season $sn'
                        + '/S$snE$en $et.nfo'),
            'still':   (base_path + '/tvshows/$st ($y)/Season $sn'
                        + '/S$snE$en $et-thumb.jpg'),
            }
    }

    config = configparser.ConfigParser()
    config.read(path)
    for category in settings:
        for entry in settings[category]:
            if isinstance(settings[category][entry], bool):
                settings[category][entry] = config.getboolean(
                    category,
                    entry,
                    fallback=settings[category][entry])
            elif isinstance(settings[category][entry], int):
                settings[category][entry] = config.getint(
                    category,
                    entry,
                    fallback=settings[category][entry])
            elif isinstance(settings[category][entry], list):
                settings[category][entry] = config.get(
                    category,
                    entry,
                    fallback=' '.join(settings[category][entry])).split()
            else:
                settings[category][entry] = config.get(
                    category,
                    entry,
                    fallback=settings[category][entry])

    return settings


def validate(settings, tmdb):
    """ Checks if settings is a valid """
    checks = {"poster_size": "poster_sizes",
              "backdrop_size": "backdrop_sizes",
              "still_size": "still_sizes"}

    for check in checks:
        if settings['tmdb'][check] not in tmdb[checks[check]]:
            errortext = ("{0} is not a valid {1}.\nValid {2} are {3}"
                         .format(settings['tmdb'][check],
                                 check,
                                 checks[check],
                                 tmdb[checks[check]]))
            raise AttributeError(errortext)
