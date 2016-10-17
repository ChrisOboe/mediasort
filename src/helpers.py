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
import logging
import os

def replace_by_rule(rules, string):
    for rule in rules:
        string = string.replace(rule, rules[rule])
    return string

def download(src, dst, simulate):
    logmsg="Downloading \"{0}\" to \"{1}\"".format(src, dst)
    if not simulate:
        logging.info(logmsg)
        create_path(dst)
        urllib.urlretrieve(src, dst)
    else:
        logging.info("SIMULATE: {0}".format(logmsg))

def create_path(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
