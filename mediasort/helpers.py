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
from urllib.parse import urlparse
import logging
import os
import shutil

DOWNLOADED = []


def merge_dict(base_dict, overwrite_dict):
    """ appends missing informations to base_dict """
    for key in overwrite_dict:
        if key not in base_dict:
            base_dict[key] = overwrite_dict[key]
        else:
            if isinstance(overwrite_dict[key], str) and \
               base_dict[key] == '':
                base_dict[key] = overwrite_dict[key]
            elif isinstance(overwrite_dict[key], dict):
                merge_dict(base_dict[key], overwrite_dict[key])


def merge_entry(old_entry, new_entry):
    """ appends missing informations to old_entry """
    if isinstance(old_entry, dict):
        merge_dict(old_entry, new_entry)
    elif isinstance(old_entry, list):
        if not old_entry:
            old_entry = new_entry
    elif isinstance(old_entry, str):
        if old_entry == '':
            old_entry = new_entry
    elif old_entry is None:
        old_entry = new_entry


def get_key_fallback(base_dict, fallback_dict, key,
                     base_translation=None, fallback_translation=None):
    """ returns a key from multiple sources """
    if base_translation is not None and key in base_translation:
        base_key = base_translation[key]
    else:
        base_key = key

    if fallback_translation is not None and key in fallback_translation:
        fallback_key = fallback_translation[key]
    else:
        fallback_key = key

    if base_key in base_dict:
        return base_dict[base_key]
    elif fallback_key in fallback_dict:
        return fallback_dict[fallback_key]
    else:
        return None


def replace_by_rule(rules, string):
    """ replaces multiple stuff from a dict """
    for rule in rules:
        string = string.replace(rule, rules[rule])
    return string


def download(src, dst, append_ext=True):
    """ Downloads something """
    if append_ext:
        ext = os.path.splitext(urlparse(src).path)[1]
        dst += ext
    if dst in DOWNLOADED:
        return

    logging.info("Downloading \"{1}\" to \"{0}\"".format(src, dst))
    DOWNLOADED.append(dst)
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


def move(src, dst, simulate=False, overwrite=False, append_ext=True):
    """ moves a file from src to dst """
    if append_ext:
        ext = os.path.splitext(src)[1].lower()
        dst += ext

    if not overwrite and os.path.exists(dst):
        raise FileExistsError("{0} already exists.".format(dst))

    logging.info("  Moving\n    from: {0}\n    to:   {1}".format(src, dst))
    if not simulate:
        create_path(dst)
        shutil.move(src, dst)


def find(path, extensions, filesize):
    """ returns all files with given extensions
    and bigger than filesize in path """

    filesize *= 1048576  # use filesize as MB
    if not os.path.exists(path):
        return

    video_files = []
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()[1:]
        if ext in extensions and os.path.getsize(path) >= filesize:
            video_files.append(path)
    else:
        for root, dirs, files in os.walk(path):
            for filename in files:
                filepath = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()[1:]
                if (ext not in extensions) or \
                   (os.path.getsize(filepath) < filesize):
                    continue
                video_files.append(filepath)

    return video_files
