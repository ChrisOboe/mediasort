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

""" helper functinos for mediasort """

from urllib.request import urlretrieve
import logging
import os

DOWNLOADED = []


def merge_dict(base_dict, overwrite_dict):
    """ merges two dicts """
    for key in overwrite_dict:
        if key not in base_dict:
            base_dict[key] = overwrite_dict[key]
        else:
            if isinstance(overwrite_dict[key], str) and \
               base_dict[key] == '':
                base_dict[key] = overwrite_dict[key]
            elif isinstance(overwrite_dict[key], dict):
                merge_dict(base_dict[key], overwrite_dict[key])


def replace_by_rule(rules, string):
    """ replaces multiple stuff from a dict """
    for rule in rules:
        string = string.replace(rule, rules[rule])
    return string


def download(src, dst, simulate=False, overwrite=False):
    """ Downloads something """
    if dst in DOWNLOADED:
        return
    if not overwrite and os.path.exists(dst):
        return

    logging.info("  Downloading\n    from: {0}\n    to:   {1}"
                 .format(src, dst))
    DOWNLOADED.append(dst)
    if not simulate:
        create_path(dst)
        urlretrieve(src, dst)


def create_path(path):
    """ Creats a path if it not exists """
    dirname = os.path.dirname(path)
    logging.info("  Creating path {0}".format(dirname))
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def filter_fs_chars(string):
    """ Replaces problematic chars from a string with a underline """
    forbidden_chars = ['/', '\\', '<', '>', ':', '"', '|', '?', '*']
    for char in forbidden_chars:
        string = string.replace(char, "_")
    return string
