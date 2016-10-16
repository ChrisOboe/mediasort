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
import shutil
import logging

def move(src, dst):
    logmsg="Moving \"{0}\" to \"{1}\"".format(src, dst)

    if config['general']['simulate_move'] == 'yes':
        logging.info("SIMULATE: {0}".format(logmsg))
    else
        logging.info(logmsg)
        shutil.move(src, dst)

def find_video_files(path, extensions, filesize):
    if not os.path.exists(path):
        return

    video_files = []
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in extensions: video_files.append(path)
    else:
        for root, dirs, files in os.walk(path):
            for filename in files:
                filepath = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()
                if ext in video_extensions: video_files.append(filepath)

    return video_files
