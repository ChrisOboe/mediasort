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

""" the executable for mediasort """

import sys
import logging
import mediasort


def verbose():
    """ logs info to stdout """
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.handlers = []
    logout = logging.StreamHandler(sys.stdout)
    logout.setLevel(logging.INFO)
    log.addHandler(logout)


# load config
ARGS = mediasort.config.parse_arguments()
CONFIG = mediasort.config.parse_configfile(ARGS['config'])

mediasort.tmdb.init(CONFIG['tmdb'])
mediasort.fanart.init(CONFIG['fanarttv'])

# init stuff
logging.getLogger("requests").setLevel(logging.WARNING)
if ARGS['verbose']:
    verbose()

# get list of files
VIDEOFILES = mediasort.fs.find(ARGS['source'],
                               CONFIG['videofiles']['allowed_extensions'],
                               CONFIG['videofiles']['minimal_file_size'])

for videofile in VIDEOFILES:
    mediasort.sort(videofile, CONFIG, ARGS['force_type'])
