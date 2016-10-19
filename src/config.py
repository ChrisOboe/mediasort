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
import configparser

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
    config = configparser.ConfigParser()
    config.read(path)

    setting = {
        'general':{
            'language':config.get('general','language', fallback='EN-US').upper(),
            'cache_path':config.get('general','cache_path', fallback='~/.cache/autosort/'),
            'tmdb_config_cache_days':int(config.get('general','tmdb_config_cache_days', fallback='7')),
            'simulate_move':config.getboolean('general','simulate_move', fallback=False),
            'simulate_download':config.getboolean('general','simulate_download', fallback=False),
            'simulate_nfo':config.getboolean('general','simulate_nfo', fallback=False),
            'tmdb_api_key':config.get('general','tmdb_api_key', fallback='bd65f46c799046c2d4286966d76c37c6'),
            'allowed_extensions':config.get('general','allowed_extensions', fallback='mkv avi').split(),
            'minimal_file_size':int(config.get('general', 'minimal_file_size', fallback='100'))*1048576
            },
        'movie':{
            'video_destination':config.get('movie','video_destination', fallback='/var/lib/media/movies/$t ($y)/$t ($y).$ext'),
            'nfo_destination':config.get('movie','nfo_destination', fallback='/var/lib/media/movies/$t ($y)/$t ($y).nfo'),
            'backdrop_destination':config.get('movie','backdrop_destination', fallback='/var/lib/media/movies/$t ($y)/fanart.jpg'),
            'poster_destination':config.get('movie','poster_destination', fallback='/var/lib/media/movies/$t ($y)/poster.jpg'),
            'poster_size':config.get('movie','poster_size', fallback='w500'),
            'backdrop_size':config.get('movie','backdrop_size', fallback='w1280')
            },
        'episode':{
            'video_destination':config.get('episode','video_destination', fallback='/var/lib/media/series/$t ($y)/Season $sn/E$enS$sn $et.$ext'),
            'nfo_destination':config.get('episode','nfo_destination', fallback='/var/lib/media/series/$t ($y)/$t ($y).nfo'),
            'backdrop_destination':config.get('episode','backdrop_destination', fallback='/var/lib/media/series/%n ($y)/fanart.jpg'),
            'poster_destination':config.get('episode','poster_destination', fallback='/var/lib/media/series/%n ($y)/poster.jpg'),
            'poster_size':config.get('episode','poster_size', fallback='w500'),
            'backdrop_size':config.get('episode','backdrop_size', fallback='w1280')
            }
    }

    return setting

