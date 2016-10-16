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

import urllib
import logger

def replace_by_rule(rules, string):
    for rule in rules:
        string = string.replace(rule, rules[i])
    return string

def download(src, dst, simulate):
    logmsg="Downloading \"{0}\" to \"{1}\"".format(src, dst)
    if not simulate:
        logger.info(logmsg)
        create_path(os.path.dirname(dst))
        urllib.urlretrieve(src, dst)
    else:
        logger.info("SIMULATE: {0}".format(logmsg))

def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_movie_name(movie, name):
    newname = name
    date = dateutil.parser.parse(movie['release_date'])
    replacement_rules = {
            '%t':movie['title'],
            '%ot':movie['original_title'],
            '%y':str(date.year)
    }
    for i in replacement_rules:
        newname = newname.replace(i, replacement_rules[i])
    return newname
