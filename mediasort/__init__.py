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

""" initializes mediasort and its plugins """

import sys
import os
from importlib import import_module

from mediasort.enums import PluginType, MediaType
from mediasort import error
# stuff we need from outside
from mediasort.sorting import sort  # noqa: F401


def check_function(module, function):
    """ check if a module contains the functions from functionlist """
    if not hasattr(module, function):
        raise error.InvalidPlugin("Plugin {0} is missing {1}".format(
            module.__name__,
            function))


def load_module(name, config):
    # check if module is already loaded
    modulename = 'mediasort.plugins' + '.' + name
    if modulename in sys.modules:
        return sys.modules[modulename]

    path = '{0}/plugins/{1}.py'.format(
        os.path.dirname(os.path.abspath(__file__)),
        name)

    # check if module exists
    if not os.path.isfile(path):
        raise error.InvalidConfig(
            "The module {0} doesn't exist in the plugin folder".format(name)
        )

    module = import_module(modulename)
    check_function(module, 'init')

    module.init(config)
    return module


def initialize_plugins(config):
    """
    Calls the init function of every plugin
    checks if the plugins has the needed functions
    checks if some configurations are valid
    """

    plugins = {
        PluginType.guess: [],
        PluginType.identificator: {},
        PluginType.metadata: {},
        PluginType.images: {},
    }

    ids = {
        'wanted': {},
        'provided': {}
    }

    for mediatype in MediaType:
        plugins[PluginType.identificator][mediatype.__name__] = []
        plugins[PluginType.metadata][mediatype.__name__] = {}
        plugins[PluginType.images][mediatype.__name__] = {}
        for metadatatype in mediatype.metadataTypes:
            plugins[PluginType.metadata][mediatype.__name__][metadatatype] = []
        for imagetype in mediatype.imageTypes:
            plugins[PluginType.images][mediatype.__name__][imagetype] = []
        ids['wanted'][mediatype.__name__] = []
        ids['provided'][mediatype.__name__] = []

    # initializing and function existance checking
    for plugintype in config['plugins']:
        if plugintype == PluginType.guess:
            for plugin in config['plugins'][plugintype]:
                # load the module
                module = load_module(plugin, config[plugin])
                # check needed functions
                check_function(module, 'get_guess')
                # add module to dict
                plugins[plugintype].append(module)

        elif plugintype == PluginType.identificator:
            for mediatype in config['plugins'][plugintype]:
                for plugin in config['plugins'][plugintype][mediatype]:
                    # load the module
                    module = load_module(plugin, config[plugin])
                    # check needed functions
                    check_function(module, 'get_identificator_list')
                    check_function(module, 'get_identificator')
                    # add module to dict
                    plugins[plugintype][mediatype].append(module)
                    ids['provided'][mediatype].extend(
                        module.get_identificator_list()
                    )

        elif plugintype == PluginType.metadata:
            for mediatype in config['plugins'][plugintype]:
                for metadatatype in config['plugins'][plugintype][mediatype]:
                    for plugin in config['plugins'][plugintype][mediatype][metadatatype]:
                        # load the module
                        module = load_module(plugin, config[plugin])
                        # check needed functions
                        check_function(module, 'get_needed_ids')
                        check_function(module, 'get_metadata')
                        # add module to dict
                        ids['wanted'][mediatype].extend(module.get_needed_ids)
                        plugins[plugintype][mediatype][metadatatype].append(module)

        elif plugintype == PluginType.image:
            for mediatype in config['plugins'][plugintype]:
                for imagetype in config['plugins'][plugintype][mediatype]:
                    for plugin in config['plugins'][plugintype][mediatype][imagetype]:
                        # load the module
                        module = load_module(plugin, config[plugin])
                        # check needed functions
                        check_function(module, 'get_needed_ids')
                        check_function(module, 'get_image')
                        # add module to dict
                        ids['wanted'][mediatype].extend(module.get_needed_ids)
                        plugins[plugintype][mediatype][imagetype].append(module)

    # since the pluginlist is built, we can now do some checks
    for mediatype in MediaType:
        if not ids['wanted'][mediatype.__name__].issubsetof(
               ids['provided'][mediatype.__name__]):
            raise error.InvalidConfig("A plugin needs an id which isn't provided by the identificator providers")

    return {'plugins': plugins, 'ids': ids}
