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

from mako.template import Template

INVALID_CHARS = "?<>:*|\""


def get_filename_string(string):
    result = ''
    for char in string:
        if char in INVALID_CHARS:
            result += '_'
        else:
            result += char
    return result.strip()


def get_paths(paths, metadata):
    outpaths = {}
    for path in paths:
        if path == 'template':
            outpaths[path] = paths[path]
        elif path != 'base':
            outpaths[path] = Template(paths['base']).render_unicode(**metadata)
            outpaths[path] += Template(paths[path]).render_unicode(**metadata)
        elif path == 'base':
            outpaths[path] = Template(paths[path]).render_unicode(**metadata)
        outpaths[path] = get_filename_string(outpaths[path])

    return outpaths


def write_nfo(templatefile, metadata, filename):
    """ writes the nfo based on the template file """

    with open(templatefile, 'r') as tf:
        template = tf.read()

    output = Template(template).render_unicode(**metadata)

    with open(filename, 'w') as outfile:
        outfile.write(output)
