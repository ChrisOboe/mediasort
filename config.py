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

import argparse
import ConfigParser

# parse arguments via argparse
def parse_arguments():
    parser = argparse.ArgumentParser(
            description='Scrapes metadata for movies and episodes from TMDb '
            'by guessing the title from scene standard naming conventions. '
            'This product uses the TMDb API but is not endorsed or certified by TMDb.')
    parser.add_argument("source",
            help="either a file that should be sorted, or a folder "
            "where every found media files are recursively sorted")
    parser.add_argument('-c','--config', required=True,
            help="the config file")

    return parser.parse_args()

# parses the configfile
def parse_configfile(path):
    config = ConfigParser.RawConfigParser()
    config.read(path)

    # default config parser doesn't support defaults
    def config_get(section, option, default):
        if config.has_option(section, option):
            return config.get(section, option)
        else:
            return default

    setting = {
        'general':{
            'language':config_get('general','language', 'en-US'),
            'tmdb_config_cache':config_get('general','tmdb_config_cache','~/.cache/autosort'),
            'tmdb_config_cache_days':config_get('general','tmdb_config_cache_days', '7'),
            'simulate_move':config_get('general','simulate_move', 'yes'),
            'simulate_download':config_get('general','simulate_download', 'yes'),
            'simulate_nfo':config_get('general','simulate_nfo', 'yes'),
            'tmdb_api_key':config_get('general','tmdb_api_key', 'bd65f46c799046c2d4286966d76c37c6'),
            'allowed_extensions':config_get('general','allowed_extensions', 'mkv avi'),
            'minimal_file_size':config_get('general', 'minimal_file_size', '100')
            },
        'movie':{
            'video_destination':config_get('movie','video_destination', '/var/lib/media/movies/%t (%y)/%t (%y)'),
            'nfo_destination':config_get('movie','nfo_destination', '/var/lib/media/movies/%t (%y)/%t (%y).nfo'),
            'backdrop_destination':config_get('movie','backdrop_destination', '/var/lib/media/movies/%t (%y)/fanart.jpg'),
            'poster_destination':config_get('movie','poster_destination', '/var/lib/media/movies/%t (%y)/poster.jpg'),
            'poster_size':config_get('movie','poster_size', 'w500'),
            'backdrop_size':config_get('movie','backdrop_size', 'w1280')
            },
        'episode':{
            'video_destination':config_get('episode','video_destination', '/var/lib/media/movies/%t (%y)/%t (%y)'),
            'nfo_destination':config_get('episode','nfo_destination', '/var/lib/media/movies/%t (%y)/%t (%y).nfo'),
            'backdrop_destination':config_get('episode','backdrop_destination', '/var/lib/media/series/%n (%y)/fanart.jpg'),
            'poster_destination':config_get('episode','poster_destination', '/var/lib/media/series/%n (%y)/poster.jpg'),
            'poster_size':config_get('episode','poster_size', 'w500'),
            'backdrop_size':config_get('episode','backdrop_size', 'w1280')
            }
    }

    return setting

