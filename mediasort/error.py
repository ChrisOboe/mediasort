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


class InvalidConfig(Exception):
    """ Should be raised when configuration is invalid """
    pass


class InvalidPlugin(Exception):
    """ Should be raised when a plugin hasn't the needed functions """
    pass


class InternalError(Exception):
    """ Should be raised when this error should never happen"""
    pass


class NotEnoughData(Exception):
    """ Should be raised when a needet value is missing """
    pass


class InvalidMediaType(Exception):
    """ Should be raised when a mediatype is not supportet """
    pass


class CallbackBreak(Exception):
    """ Should be raised when the callback function should stop something """
    pass
