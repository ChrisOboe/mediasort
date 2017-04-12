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

from urllib.request import urlopen
from urllib.parse import urlsplit

# Remebers if file is already written
DOWNLOADED = []


def download(url, destination):
    """ download the file if not downloaded before """
    if destination not in DOWNLOADED:
        with urlopen(url, timeout=30.0) as remote:
            # get filename
            filename = None
            if 'Content-Disposition' in remote.info():
                filename = remote.info()['Content-Disposition']
            else:
                filename = urlsplit(url)[2]

            # extract extension from filename
            extension = filename.split('.')[-1]

            # download the file
            with open("{0}.{1}".format(destination, extension), 'wb') as local:
                local.write(remote.read())

            # remember it
            DOWNLOADED.append(destination)
