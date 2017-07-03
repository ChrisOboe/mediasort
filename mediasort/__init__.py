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
        PluginType.guess.name: [],
        PluginType.identificator.name: {},
        PluginType.metadata.name: {},
        PluginType.images.name: {},
    }

    ids = {
        'wanted': {},
        'provided': {}
    }

    for mediatype in MediaType:
        plugins[PluginType.identificator.name][mediatype.name] = []
        plugins[PluginType.metadata.name][mediatype.name] = {}
        plugins[PluginType.images.name][mediatype.name] = {}
        for metadatatype in mediatype.value.metadataTypes.value:
            plugins[PluginType.metadata.name][mediatype.name][metadatatype] = []
        for imagetype in mediatype.value.imageTypes.value:
            plugins[PluginType.images.name][mediatype.name][imagetype] = []
        ids['wanted'][mediatype.name] = []
        ids['provided'][mediatype.name] = []

    # initializing and function existance checking
    for plugintype in config['plugins']:
        if plugintype == PluginType.guess.name:
            for plugin in config['plugins'][plugintype]:
                # load the module
                module = load_module(plugin, config.get(plugin))
                # check needed functions
                check_function(module, 'get_guess')
                # add module to dict
                plugins[plugintype].append(module)

        elif plugintype == PluginType.identificator.name:
            for mediatype in config['plugins'][plugintype]:
                for plugin in config['plugins'][plugintype][mediatype]:
                    # load the module
                    module = load_module(plugin, config.get(plugin))
                    # check needed functions
                    check_function(module, 'get_identificator_list')
                    check_function(module, 'get_identificator')
                    # add module to dict
                    plugins[plugintype][mediatype].append(module)
                    ids['provided'][mediatype] = list(set(
                        ids['provided'][mediatype] +
                        module.get_identificator_list(mediatype)
                    ))

        elif plugintype == PluginType.metadata.name:
            for mediatype in config['plugins'][plugintype]:
                # check if we have a plugin configured for every metadatatpe
                for metadatatype in MediaType[mediatype].value.metadataTypes.value:
                    if metadatatype not in config['plugins'][plugintype][mediatype]:
                        raise error.InvalidConfig("There is no plugin configured for {1}/{0}".format(metadatatype, mediatype))
                # load plugins
                for metadatatype in config['plugins'][plugintype][mediatype]:
                    for plugin in config['plugins'][plugintype][mediatype][metadatatype]:
                        # load the module
                        module = load_module(plugin, config.get(plugin))
                        # check needed functions
                        check_function(module, 'get_needed_ids')
                        check_function(module, 'get_metadata')
                        # add module to dict
                        ids['wanted'][mediatype] = list(set(
                            ids['wanted'][mediatype] +
                            module.get_needed_ids(mediatype)
                        ))
                        plugins[plugintype][mediatype][metadatatype].append(module)

        elif plugintype == PluginType.images.name:
            for mediatype in config['plugins'][plugintype]:
                # check if we have a plugin configured for every metadatatpe
                for imagetype in MediaType[mediatype].value.imageTypes.value:
                    if imagetype not in config['plugins'][plugintype][mediatype]:
                        raise error.InvalidConfig("There is no plugin configured for {1}/{0}".format(metadatatype, imagetype))
                for imagetype in config['plugins'][plugintype][mediatype]:
                    for plugin in config['plugins'][plugintype][mediatype][imagetype]:
                        # load the module
                        module = load_module(plugin, config.get(plugin))
                        # check needed functions
                        check_function(module, 'get_needed_ids')
                        check_function(module, 'get_image')
                        # add module to dict
                        ids['wanted'][mediatype] = list(set(
                            ids['wanted'][mediatype] +
                            module.get_needed_ids(mediatype)
                        ))
                        plugins[plugintype][mediatype][imagetype].append(module)

    # if we have depending mediatypes (eg season and tvshow depends on episode)
    # we use the ids from the parents
    for mediatype in MediaType:
        if getattr(mediatype.value, 'get_successors', None) is not None:
            for successor in mediatype.value.get_successors():
                ids['provided'][successor.name] = ids['provided'][mediatype.name]

    # since the pluginlist is built, we can now do some checks
    for mediatype in MediaType:
        for mid in ids['wanted'][mediatype.name]:
            if mid not in ids['provided'][mediatype.name]:
                raise error.InvalidConfig("A plugin needs a {0} id which isn't provided by the identificator providers".format(mid))

    return {'plugins': plugins, 'ids': ids}
